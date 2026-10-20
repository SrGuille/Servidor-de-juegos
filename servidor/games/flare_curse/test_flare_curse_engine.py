import time
import unittest
import os
from collections import deque
from unittest.mock import MagicMock, patch

import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "servidor_juegos.settings")
django.setup()

from servidor.games.flare_curse.flare_curse_engine import FlareCurseEngine
from servidor.games.flare_curse.flare_curse_engine import FlareCurseGhostState
from servidor.games.flare_curse.flare_curse_engine import FlareCursePlayerState
from servidor.games.flare_curse.flare_curse_engine import FLARE_CURSE_GAME_ID
from servidor.games.flare_curse.flare_curse_engine import get_player_group_name
from servidor.games.flare_curse.flare_curse_engine import sanitize_group_name


class TestFlareCurseEngine(unittest.TestCase):
    def setUp(self):
        self.engine = FlareCurseEngine()
        self.broadcast_events = []
        self.private_events = []

        # Keep tests fully in-memory and deterministic regarding outbound events.
        self.engine._broadcast_locked = lambda payload: self.broadcast_events.append(payload)
        self.engine._send_to_player_locked = lambda player_name, payload: self.private_events.append((player_name, payload))

    def _initialize_game(self, players):
        with patch("servidor.games.flare_curse.flare_curse_engine.main_views.main_controller_.set_can_players_join"), patch(
            "servidor.games.flare_curse.flare_curse_engine.main_views.main_controller_.set_can_players_interact"
        ):
            self.engine._initialize_locked(players)

    def _alive_team_groups(self):
        groups = {}
        for name, player in self.engine._players.items():
            if player.alive and player.team in {"circle", "square"}:
                groups.setdefault(player.team, []).append(name)
        return groups

    def _set_alive_count(self, alive_count):
        self.engine._players = {
            f"P{i}": FlareCursePlayerState(name=f"P{i}", team="circle" if i % 2 == 0 else "square", alive=(i < alive_count))
            for i in range(12)
        }

    def test_ensure_started_returns_false_if_game_not_selected(self):
        with patch(
            "servidor.games.flare_curse.flare_curse_engine.main_views.main_controller_.get_ready_to_join_game",
            return_value=3,
        ):
            self.assertFalse(self.engine.ensure_started())

    def test_ensure_started_returns_false_if_not_enough_players(self):
        with patch(
            "servidor.games.flare_curse.flare_curse_engine.main_views.main_controller_.get_ready_to_join_game",
            return_value=FLARE_CURSE_GAME_ID,
        ), patch("servidor.games.flare_curse.flare_curse_engine.q.get_logged_players_names", return_value=["A"]):
            self.assertFalse(self.engine.ensure_started())

    def test_ensure_started_starts_thread_once(self):
        fake_thread = MagicMock()
        with patch(
            "servidor.games.flare_curse.flare_curse_engine.main_views.main_controller_.get_ready_to_join_game",
            return_value=FLARE_CURSE_GAME_ID,
        ), patch(
            "servidor.games.flare_curse.flare_curse_engine.q.get_logged_players_names",
            return_value=["A", "B", "C", "D"],
        ), patch(
            "servidor.games.flare_curse.flare_curse_engine.threading.Thread",
            return_value=fake_thread,
        ), patch.object(
            self.engine,
            "_initialize_locked",
        ) as init_mock:
            self.assertTrue(self.engine.ensure_started())
            self.assertTrue(self.engine._running)
            self.assertIs(self.engine._thread, fake_thread)
            init_mock.assert_called_once()
            fake_thread.start.assert_called_once()

            # Second call should short-circuit while already running.
            self.assertTrue(self.engine.ensure_started())
            init_mock.assert_called_once()

    def test_snapshot_returns_error_for_unknown_player(self):
        self._initialize_game(["A", "B", "C", "D"])
        snapshot = self.engine.get_snapshot_for_player("Z")
        self.assertEqual("Error", snapshot["type"])

    def test_snapshot_hides_alive_teams_and_shows_ghosts(self):
        self._initialize_game(["A", "B", "C", "D"])

        now = time.monotonic()
        ghost_name = next(iter(self.engine._players.keys()))
        self.engine._make_ghost_locked(ghost_name, now)

        viewer = next(name for name, p in self.engine._players.items() if p.alive)
        snapshot = self.engine.get_snapshot_for_player(viewer)
        self.assertEqual("GameSnapshot", snapshot["type"])

        rows = {p["name"]: p for p in snapshot["players"]}
        self.assertEqual(self.engine._players[viewer].team, rows[viewer]["team_symbol"])

        for name, row in rows.items():
            if name == viewer:
                continue
            if self.engine._players[name].alive:
                self.assertIsNone(row["team_symbol"])
            else:
                self.assertEqual(self.engine._players[name].team, row["team_symbol"])

    def test_snapshot_for_ghost_role_contains_ghost_fields(self):
        self._initialize_game(["A", "B", "C", "D"])
        now = time.monotonic()

        ghost_name = next(iter(self.engine._players.keys()))
        self.engine._players[ghost_name].last_face_color = "blue"
        self.engine._make_ghost_locked(ghost_name, now)
        self.engine._ghosts[ghost_name].points = 3
        self.engine._ghosts[ghost_name].cooldown_expires_at = now + 5

        snapshot = self.engine.get_snapshot_for_player(ghost_name)
        self.assertEqual("ghost", snapshot["you"]["role"])
        self.assertEqual("blue", snapshot["you"]["ghost_color"])
        self.assertEqual(3, snapshot["you"]["ghost_points"])
        self.assertGreater(snapshot["you"]["ghost_cooldown_seconds_left"], 0)

    def test_snapshot_includes_timing_configuration(self):
        self._initialize_game(["A", "B", "C", "D"])
        viewer = next(name for name, p in self.engine._players.items() if p.alive)

        snapshot = self.engine.get_snapshot_for_player(viewer)

        self.assertIn("timings", snapshot)
        self.assertEqual(self.engine.HOLD_COLOR_SECONDS, snapshot["timings"]["hold_color_seconds"])
        self.assertEqual(self.engine.GHOST_COOLDOWN_SECONDS, snapshot["timings"]["ghost_cooldown_seconds"])

    def test_initial_ghost_has_dedicated_symbol(self):
        self._initialize_game(["A", "B", "C", "D", "E"])

        ghost_symbol_players = [p.name for p in self.engine._players.values() if p.team == "ghost"]
        self.assertEqual(1, len(ghost_symbol_players))
        self.assertEqual(set(ghost_symbol_players), set(self.engine._ghosts.keys()))

        initial_ghost_name = ghost_symbol_players[0]
        self.assertFalse(self.engine._players[initial_ghost_name].alive)

    def test_claim_flare_is_exclusive(self):
        self._initialize_game(["A", "B", "C", "D"])

        self.engine._offered_color = "red"

        accepted_a = self.engine.claim_flare("A", "red")
        accepted_b = self.engine.claim_flare("B", "red")

        self.assertTrue(accepted_a)
        self.assertFalse(accepted_b)
        self.assertEqual("red", self.engine._players["A"].hand_color)
        self.assertIsNone(self.engine._offered_color)
        self.assertTrue(any(event["type"] == "DestelloNoDisponible" for event in self.broadcast_events))

    def test_claim_flare_rejection_cases(self):
        self._initialize_game(["A", "B", "C", "D"])
        self.engine._offered_color = "red"

        self.engine._game_over = True
        self.assertFalse(self.engine.claim_flare("A", "red"))
        self.engine._game_over = False

        self.assertFalse(self.engine.claim_flare("unknown", "red"))

        self.engine._players["A"].alive = False
        self.assertFalse(self.engine.claim_flare("A", "red"))
        self.engine._players["A"].alive = True

        self.engine._players["A"].hand_color = "green"
        self.assertFalse(self.engine.claim_flare("A", "red"))
        self.engine._players["A"].hand_color = None

        self.assertFalse(self.engine.claim_flare("A", "blue"))

    def test_launch_flare_rejection_cases(self):
        self._initialize_game(["A", "B", "C", "D"])
        self.assertFalse(self.engine.launch_flare("unknown"))

        self.engine._players["A"].alive = False
        self.assertFalse(self.engine.launch_flare("A"))
        self.engine._players["A"].alive = True

        self.assertFalse(self.engine.launch_flare("A"))

        self.engine._game_over = True
        self.assertFalse(self.engine.launch_flare("A"))

    def test_launch_flare_success_updates_state_and_notifies(self):
        self._initialize_game(["A", "B", "C", "D"])
        groups = self._alive_team_groups()
        team_names = list(groups.keys())

        source = groups[team_names[0]][0]
        enemy = groups[team_names[1]][0]
        self.engine._players[source].hand_color = "blue"

        with patch("servidor.games.flare_curse.flare_curse_engine.random.choice", return_value=enemy):
            accepted = self.engine.launch_flare(source)

        self.assertTrue(accepted)
        self.assertIsNone(self.engine._players[source].hand_color)
        self.assertEqual(1, len(self.engine._used_queue))
        self.assertEqual("blue", self.engine._used_queue[0][2])

        notified_names = [name for name, _ in self.private_events]
        self.assertIn(source, notified_names)
        self.assertIn(enemy, notified_names)
        self.assertEqual(1, len(self.engine._recent_flare_timestamps))

    def test_launch_flare_uses_configured_used_cooldown_random(self):
        self._initialize_game(["A", "B", "C", "D"])
        groups = self._alive_team_groups()
        team_names = list(groups.keys())

        source = groups[team_names[0]][0]
        enemy = groups[team_names[1]][0]
        self.engine._players[source].hand_color = "blue"

        with patch("servidor.games.flare_curse.flare_curse_engine.time.monotonic", return_value=100.0), patch(
            "servidor.games.flare_curse.flare_curse_engine.random.uniform", return_value=9.5
        ), patch("servidor.games.flare_curse.flare_curse_engine.random.choice", return_value=enemy):
            accepted = self.engine.launch_flare(source)

        self.assertTrue(accepted)
        self.assertEqual(1, len(self.engine._used_queue))
        ready_at, _, color = self.engine._used_queue[0]
        self.assertEqual("blue", color)
        self.assertEqual(109.5, ready_at)

    def test_launch_flare_overwrites_target_existing_face_color(self):
        self._initialize_game(["A", "B", "C", "D"])
        groups = self._alive_team_groups()
        team_names = list(groups.keys())

        source = groups[team_names[0]][0]
        target = groups[team_names[1]][0]

        now = 250.0
        old_face_expires_at = now + 8.0
        self.engine._players[source].hand_color = "orange"
        self.engine._players[target].face_color = "green"
        self.engine._players[target].face_expires_at = old_face_expires_at

        with patch("servidor.games.flare_curse.flare_curse_engine.time.monotonic", return_value=now), patch(
            "servidor.games.flare_curse.flare_curse_engine.random.uniform", return_value=8.5
        ), patch("servidor.games.flare_curse.flare_curse_engine.random.choice", return_value=target):
            accepted = self.engine.launch_flare(source)

        self.assertTrue(accepted)
        self.assertEqual("orange", self.engine._players[target].face_color)
        self.assertEqual(now + self.engine.FLASH_SECONDS, self.engine._players[target].face_expires_at)
        self.assertLess(self.engine._players[target].face_expires_at, old_face_expires_at)
        self.assertTrue(
            any(
                name == target and payload["type"] == "TeHanLanzadoDestello" and payload["color"] == "orange"
                for name, payload in self.private_events
            )
        )

    def test_launch_ghost_flare_rejection_cases(self):
        self._initialize_game(["A", "B", "C", "D"])
        self.assertEqual((False, 0, 0.0), self.engine.launch_ghost_flare("A"))

        now = time.monotonic()
        self.engine._make_ghost_locked("A", now)
        self.engine._ghosts["A"].cooldown_expires_at = now + 3.0

        in_time, points, left = self.engine.launch_ghost_flare("A")
        self.assertFalse(in_time)
        self.assertEqual(0, points)
        self.assertGreater(left, 0)

    def test_launch_ghost_flare_scores_when_in_time(self):
        self._initialize_game(["A", "B", "C", "D"])
        now = time.monotonic()

        self.engine._players["A"].last_face_color = "red"
        self.engine._make_ghost_locked("A", now)
        self.engine._ghosts["A"].cooldown_expires_at = 0.0

        alive_names = [name for name, p in self.engine._players.items() if p.alive]
        active_name = alive_names[0]
        target_name = alive_names[1]

        self.engine._players[active_name].face_color = "red"
        self.engine._players[active_name].face_expires_at = now + 1.0

        with patch("servidor.games.flare_curse.flare_curse_engine.random.choice", return_value=target_name):
            in_time, points, cooldown = self.engine.launch_ghost_flare("A")

        self.assertTrue(in_time)
        self.assertEqual(1, points)
        self.assertEqual(self.engine.GHOST_COOLDOWN_SECONDS, cooldown)
        self.assertTrue(
            any(name == target_name and payload["type"] == "TeHanLanzadoDestello" for name, payload in self.private_events)
        )

    def test_launch_ghost_flare_no_eligible_target(self):
        self._initialize_game(["A", "B", "C", "D"])
        now = time.monotonic()

        self.engine._players["A"].last_face_color = "green"
        self.engine._make_ghost_locked("A", now)

        for player in self.engine._players.values():
            if player.alive:
                player.face_color = "green"
                player.face_expires_at = now + 1.0

        in_time, points, cooldown = self.engine.launch_ghost_flare("A")
        self.assertFalse(in_time)
        self.assertEqual(0, points)
        self.assertEqual(self.engine.GHOST_COOLDOWN_SECONDS, cooldown)

    def test_launch_ghost_flare_same_color_compete_single_target(self):
        self._initialize_game(["A", "B", "C", "D"])
        now = time.monotonic()

        self.engine._players["A"].last_face_color = "red"
        self.engine._players["B"].last_face_color = "red"
        self.engine._make_ghost_locked("A", now)
        self.engine._make_ghost_locked("B", now)
        self.engine._ghosts["A"].cooldown_expires_at = 0.0
        self.engine._ghosts["B"].cooldown_expires_at = 0.0

        alive_names = [name for name, p in self.engine._players.items() if p.alive]
        active_name = alive_names[0]
        only_target = alive_names[1]

        self.engine._players[active_name].face_color = "red"
        self.engine._players[active_name].face_expires_at = now + 1.0

        with patch("servidor.games.flare_curse.flare_curse_engine.random.choice", return_value=only_target):
            first_in_time, first_points, _ = self.engine.launch_ghost_flare("A")
            second_in_time, second_points, _ = self.engine.launch_ghost_flare("B")

        self.assertTrue(first_in_time)
        self.assertEqual(1, first_points)
        self.assertFalse(second_in_time)
        self.assertEqual(0, second_points)

        target_hits = [
            name
            for name, payload in self.private_events
            if payload["type"] == "TeHanLanzadoDestello" and name == only_target
        ]
        self.assertEqual(1, len(target_hits))

    def test_launch_ghost_flare_avoids_recently_expired_targets(self):
        self._initialize_game(["A", "B", "C", "D"])
        now = time.monotonic()

        self.engine._players["A"].last_face_color = "red"
        self.engine._make_ghost_locked("A", now)
        self.engine._ghosts["A"].cooldown_expires_at = 0.0

        alive_names = [name for name, p in self.engine._players.items() if p.alive]
        active_name = alive_names[0]
        recently_off_name = alive_names[1]
        fallback_target = alive_names[2]

        self.engine._players[active_name].face_color = "red"
        self.engine._players[active_name].face_expires_at = now + 1.0

        self.engine._players[recently_off_name].face_color = None
        self.engine._players[recently_off_name].last_face_color = "red"
        self.engine._players[recently_off_name].last_face_expires_at = now - 0.2

        with patch(
            "servidor.games.flare_curse.flare_curse_engine.random.choice",
            return_value=fallback_target,
        ) as choice_mock:
            in_time, points, cooldown = self.engine.launch_ghost_flare("A")

        self.assertTrue(in_time)
        self.assertEqual(1, points)
        self.assertEqual(self.engine.GHOST_COOLDOWN_SECONDS, cooldown)
        choices = choice_mock.call_args[0][0]
        self.assertIn(fallback_target, choices)
        self.assertNotIn(recently_off_name, choices)

    def test_launch_ghost_flare_grace_window_without_alternative_has_no_effect(self):
        self._initialize_game(["A", "B", "C", "D"])
        now = time.monotonic()

        self.engine._players["A"].last_face_color = "green"
        self.engine._make_ghost_locked("A", now)
        self.engine._ghosts["A"].cooldown_expires_at = 0.0

        for name, player in self.engine._players.items():
            if player.alive:
                player.face_color = None
                player.last_face_color = "green"
                player.last_face_expires_at = now - 0.2

        in_time, points, cooldown = self.engine.launch_ghost_flare("A")

        self.assertFalse(in_time)
        self.assertEqual(0, points)
        self.assertEqual(self.engine.GHOST_COOLDOWN_SECONDS, cooldown)

    def test_launch_ghost_flare_grace_boundary_still_counts_as_in_time(self):
        self._initialize_game(["A", "B", "C", "D"])
        now = time.monotonic()

        self.engine._players["A"].last_face_color = "blue"
        self.engine._make_ghost_locked("A", now)
        self.engine._ghosts["A"].cooldown_expires_at = 0.0

        alive_names = [name for name, p in self.engine._players.items() if p.alive]
        recently_off_name = alive_names[0]
        target_name = alive_names[1]

        self.engine._players[recently_off_name].face_color = None
        self.engine._players[recently_off_name].last_face_color = "blue"
        self.engine._players[recently_off_name].last_face_expires_at = now - self.engine.GHOST_POST_FACE_GRACE_SECONDS

        with patch("servidor.games.flare_curse.flare_curse_engine.random.choice", return_value=target_name):
            in_time, points, cooldown = self.engine.launch_ghost_flare("A")

        self.assertTrue(in_time)
        self.assertEqual(1, points)
        self.assertEqual(self.engine.GHOST_COOLDOWN_SECONDS, cooldown)
        self.assertTrue(
            any(name == target_name and payload["type"] == "TeHanLanzadoDestello" for name, payload in self.private_events)
        )

    def test_launch_ghost_flare_after_grace_window_is_not_in_time(self):
        self._initialize_game(["A", "B", "C", "D"])
        now = time.monotonic()

        self.engine._players["A"].last_face_color = "purple"
        self.engine._make_ghost_locked("A", now)
        self.engine._ghosts["A"].cooldown_expires_at = 0.0

        alive_names = [name for name, p in self.engine._players.items() if p.alive]
        recently_off_name = alive_names[0]

        self.engine._players[recently_off_name].face_color = None
        self.engine._players[recently_off_name].last_face_color = "purple"
        self.engine._players[recently_off_name].last_face_expires_at = (
            now - self.engine.GHOST_POST_FACE_GRACE_SECONDS - 0.001
        )

        in_time, points, cooldown = self.engine.launch_ghost_flare("A")

        self.assertFalse(in_time)
        self.assertEqual(0, points)
        self.assertEqual(self.engine.GHOST_COOLDOWN_SECONDS, cooldown)
        self.assertEqual([], [payload for _, payload in self.private_events if payload["type"] == "TeHanLanzadoDestello"])

    def test_timeout_prevents_late_launch(self):
        self._initialize_game(["A", "B", "C", "D"])

        now = time.monotonic()
        self.engine._players["A"].hand_color = "blue"
        self.engine._players["A"].hand_expires_at = now - 0.01

        self.engine._process_hand_timeouts_locked(now)
        accepted_launch = self.engine.launch_flare("A")

        self.assertFalse(accepted_launch)
        self.assertIsNone(self.engine._players["A"].hand_color)
        self.assertTrue(any(entry[2] == "blue" for entry in self.engine._timeout_queue))
        self.assertTrue(
            any(name == "A" and payload["type"] == "TimeoutDestello" for name, payload in self.private_events)
        )

    def test_offered_color_persists_until_claim(self):
        self._initialize_game(["A", "B", "C", "D"])
        now = time.monotonic()

        self.engine._offered_color = "purple"
        self.engine._timeout_queue = [(now, 1, "red")]
        self.engine._release_enabled_at = 0.0
        self.engine._last_release_at = 0.0
        self.engine._next_gap_seconds = 0.0

        self.engine._try_release_color_locked(now + 999.0)

        self.assertEqual("purple", self.engine._offered_color)
        self.assertEqual("red", self.engine._timeout_queue[0][2])
        self.assertFalse(any(e["type"] == "DestelloNoDisponible" for e in self.broadcast_events))

    def test_try_release_color_prioritizes_timeout_queue(self):
        self._initialize_game(["A", "B", "C", "D"])
        now = time.monotonic()

        self.engine._release_enabled_at = 0.0
        self.engine._last_release_at = 0.0
        self.engine._next_gap_seconds = 0.0
        self.engine._timeout_queue = [(now - 1.0, 1, "orange")]
        self.engine._used_queue = [(now - 1.0, 2, "blue")]

        self.engine._try_release_color_locked(now)
        self.assertEqual("orange", self.engine._offered_color)
        self.assertEqual(0, len(self.engine._timeout_queue))
        self.assertEqual(1, len(self.engine._used_queue))

    def test_try_release_color_uses_used_queue_when_ready(self):
        self._initialize_game(["A", "B", "C", "D"])
        now = time.monotonic()

        self.engine._release_enabled_at = 0.0
        self.engine._last_release_at = 0.0
        self.engine._next_gap_seconds = 0.0
        self.engine._timeout_queue = []
        self.engine._used_queue = [(now - 1.0, 1, "green")]

        self.engine._try_release_color_locked(now)
        self.assertEqual("green", self.engine._offered_color)
        self.assertEqual(0, len(self.engine._used_queue))

    def test_try_release_color_recomputes_random_release_gap(self):
        self._initialize_game(["A", "B", "C", "D"])
        now = time.monotonic()

        self.engine._release_enabled_at = 0.0
        self.engine._last_release_at = 0.0
        self.engine._next_gap_seconds = 0.0
        self.engine._timeout_queue = [(now - 1.0, 1, "orange")]

        with patch("servidor.games.flare_curse.flare_curse_engine.random.uniform", return_value=1.7):
            self.engine._try_release_color_locked(now)

        self.assertEqual("orange", self.engine._offered_color)
        self.assertEqual(1.7, self.engine._next_gap_seconds)
        self.assertEqual(now, self.engine._last_release_at)

    def test_used_queue_prioritizes_earliest_ready_even_if_inserted_later(self):
        self._initialize_game(["A", "B", "C", "D"])
        now = time.monotonic()

        self.engine._release_enabled_at = 0.0
        self.engine._last_release_at = 0.0
        self.engine._next_gap_seconds = 0.0
        self.engine._timeout_queue = []
        self.engine._used_queue = []
        self.engine._release_order = 0

        self.engine._enqueue_color_ready_at_locked(self.engine._used_queue, "late", now + 5.0)
        self.engine._enqueue_color_ready_at_locked(self.engine._used_queue, "early", now + 1.0)

        # At now+1.5 only "early" should be eligible and therefore released first.
        self.engine._try_release_color_locked(now + 1.5)
        self.assertEqual("early", self.engine._offered_color)
        self.assertEqual("late", self.engine._used_queue[0][2])

    def test_used_queue_tie_breaks_by_insertion_order(self):
        self._initialize_game(["A", "B", "C", "D"])
        now = time.monotonic()

        self.engine._release_enabled_at = 0.0
        self.engine._last_release_at = 0.0
        self.engine._next_gap_seconds = 0.0
        self.engine._timeout_queue = []
        self.engine._used_queue = []
        self.engine._release_order = 0

        self.engine._enqueue_color_ready_at_locked(self.engine._used_queue, "first", now + 1.0)
        self.engine._enqueue_color_ready_at_locked(self.engine._used_queue, "second", now + 1.0)

        self.engine._try_release_color_locked(now + 2.0)
        self.assertEqual("first", self.engine._offered_color)
        self.assertEqual("second", self.engine._used_queue[0][2])

    def test_timeout_queue_tie_breaks_by_insertion_order(self):
        self._initialize_game(["A", "B", "C", "D"])
        now = time.monotonic()

        self.engine._release_enabled_at = 0.0
        self.engine._last_release_at = 0.0
        self.engine._next_gap_seconds = 0.0
        self.engine._timeout_queue = []
        self.engine._used_queue = []
        self.engine._release_order = 0

        self.engine._enqueue_color_ready_at_locked(self.engine._timeout_queue, "first", now - 1.0)
        self.engine._enqueue_color_ready_at_locked(self.engine._timeout_queue, "second", now - 1.0)

        self.engine._try_release_color_locked(now)
        self.assertEqual("first", self.engine._offered_color)
        self.assertEqual("second", self.engine._timeout_queue[0][2])

    def test_claim_flare_wrong_color_keeps_offer_unchanged(self):
        self._initialize_game(["A", "B", "C", "D"])
        self.engine._offered_color = "red"

        accepted = self.engine.claim_flare("A", "blue")

        self.assertFalse(accepted)
        self.assertEqual("red", self.engine._offered_color)
        self.assertIsNone(self.engine._players["A"].hand_color)
        self.assertEqual([], [e for e in self.broadcast_events if e["type"] == "DestelloNoDisponible"])

    def test_try_release_color_respects_gap_and_concurrency_limit(self):
        self._initialize_game(["A", "B", "C", "D"])
        now = time.monotonic()

        self.engine._timeout_queue = [(now - 1.0, 1, "red")]
        self.engine._release_enabled_at = 0.0

        # Gap not elapsed.
        self.engine._last_release_at = now
        self.engine._next_gap_seconds = 1.0
        self.engine._try_release_color_locked(now)
        self.assertIsNone(self.engine._offered_color)

        # Gap elapsed but no concurrency room (4 alive -> limit 2).
        self.engine._last_release_at = 0.0
        self.engine._next_gap_seconds = 0.0
        alive_names = [name for name, p in self.engine._players.items() if p.alive]
        self.engine._players[alive_names[0]].hand_color = "red"
        self.engine._players[alive_names[1]].hand_color = "blue"
        self.engine._try_release_color_locked(now)
        self.assertIsNone(self.engine._offered_color)

    def test_close_offer_broadcasts_no_disponible(self):
        self._initialize_game(["A", "B", "C", "D"])

        self.engine._offered_color = "blue"
        self.engine._close_offer_locked()

        self.assertIsNone(self.engine._offered_color)
        self.assertTrue(any(e["type"] == "DestelloNoDisponible" and e["color"] == "blue" for e in self.broadcast_events))

    def test_expire_faces_clears_expired_only(self):
        self._initialize_game(["A", "B", "C", "D"])
        now = time.monotonic()
        names = list(self.engine._players.keys())

        self.engine._players[names[0]].face_color = "red"
        self.engine._players[names[0]].face_expires_at = now - 0.001
        self.engine._players[names[1]].face_color = "blue"
        self.engine._players[names[1]].face_expires_at = now + 5.0

        self.engine._expire_faces_locked(now)
        self.assertIsNone(self.engine._players[names[0]].face_color)
        self.assertEqual("blue", self.engine._players[names[1]].face_color)

    def test_make_ghost_uses_last_face_color_when_available(self):
        self._initialize_game(["A", "B", "C", "D"])
        now = time.monotonic()

        self.engine._players["A"].last_face_color = "green"
        color = self.engine._make_ghost_locked("A", now)
        self.assertEqual("green", color)
        self.assertIn("A", self.engine._ghosts)

    def test_make_ghost_converts_hand_to_timeout_and_notifies(self):
        self._initialize_game(["A", "B", "C", "D"])
        now = time.monotonic()

        self.engine._players["A"].hand_color = "orange"
        self.engine._players["A"].hand_expires_at = now + 2.0
        self.engine._make_ghost_locked("A", now)

        self.assertTrue(any(entry[2] == "orange" for entry in self.engine._timeout_queue))
        self.assertTrue(any(name == "A" and p["type"] == "TimeoutDestello" for name, p in self.private_events))

    def test_make_ghost_when_already_ghost_returns_same_color(self):
        self._initialize_game(["A", "B", "C", "D"])
        now = time.monotonic()

        first = self.engine._make_ghost_locked("A", now)
        second = self.engine._make_ghost_locked("A", now + 1.0)
        self.assertEqual(first, second)

    def test_pick_least_used_ghost_color(self):
        self.engine._active_colors = ["red", "green", "blue"]
        self.engine._ghosts = {
            "g1": FlareCurseGhostState(color="red"),
            "g2": FlareCurseGhostState(color="red"),
            "g3": FlareCurseGhostState(color="green"),
        }

        with patch("servidor.games.flare_curse.flare_curse_engine.random.choice", return_value="blue") as choice_mock:
            chosen = self.engine._pick_least_used_ghost_color_locked()

        self.assertEqual("blue", chosen)
        # Candidates must be the least-used colors: only blue here.
        self.assertEqual(["blue"], choice_mock.call_args[0][0])

    def test_pick_least_used_ghost_color_defaults_when_no_active(self):
        self.engine._active_colors = []
        self.assertEqual("red", self.engine._pick_least_used_ghost_color_locked())

    def test_curse_reflects_on_ally_and_hits_enemy(self):
        self._initialize_game(["A", "B", "C", "D", "E", "F"])

        groups = self._alive_team_groups()
        team_names = list(groups.keys())
        self.assertEqual(2, len(team_names))

        ally_team = team_names[0]
        enemy_team = team_names[1]
        self.assertGreaterEqual(len(groups[ally_team]), 2)
        self.assertGreaterEqual(len(groups[enemy_team]), 1)

        origin = groups[ally_team][0]
        ally_target = groups[ally_team][1]

        accepted, victim_is_enemy, cursed_player = self.engine.cast_curse(origin, ally_target)
        self.assertTrue(accepted)
        self.assertFalse(victim_is_enemy)
        self.assertEqual(origin, cursed_player)
        self.assertIn(origin, self.engine._ghosts)

        updated_groups = self._alive_team_groups()
        attacker = updated_groups[ally_team][0]
        enemy_target = updated_groups[enemy_team][0]

        accepted2, victim_is_enemy2, cursed_player2 = self.engine.cast_curse(attacker, enemy_target)
        self.assertTrue(accepted2)
        self.assertTrue(victim_is_enemy2)
        self.assertEqual(enemy_target, cursed_player2)
        self.assertIn(enemy_target, self.engine._ghosts)

        self.assertEqual(2, len(self.engine._curse_history))
        first = self.engine._curse_history[0]
        second = self.engine._curse_history[1]
        self.assertEqual(origin, first["origin"])
        self.assertEqual(ally_target, first["target"])
        self.assertEqual(origin, first["cursed_player"])
        self.assertFalse(first["victim_is_enemy"])
        self.assertEqual("self_rebound", first["result"])
        self.assertEqual(attacker, second["origin"])
        self.assertEqual(enemy_target, second["target"])
        self.assertEqual(enemy_target, second["cursed_player"])
        self.assertTrue(second["victim_is_enemy"])
        self.assertEqual("enemy_hit", second["result"])

    def test_cast_curse_rejects_target_already_cursed_by_previous_action(self):
        self._initialize_game(["A", "B", "C", "D", "E", "F"])

        groups = self._alive_team_groups()
        team_names = list(groups.keys())
        self.assertGreaterEqual(len(groups[team_names[0]]), 2)
        self.assertGreaterEqual(len(groups[team_names[1]]), 1)

        first_attacker = groups[team_names[0]][0]
        second_attacker = groups[team_names[0]][1]
        target = groups[team_names[1]][0]

        accepted_first, victim_is_enemy_first, cursed_player_first = self.engine.cast_curse(first_attacker, target)
        self.assertTrue(accepted_first)
        self.assertTrue(victim_is_enemy_first)
        self.assertEqual(target, cursed_player_first)
        self.assertFalse(self.engine._players[target].alive)

        accepted_second, victim_is_enemy_second, cursed_player_second = self.engine.cast_curse(second_attacker, target)
        self.assertEqual((False, False, None), (accepted_second, victim_is_enemy_second, cursed_player_second))
        self.assertEqual(1, len(self.engine._curse_history))

    def test_action_chain_claim_launch_and_curse_keeps_consistent_state(self):
        self._initialize_game(["A", "B", "C", "D", "E", "F"])
        groups = self._alive_team_groups()
        team_names = list(groups.keys())

        source = groups[team_names[0]][0]
        teammate = groups[team_names[0]][1]
        target = groups[team_names[1]][0]

        self.engine._offered_color = "purple"
        self.assertTrue(self.engine.claim_flare(source, "purple"))
        self.assertEqual("purple", self.engine._players[source].hand_color)

        with patch("servidor.games.flare_curse.flare_curse_engine.random.choice", return_value=target):
            self.assertTrue(self.engine.launch_flare(source))

        accepted, victim_is_enemy, cursed_player = self.engine.cast_curse(teammate, target)
        self.assertTrue(accepted)
        self.assertTrue(victim_is_enemy)
        self.assertEqual(target, cursed_player)

        snapshot = self.engine.get_snapshot_for_player(teammate)
        rows = {row["name"]: row for row in snapshot["players"]}
        self.assertEqual("ghost", rows[target]["status"])
        self.assertEqual(1, len(self.engine._curse_history))
        self.assertEqual(target, self.engine._curse_history[0]["target"])
        self.assertEqual(target, self.engine._curse_history[0]["cursed_player"])

    def test_active_game_always_has_enemy_candidate_for_alive_players(self):
        self._initialize_game(["A", "B", "C", "D", "E", "F"])

        # Progress with legal curse actions and assert enemy availability while game is active.
        while not self.engine._game_over:
            alive_players = [player for player in self.engine._players.values() if player.alive]
            alive_teams = {player.team for player in alive_players}
            self.assertGreater(len(alive_teams), 1)

            for source in alive_players:
                enemy_candidates = [
                    player.name
                    for player in self.engine._players.values()
                    if player.alive and player.team != source.team
                ]
                self.assertGreater(len(enemy_candidates), 0)

            origin_name = alive_players[0].name
            target_name = next(player.name for player in alive_players if player.team != alive_players[0].team)
            accepted, victim_is_enemy, cursed_player = self.engine.cast_curse(origin_name, target_name)
            self.assertTrue(accepted)
            self.assertTrue(victim_is_enemy)
            self.assertEqual(target_name, cursed_player)

    def test_cast_curse_rejection_cases(self):
        self._initialize_game(["A", "B", "C", "D"])

        self.assertEqual((False, False, None), self.engine.cast_curse("X", "B"))
        self.assertEqual((False, False, None), self.engine.cast_curse("A", "Y"))
        self.assertEqual((False, False, None), self.engine.cast_curse("A", "A"))

        self.engine._players["A"].alive = False
        self.assertEqual((False, False, None), self.engine.cast_curse("A", "B"))
        self.engine._players["A"].alive = True

        self.engine._players["B"].alive = False
        self.assertEqual((False, False, None), self.engine.cast_curse("A", "B"))

    def test_cast_curse_can_trigger_finish(self):
        self._initialize_game(["A", "B", "C", "D"])
        now = time.monotonic()

        groups = self._alive_team_groups()
        team_a, team_b = list(groups.keys())
        attacker = groups[team_a][0]
        victim = groups[team_b][0]

        # Leave only attacker + victim alive.
        for name, player in self.engine._players.items():
            if name not in {attacker, victim} and player.alive:
                self.engine._make_ghost_locked(name, now)

        accepted, victim_is_enemy, cursed_player = self.engine.cast_curse(attacker, victim)
        self.assertTrue(accepted)
        self.assertTrue(victim_is_enemy)
        self.assertEqual(victim, cursed_player)
        self.assertTrue(self.engine._game_over)

        event_types = [e["type"] for e in self.broadcast_events]
        self.assertIn("NuevoJugadorMaldito", event_types)
        self.assertIn("FinJuego", event_types)

        fin_payload = next(e for e in self.broadcast_events if e["type"] == "FinJuego")
        self.assertIn("curse_history", fin_payload)
        self.assertIn("ghost_leaderboard", fin_payload)
        self.assertGreaterEqual(len(fin_payload["curse_history"]), 1)
        self.assertGreaterEqual(len(fin_payload["ghost_leaderboard"]), 1)

        first_curse = fin_payload["curse_history"][0]
        self.assertEqual(attacker, first_curse["origin"])
        self.assertEqual(victim, first_curse["target"])
        self.assertEqual(victim, first_curse["cursed_player"])
        self.assertTrue(first_curse["victim_is_enemy"])

        first_ghost = fin_payload["ghost_leaderboard"][0]
        self.assertIn("name", first_ghost)
        self.assertIn("points", first_ghost)
        self.assertIn("color", first_ghost)

    def test_end_condition_false_when_no_alive(self):
        self._initialize_game(["A", "B", "C", "D"])
        for player in self.engine._players.values():
            player.alive = False
        self.assertFalse(self.engine._is_end_condition_met_locked())

    def test_end_condition_false_when_both_teams_alive(self):
        self._initialize_game(["A", "B", "C", "D"])
        self.assertFalse(self.engine._is_end_condition_met_locked())

    def test_end_condition_sets_winner_and_broadcasts_finish(self):
        self._initialize_game(["A", "B", "C", "D"])

        now = time.monotonic()
        groups = self._alive_team_groups()
        team_names = list(groups.keys())
        eliminated_team = team_names[0]
        surviving_team = team_names[1]

        for player_name in groups[eliminated_team]:
            self.engine._make_ghost_locked(player_name, now)

        self.assertTrue(self.engine._is_end_condition_met_locked())

        self.engine._finish_game_locked(now)
        self.assertTrue(self.engine._game_over)
        self.assertEqual(surviving_team, self.engine._winner_team)
        self.assertGreater(len(self.engine._winner_players), 0)
        self.assertTrue(any(event["type"] == "FinJuego" for event in self.broadcast_events))

    def test_finish_game_noop_when_already_finished(self):
        self._initialize_game(["A", "B", "C", "D"])
        now = time.monotonic()

        self.engine._finish_game_locked(now)
        events_after_first = len(self.broadcast_events)
        self.engine._finish_game_locked(now + 1.0)
        self.assertEqual(events_after_first, len(self.broadcast_events))

    def test_finish_game_forces_intense_music_mode(self):
        self._initialize_game(["A", "B", "C", "D"])
        now = time.monotonic()

        self.engine._music_mode = "calm"
        self.engine._finish_game_locked(now)

        self.assertEqual("intense", self.engine._music_mode)
        self.assertTrue(any(e["type"] == "MusicModeChanged" and e["mode"] == "intense" for e in self.broadcast_events))

    def test_evaluate_music_switches_to_intense(self):
        self._initialize_game(["A", "B", "C", "D"])
        now = time.monotonic()

        alive_names = [name for name, p in self.engine._players.items() if p.alive]
        self.engine._players[alive_names[0]].hand_color = "red"
        self.engine._players[alive_names[1]].hand_color = "blue"
        self.engine._recent_flare_timestamps = deque([now - 1.0, now - 2.0])
        self.engine._recent_curse_timestamps = deque()
        self.engine._music_mode = "calm"
        self.engine._last_music_eval_at = now - 10.0

        self.engine._evaluate_music_locked(now)
        self.assertEqual("intense", self.engine._music_mode)
        self.assertTrue(any(e["type"] == "MusicModeChanged" and e["mode"] == "intense" for e in self.broadcast_events))

    def test_loop_recovers_after_tick_exception(self):
        self._initialize_game(["A", "B", "C", "D"])

        tick_counter = {"count": 0}

        def fail_once(now):
            tick_counter["count"] += 1
            if tick_counter["count"] == 1:
                raise RuntimeError("simulated loop failure")
            self.engine._running = False

        self.engine._running = True
        self.engine._process_hand_timeouts_locked = fail_once
        self.engine._expire_faces_locked = lambda now: None
        self.engine._try_release_color_locked = lambda now: None
        self.engine._evaluate_music_locked = lambda now: None

        with patch("servidor.games.flare_curse.flare_curse_engine.time.sleep", return_value=None):
            self.engine._loop()

        self.assertGreaterEqual(tick_counter["count"], 2)

    def test_loop_wait_room_redirect_does_not_rewrite_artifacts(self):
        self._initialize_game(["A", "B", "C", "D"])
        now = time.monotonic()

        self.engine._running = True
        self.engine._game_over = True
        self.engine._end_redirect_at = now - 0.1

        with patch.object(self.engine, "_write_match_artifacts_locked") as write_mock, patch(
            "servidor.games.flare_curse.flare_curse_engine.time.monotonic",
            return_value=now,
        ):
            self.engine._loop()

        write_mock.assert_not_called()
        self.assertFalse(self.engine._running)

    def test_build_match_event_rows_keeps_explicit_zero_score(self):
        self.engine._match_event_log = [
            {
                "time_seconds": 1.0,
                "type": "music_eval",
                "alive_total": 4,
                "concurrent_limit": 2,
                "offered_color": "",
                "music_mode": "intense",
                "score": 1.25,
                "payload": {},
            },
            {
                "time_seconds": 1.0,
                "type": "music_mode_changed",
                "alive_total": 4,
                "concurrent_limit": 2,
                "offered_color": "",
                "music_mode": "calm",
                "score": 0.0,
                "payload": {},
            },
        ]

        rows = self.engine._build_match_event_rows_locked()

        self.assertEqual(1, len(rows))
        self.assertEqual(0.0, rows[0]["score"])

    def test_evaluate_music_scales_hand_component_by_current_concurrency(self):
        self.engine._active_colors = ["red", "green", "blue", "purple", "orange"]
        self.engine.WEIGHT_COLORS_IN_HAND = 1.0
        self.engine.WEIGHT_RECENT_FLARES = 0.0
        self.engine.WEIGHT_RECENT_CURSES = 0.0
        self.engine.INTENSITY_THRESHOLD_HIGH = 0.6
        self.engine.INTENSITY_THRESHOLD_LOW = 0.4

        now = time.monotonic()

        # With 10 alive players, concurrent limit is 4 -> 1 hand color yields pressure 0.25.
        self._set_alive_count(10)
        alive_many = [name for name, p in self.engine._players.items() if p.alive]
        self.engine._players[alive_many[0]].hand_color = "red"
        self.engine._music_mode = "calm"
        self.engine._last_music_eval_at = now - 10.0
        self.engine._evaluate_music_locked(now)
        self.assertEqual("calm", self.engine._music_mode)
        self.assertEqual([], [e for e in self.broadcast_events if e["type"] == "MusicModeChanged"])

        # With 2 alive players, concurrent limit is 1 -> same hand count yields pressure 1.0.
        self._set_alive_count(2)
        alive_few = [name for name, p in self.engine._players.items() if p.alive]
        self.engine._players[alive_few[0]].hand_color = "red"
        self.engine._last_music_eval_at = now - 10.0
        self.engine._evaluate_music_locked(now + 1.0)
        self.assertEqual("intense", self.engine._music_mode)
        self.assertTrue(any(e["type"] == "MusicModeChanged" and e["mode"] == "intense" for e in self.broadcast_events))

    def test_evaluate_music_scales_recent_flares_and_curses_by_current_concurrency(self):
        self.engine._active_colors = ["red", "green", "blue", "purple", "orange"]
        self.engine.WEIGHT_COLORS_IN_HAND = 0.0
        self.engine.WEIGHT_RECENT_FLARES = 1.0
        self.engine.WEIGHT_RECENT_CURSES = 1.0
        self.engine.INTENSITY_THRESHOLD_HIGH = 0.7
        self.engine.INTENSITY_THRESHOLD_LOW = 0.5

        now = time.monotonic()

        # Same raw events on higher concurrency produce lower normalized pressure.
        self._set_alive_count(10)  # concurrent limit = 4
        self.engine._recent_flare_timestamps = deque([now - 1.0])
        self.engine._recent_curse_timestamps = deque([now - 0.8])
        self.engine._music_mode = "calm"
        self.engine._last_music_eval_at = now - 10.0
        self.engine._evaluate_music_locked(now)
        self.assertEqual("calm", self.engine._music_mode)
        self.assertEqual([], [e for e in self.broadcast_events if e["type"] == "MusicModeChanged"])

        # Same raw events on lower concurrency increase normalized pressure enough to switch.
        self._set_alive_count(2)  # concurrent limit = 1
        self.engine._recent_flare_timestamps = deque([now])
        self.engine._recent_curse_timestamps = deque([now])
        self.engine._last_music_eval_at = now - 10.0
        self.engine._evaluate_music_locked(now + 1.0)
        self.assertEqual("intense", self.engine._music_mode)
        self.assertTrue(any(e["type"] == "MusicModeChanged" and e["mode"] == "intense" for e in self.broadcast_events))

    def test_recent_event_normalization_uses_blended_concurrency_denominator(self):
        self.engine._active_colors = ["red", "green", "blue", "purple", "orange"]

        # With alive=7, concurrent limit is 3.
        self._set_alive_count(7)
        linear_many = self.engine._normalize_music_count_by_concurrency_locked(1)
        blended_many = self.engine._normalize_recent_event_count_locked(1)
        self.assertGreater(blended_many, linear_many)

        # With alive=2, concurrent limit is 1.
        self._set_alive_count(2)
        linear_few = self.engine._normalize_music_count_by_concurrency_locked(1)
        blended_few = self.engine._normalize_recent_event_count_locked(1)
        self.assertLess(blended_few, linear_few)

    def test_initialize_derives_recent_event_reference_from_initial_concurrency_midpoint(self):
        self._initialize_game(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"])

        self.assertEqual(4, self.engine._initial_concurrent_limit_for_match)
        self.assertAlmostEqual(2.5, self.engine._event_concurrency_reference)

    def test_evaluate_music_switches_to_calm(self):
        self._initialize_game(["A", "B", "C", "D"])
        now = time.monotonic()

        self.engine._music_mode = "intense"
        self.engine._last_music_eval_at = now - 10.0
        self.engine._recent_flare_timestamps = deque()
        self.engine._recent_curse_timestamps = deque()

        self.engine._evaluate_music_locked(now)
        self.assertEqual("calm", self.engine._music_mode)
        self.assertTrue(any(e["type"] == "MusicModeChanged" and e["mode"] == "calm" for e in self.broadcast_events))

    def test_evaluate_music_respects_eval_interval(self):
        self._initialize_game(["A", "B", "C", "D"])
        now = time.monotonic()

        self.engine._last_music_eval_at = now
        self.engine._evaluate_music_locked(now)
        self.assertEqual([], [e for e in self.broadcast_events if e["type"] == "MusicModeChanged"])

    def test_trim_recent_events_discards_old_entries(self):
        self._initialize_game(["A", "B", "C", "D"])
        now = time.monotonic()

        self.engine._recent_flare_timestamps = deque(
            [now - self.engine.INTENSITY_CUTOFF_SECONDS - 1.0, now - 1.0]
        )
        self.engine._recent_curse_timestamps = deque(
            [now - self.engine.INTENSITY_CUTOFF_SECONDS - 2.0, now - 0.5]
        )

        self.engine._trim_recent_events_locked(now)
        self.assertEqual(1, len(self.engine._recent_flare_timestamps))
        self.assertEqual(1, len(self.engine._recent_curse_timestamps))

    def test_concurrent_colors_limit_boundaries(self):
        self.engine._active_colors = ["red", "green", "blue", "purple", "orange"]

        self._set_alive_count(10)
        self.assertEqual(4, self.engine._concurrent_colors_limit_locked())

        self._set_alive_count(7)
        self.assertEqual(3, self.engine._concurrent_colors_limit_locked())

        self._set_alive_count(4)
        self.assertEqual(2, self.engine._concurrent_colors_limit_locked())

        self._set_alive_count(2)
        self.assertEqual(1, self.engine._concurrent_colors_limit_locked())

        self._set_alive_count(1)
        self.assertEqual(0, self.engine._concurrent_colors_limit_locked())

    def test_concurrency_rules_are_configurable(self):
        self.engine._active_colors = ["red", "green", "blue", "purple", "orange"]
        self.engine.COLOR_CONCURRENCY_RULES = (
            (6, 3),
            (3, 2),
            (1, 1),
        )

        self._set_alive_count(6)
        self.assertEqual(3, self.engine._concurrent_colors_limit_locked())
        self._set_alive_count(4)
        self.assertEqual(2, self.engine._concurrent_colors_limit_locked())
        self._set_alive_count(1)
        self.assertEqual(1, self.engine._concurrent_colors_limit_locked())

    def test_initial_total_colors_boundaries(self):
        self.assertEqual(4, self.engine._initial_total_colors(10))
        self.assertEqual(3, self.engine._initial_total_colors(7))
        self.assertEqual(2, self.engine._initial_total_colors(4))
        self.assertEqual(1, self.engine._initial_total_colors(3))
        self.assertEqual(0, self.engine._initial_total_colors(1))

    def test_initial_total_colors_can_override_concurrency_based_default(self):
        self.engine.INITIAL_TOTAL_COLORS = 5
        self.assertEqual(5, self.engine._initial_total_colors(2))

        self.engine.INITIAL_TOTAL_COLORS = 4
        self.assertEqual(4, self.engine._initial_total_colors(1))

    def test_initial_total_colors_override_is_clamped_and_invalid_falls_back(self):
        self.engine.INITIAL_TOTAL_COLORS = 99
        self.assertEqual(len(self.engine.COLORS), self.engine._initial_total_colors(10))

        self.engine.INITIAL_TOTAL_COLORS = -3
        self.assertEqual(0, self.engine._initial_total_colors(10))

        self.engine.INITIAL_TOTAL_COLORS = "invalid"
        self.assertEqual(2, self.engine._initial_total_colors(4))

    def test_default_initial_total_colors_with_odd_players_uses_alive_after_initial_ghost(self):
        self.engine.INITIAL_TOTAL_COLORS = None
        self._initialize_game(["A", "B", "C", "D", "E"])

        alive_count = sum(1 for p in self.engine._players.values() if p.alive)
        self.assertEqual(4, alive_count)
        self.assertEqual(1, len(self.engine._ghosts))
        self.assertEqual(2, len(self.engine._active_colors))

    def test_override_initial_total_colors_seeds_all_active_colors_in_timeout_queue(self):
        self.engine.INITIAL_TOTAL_COLORS = 5
        self._initialize_game(["A", "B", "C", "D", "E"])

        timeout_colors = [entry[2] for entry in self.engine._timeout_queue]
        self.assertEqual(5, len(self.engine._active_colors))
        self.assertEqual(5, len(timeout_colors))
        self.assertEqual(set(self.engine._active_colors), set(timeout_colors))

        # Concurrency remains tied to alive players, even with a larger total pool.
        self.assertEqual(2, self.engine._concurrent_colors_limit_locked())

    def test_seconds_left_helper(self):
        now = time.monotonic()
        self.assertEqual(0.0, self.engine._seconds_left(now, 0.0))
        self.assertEqual(0.0, self.engine._seconds_left(now, now - 1.0))
        self.assertGreater(self.engine._seconds_left(now, now + 2.0), 1.9)

    def test_gameplay_does_not_touch_coins(self):
        with patch("servidor.games.flare_curse.flare_curse_engine.q.add_coins_to_player") as add_coins_mock:
            self._initialize_game(["A", "B", "C", "D"])

            self.engine._offered_color = "green"
            self.assertTrue(self.engine.claim_flare("A", "green"))
            self.engine.launch_flare("A")

            groups = self._alive_team_groups()
            team_names = list(groups.keys())
            attacker = groups[team_names[0]][0]
            target = groups[team_names[1]][0]
            self.engine.cast_curse(attacker, target)

            add_coins_mock.assert_not_called()


class TestFlareCurseEngineHelpers(unittest.TestCase):
    def test_sanitize_group_name(self):
        self.assertEqual("anon", sanitize_group_name(None))
        self.assertEqual("ana-foo-1", sanitize_group_name("Ana Foo@1"))
        self.assertEqual("tona", sanitize_group_name("Toña"))
        self.assertEqual("ana_maria", sanitize_group_name("Ana_María"))
        self.assertEqual("anon", sanitize_group_name("***"))

    def test_get_player_group_name(self):
        group = get_player_group_name(" Ju@n ")
        self.assertTrue(group.startswith("flare-curse-player-"))
        self.assertIn("ju-n", group)

        group_unicode = get_player_group_name("Toña")
        self.assertTrue(group_unicode.startswith("flare-curse-player-"))
        self.assertIn("tona", group_unicode)
        self.assertNotIn("ñ", group_unicode)


if __name__ == "__main__":
    unittest.main()
