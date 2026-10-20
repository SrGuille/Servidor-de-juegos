import datetime
import os
import random
import threading
import time
import unicodedata
from bisect import insort
from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, List, Optional, Tuple

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from servidor import main_views
from servidor import queries as q


FLARE_CURSE_GAME_ID = 6
ROOM_GROUP_NAME = "flare-curse-room"


@dataclass
class FlareCursePlayerState:
    name: str
    team: str
    alive: bool = True
    hand_color: Optional[str] = None
    hand_expires_at: float = 0.0
    face_color: Optional[str] = None
    face_expires_at: float = 0.0
    last_face_color: Optional[str] = None
    last_face_at: float = 0.0
    last_face_expires_at: float = 0.0


@dataclass
class FlareCurseGhostState:
    color: str
    points: int = 0
    cooldown_expires_at: float = 0.0
    became_ghost_at: float = 0.0


class FlareCurseEngine:
    """
    Server-authoritative Flare Curse state machine with a periodic loop.
    It is intentionally isolated from coins/prizes: no economy writes are performed.
    """

    COLORS = ["red", "green", "blue", "purple"]

    # Timings tuned for phase 1 baseline.
    INITIAL_DELAY_SECONDS = 7.0
    HOLD_COLOR_SECONDS = 7.0
    FLASH_SECONDS = 1.3
    RELEASE_GAP_RANGE_SECONDS = (1.0, 2.0)
    USED_COLOR_COOLDOWN_RANGE_SECONDS = (8.0, 10.0)
    GHOST_COOLDOWN_SECONDS = 9.0
    GHOST_POST_FACE_GRACE_SECONDS = 1.0
    END_SCREEN_SECONDS = 60.0

    # Optional override for the total color pool available in the match.
    # None keeps legacy behavior based on COLOR_CONCURRENCY_RULES and initial alive count.
    INITIAL_TOTAL_COLORS = None

    # Configurable mapping: minimum alive players -> maximum concurrent colors.
    COLOR_CONCURRENCY_RULES = (
        (10, 3),
        (7, 2),
        (3, 1),
    )

    # Music intensity (phase 1 server decisions; client may choose to use/ignore).
    MUSIC_EVAL_SECONDS = 2.5
    INTENSITY_THRESHOLD_HIGH = 1.4
    INTENSITY_THRESHOLD_LOW = 0.9
    INTENSITY_CUTOFF_SECONDS = 10.0
    WEIGHT_COLORS_IN_HAND = 1.0
    WEIGHT_RECENT_FLARES = 0.8
    WEIGHT_RECENT_CURSES = -0.6
    # Smooth event-pressure normalization so early game is less penalized and end game less amplified.
    EVENT_CONCURRENCY_BLEND_ALPHA = 0.65
    EVENT_CONCURRENCY_REFERENCE = 2.0

    MATCH_LOG_DIR_NAME = "flare_curse_log"

    def __init__(self):
        self._lock = threading.RLock()
        self._running = False
        self._thread: Optional[threading.Thread] = None

        self._players: Dict[str, FlareCursePlayerState] = {}
        self._ghosts: Dict[str, FlareCurseGhostState] = {}

        self._active_colors: List[str] = []
        self._timeout_queue: List[Tuple[float, int, str]] = []
        self._used_queue: List[Tuple[float, int, str]] = []
        self._release_order: int = 0

        self._offered_color: Optional[str] = None
        self._last_release_at: float = 0.0
        self._next_gap_seconds: float = 0.0
        self._release_enabled_at: float = 0.0

        self._last_real_flash_players: List[str] = []
        self._last_real_flash_color: Optional[str] = None
        self._last_real_flash_until: float = 0.0

        self._recent_flare_timestamps: Deque[float] = deque()
        self._recent_curse_timestamps: Deque[float] = deque()
        self._initial_concurrent_limit_for_match: int = 0
        self._event_concurrency_reference: float = float(self.EVENT_CONCURRENCY_REFERENCE)
        self._music_mode = "calm"
        self._last_music_eval_at: float = 0.0
        self._last_intensity_score: float = 0.0

        self._match_started_at_monotonic: float = 0.0
        self._match_started_at_utc: Optional[datetime.datetime] = None
        self._match_log_basename: str = ""
        self._match_event_log: List[Dict] = []
        self._match_music_eval_log: List[Dict] = []

        self._game_over = False
        self._end_redirect_at: float = 0.0
        self._winner_team: Optional[str] = None
        self._winner_players: List[str] = []
        self._ghost_winners: List[str] = []
        self._curse_history: List[Dict] = []

    # -----------------------------
    # Public API used by consumer
    # -----------------------------

    def ensure_started(self) -> bool:
        """
        Initializes a fresh game if selected and not already running.
        Returns True when game state is ready (running or initialized).
        """
        with self._lock:
            if self._running:
                return True

            ready_game_id = main_views.main_controller_.get_ready_to_join_game()
            if ready_game_id != FLARE_CURSE_GAME_ID:
                return False

            players = q.get_logged_players_names()
            if len(players) < 2:
                return False

            self._initialize_locked(players)
            self._running = True
            self._thread = threading.Thread(target=self._loop, name="flare-curse-loop", daemon=True)
            self._thread.start()
            return True

    def get_snapshot_for_player(self, player_name: str) -> Dict:
        with self._lock:
            now = time.monotonic()
            player = self._players.get(player_name)
            if player is None:
                return {
                    "type": "Error",
                    "message": "Jugador no encontrado en Flare Curse.",
                }

            ghost_state = self._ghosts.get(player_name)
            role = "ghost" if ghost_state is not None else "alive"

            players_payload = []
            for other_name in sorted(self._players.keys()):
                other = self._players[other_name]
                if other_name == player_name:
                    team_symbol = other.team
                elif other.alive:
                    team_symbol = None
                else:
                    team_symbol = other.team

                players_payload.append(
                    {
                        "name": other_name,
                        "status": "alive" if other.alive else "ghost",
                        "team_symbol": team_symbol,
                    }
                )

            return {
                "type": "GameSnapshot",
                "you": {
                    "name": player_name,
                    "role": role,
                    "team_symbol": player.team,
                    "hand_color": player.hand_color,
                    "hand_seconds_left": self._seconds_left(now, player.hand_expires_at),
                    "ghost_color": ghost_state.color if ghost_state else None,
                    "ghost_points": ghost_state.points if ghost_state else 0,
                    "ghost_cooldown_seconds_left": self._seconds_left(now, ghost_state.cooldown_expires_at if ghost_state else 0.0),
                },
                "timings": {
                    "hold_color_seconds": self.HOLD_COLOR_SECONDS,
                    "ghost_cooldown_seconds": self.GHOST_COOLDOWN_SECONDS,
                },
                "players": players_payload,
                "offered_color": self._offered_color,
                "music_mode": self._music_mode,
                "game_over": self._game_over,
                "winner_team": self._winner_team,
                "winner_players": self._winner_players,
                "ghost_winners": self._ghost_winners,
                "end_screen_seconds_left": self._seconds_left(now, self._end_redirect_at),
            }

    def claim_flare(self, player_name: str, color: str) -> bool:
        with self._lock:
            if self._game_over:
                return False

            player = self._players.get(player_name)
            if player is None or not player.alive:
                return False
            if player.hand_color is not None:
                return False
            if self._offered_color != color:
                return False

            now = time.monotonic()
            player.hand_color = color
            player.hand_expires_at = now + self.HOLD_COLOR_SECONDS

            self._record_match_event_locked(
                "claim",
                now=now,
                player=player_name,
                color=color,
                hand_expires_at=round(player.hand_expires_at - self._match_started_at_monotonic, 3),
            )

            self._close_offer_locked()
            return True

    def launch_flare(self, player_name: str) -> bool:
        with self._lock:
            if self._game_over:
                return False

            source = self._players.get(player_name)
            if source is None or not source.alive:
                return False
            if source.hand_color is None:
                return False

            now = time.monotonic()
            color = source.hand_color
            source.hand_color = None
            source.hand_expires_at = 0.0

            ready_at = now + random.uniform(*self.USED_COLOR_COOLDOWN_RANGE_SECONDS)
            self._enqueue_color_ready_at_locked(self._used_queue, color, ready_at)

            enemy_candidates = [
                p.name
                for p in self._players.values()
                if p.alive and p.team != source.team
            ]
            if not enemy_candidates:
                return False

            target_name = random.choice(enemy_candidates)
            flash_until = now + self.FLASH_SECONDS
            self._apply_face_color_locked(player_name, color, flash_until)
            self._apply_face_color_locked(target_name, color, flash_until)

            self._last_real_flash_players = [player_name, target_name]
            self._last_real_flash_color = color
            self._last_real_flash_until = flash_until

            self._recent_flare_timestamps.append(now)
            self._record_match_event_locked(
                "launch_flare",
                now=now,
                player=player_name,
                target=target_name,
                color=color,
            )

            payload_source = {
                "type": "TeHanLanzadoDestello",
                "player": player_name,
                "color": color,
                "duration_seconds": self.FLASH_SECONDS,
            }
            payload_target = {
                "type": "TeHanLanzadoDestello",
                "player": target_name,
                "color": color,
                "duration_seconds": self.FLASH_SECONDS,
            }
            self._send_to_player_locked(player_name, payload_source)
            self._send_to_player_locked(target_name, payload_target)
            return True

    def launch_ghost_flare(self, player_name: str) -> Tuple[bool, int, float]:
        with self._lock:
            if self._game_over:
                return False, 0, 0.0

            ghost = self._ghosts.get(player_name)
            if ghost is None:
                return False, 0, 0.0

            now = time.monotonic()
            if ghost.cooldown_expires_at > now:
                self._record_match_event_locked(
                    "ghost_launch_cooldown_blocked",
                    now=now,
                    player=player_name,
                    cooldown_left=self._seconds_left(now, ghost.cooldown_expires_at),
                    ghost_points=ghost.points,
                )
                return False, ghost.points, self._seconds_left(now, ghost.cooldown_expires_at)

            color = ghost.color
            active_with_color = [
                p.name
                for p in self._players.values()
                if p.alive and p.face_color == color and p.face_expires_at > now
            ]
            recently_expired_with_color = self._recently_expired_face_players_locked(color, now)

            trigger_players = set(active_with_color) | set(recently_expired_with_color)
            in_time = len(trigger_players) > 0

            if in_time:
                eligible_targets = [
                    p.name
                    for p in self._players.values()
                    if p.alive and p.name not in trigger_players
                ]
                if eligible_targets:
                    target_name = random.choice(eligible_targets)
                    remaining = self._ghost_chain_duration_seconds_locked(
                        now,
                        active_with_color,
                        recently_expired_with_color,
                    )
                    self._apply_face_color_locked(target_name, color, now + remaining)
                    self._send_to_player_locked(
                        target_name,
                        {
                            "type": "TeHanLanzadoDestello",
                            "player": target_name,
                            "color": color,
                            "duration_seconds": remaining,
                        },
                    )
                    ghost.points += 1
                    self._record_match_event_locked(
                        "ghost_launch_flare",
                        now=now,
                        player=player_name,
                        target=target_name,
                        color=color,
                        success=True,
                        points=ghost.points,
                    )
                else:
                    in_time = False

            if not in_time:
                self._record_match_event_locked(
                    "ghost_launch_flare",
                    now=now,
                    player=player_name,
                    color=color,
                    success=False,
                    points=ghost.points,
                )

            ghost.cooldown_expires_at = now + self.GHOST_COOLDOWN_SECONDS
            return in_time, ghost.points, self.GHOST_COOLDOWN_SECONDS

    def cast_curse(self, origin_name: str, target_name: str) -> Tuple[bool, bool, Optional[str]]:
        """
        Returns: (accepted, victim_is_enemy, cursed_player_name).
        """
        with self._lock:
            if self._game_over:
                return False, False, None

            origin = self._players.get(origin_name)
            target = self._players.get(target_name)
            if origin is None or target is None:
                return False, False, None
            if not origin.alive or not target.alive:
                return False, False, None
            if origin_name == target_name:
                return False, False, None

            now = time.monotonic()
            victim_is_enemy = origin.team != target.team
            cursed_name = target_name if victim_is_enemy else origin_name

            ghost_color = self._make_ghost_locked(cursed_name, now)
            self._recent_curse_timestamps.append(now)

            self._curse_history.append(
                {
                    "order": len(self._curse_history) + 1,
                    "origin": origin_name,
                    "origin_team": origin.team,
                    "target": target_name,
                    "target_team": target.team,
                    "cursed_player": cursed_name,
                    "cursed_team": self._players[cursed_name].team,
                    "victim_is_enemy": victim_is_enemy,
                    "result": "enemy_hit" if victim_is_enemy else "self_rebound",
                    "at_seconds": round(max(0.0, now - self._match_started_at_monotonic), 3),
                }
            )

            self._record_match_event_locked(
                "curse_enemy_hit" if victim_is_enemy else "curse_self_rebound",
                now=now,
                origin=origin_name,
                target=target_name,
                cursed=cursed_name,
                ghost_color=ghost_color,
            )

            # Public announcement for all clients.
            self._broadcast_locked(
                {
                    "type": "NuevoJugadorMaldito",
                    "player": cursed_name,
                    "team": self._players[cursed_name].team,
                    "ghost_color": ghost_color,
                    "fin_juego": False,
                }
            )

            if self._is_end_condition_met_locked():
                self._finish_game_locked(now)

            return True, victim_is_enemy, cursed_name

    # -----------------------------
    # Internal lifecycle
    # -----------------------------

    def _initialize_locked(self, player_names: List[str]) -> None:
        now = time.monotonic()

        self._players = {}
        self._ghosts = {}
        self._timeout_queue = []
        self._used_queue = []
        self._release_order = 0

        shuffled = list(player_names)
        random.shuffle(shuffled)

        initial_ghost_name = None
        initial_ghost_team = None
        if len(shuffled) % 2 == 1:
            initial_ghost_name = random.choice(shuffled)
            shuffled.remove(initial_ghost_name)
            # Initial ghost has its own symbol and is not part of either living team.
            initial_ghost_team = "ghost"

        half = len(shuffled) // 2
        circle_team = set(shuffled[:half])
        square_team = set(shuffled[half:])

        for name in player_names:
            if initial_ghost_name is not None and name == initial_ghost_name:
                team = initial_ghost_team
            else:
                team = "circle" if name in circle_team else "square"
            self._players[name] = FlareCursePlayerState(name=name, team=team)

        num_colors = self._initial_total_colors(len(shuffled))
        color_pool = self.COLORS[:]
        random.shuffle(color_pool)
        self._active_colors = color_pool[:num_colors]

        queue_seed = self._active_colors[:]
        random.shuffle(queue_seed)
        for color in queue_seed:
            self._enqueue_color_ready_at_locked(self._timeout_queue, color, now)

        self._offered_color = None
        self._last_release_at = now
        self._next_gap_seconds = random.uniform(*self.RELEASE_GAP_RANGE_SECONDS)
        self._release_enabled_at = now + self.INITIAL_DELAY_SECONDS

        self._last_real_flash_players = []
        self._last_real_flash_color = None
        self._last_real_flash_until = 0.0

        self._recent_flare_timestamps = deque()
        self._recent_curse_timestamps = deque()
        self._initial_concurrent_limit_for_match = 0
        self._event_concurrency_reference = float(self.EVENT_CONCURRENCY_REFERENCE)
        self._music_mode = "calm"
        self._last_music_eval_at = now
        self._last_intensity_score = 0.0

        self._match_started_at_monotonic = now
        self._match_started_at_utc = datetime.datetime.utcnow()
        self._match_log_basename = "flare_curse_match_{}_{}".format(
            self._match_started_at_utc.strftime("%Y%m%d_%H%M%S"),
            int(now * 1000) % 100000,
        )
        self._match_event_log = []
        self._match_music_eval_log = []

        self._game_over = False
        self._end_redirect_at = 0.0
        self._winner_team = None
        self._winner_players = []
        self._ghost_winners = []
        self._curse_history = []

        if initial_ghost_name is not None:
            self._make_ghost_locked(initial_ghost_name, now)

        self._initial_concurrent_limit_for_match = self._concurrent_colors_limit_locked()
        self._event_concurrency_reference = self._derive_event_concurrency_reference_locked(
            self._initial_concurrent_limit_for_match
        )

        self._record_match_event_locked(
            "match_initialized",
            now=now,
            players_total=len(player_names),
            alive_total=len([player for player in self._players.values() if player.alive]),
            active_colors=list(self._active_colors),
            initial_ghost=initial_ghost_name,
            event_reference=self._event_concurrency_reference,
        )

        main_views.main_controller_.set_can_players_join(False)
        main_views.main_controller_.set_can_players_interact(True)

    def _loop(self) -> None:
        while True:
            try:
                with self._lock:
                    if not self._running:
                        break

                    now = time.monotonic()
                    if not self._game_over:
                        self._process_hand_timeouts_locked(now)
                        self._expire_faces_locked(now)
                        self._try_release_color_locked(now)
                        self._evaluate_music_locked(now)
                    else:
                        if self._end_redirect_at > 0.0 and now >= self._end_redirect_at:
                            self._record_match_event_locked("go_to_wait_room", now=now)
                            self._broadcast_locked({"type": "GoToWaitRoom"})
                            self._running = False
                            break
            except Exception as exc:
                print("[FlareCurse] loop tick error (recovered): {}".format(exc))

            time.sleep(0.1)

    # -----------------------------
    # Internal gameplay operations
    # -----------------------------

    def _process_hand_timeouts_locked(self, now: float) -> None:
        for player in self._players.values():
            if not player.alive:
                continue
            if player.hand_color is None:
                continue
            if player.hand_expires_at > now:
                continue

            timed_out_color = player.hand_color
            player.hand_color = None
            player.hand_expires_at = 0.0

            # Timeout queue has release priority.
            self._enqueue_color_ready_at_locked(self._timeout_queue, timed_out_color, now)
            self._send_to_player_locked(
                player.name,
                {
                    "type": "TimeoutDestello",
                    "player": player.name,
                    "color": timed_out_color,
                },
            )
            self._record_match_event_locked(
                "timeout",
                now=now,
                player=player.name,
                color=timed_out_color,
            )

    def _expire_faces_locked(self, now: float) -> None:
        for player in self._players.values():
            if player.face_color is not None and player.face_expires_at <= now:
                player.face_color = None
                player.face_expires_at = 0.0

    def _try_release_color_locked(self, now: float) -> None:
        if now < self._release_enabled_at:
            return
        if self._offered_color is not None:
            return

        in_hand = self._count_colors_in_hand_locked()
        max_concurrent = self._concurrent_colors_limit_locked()
        if in_hand >= max_concurrent:
            return

        if now - self._last_release_at < self._next_gap_seconds:
            return

        color_to_release = None

        if self._timeout_queue:
            _, _, color_to_release = self._timeout_queue.pop(0)
        elif self._used_queue:
            ready_at, _, next_color = self._used_queue[0]
            if ready_at <= now:
                color_to_release = next_color
                self._used_queue.pop(0)

        if color_to_release is None:
            return

        self._offered_color = color_to_release
        self._last_release_at = now
        self._next_gap_seconds = random.uniform(*self.RELEASE_GAP_RANGE_SECONDS)

        self._broadcast_locked({"type": "DestelloDisponible", "color": color_to_release})
        self._record_match_event_locked("offer_opened", now=now, color=color_to_release)

    def _close_offer_locked(self) -> None:
        if self._offered_color is None:
            return

        color = self._offered_color
        self._offered_color = None
        self._broadcast_locked({"type": "DestelloNoDisponible", "color": color})
        self._record_match_event_locked("offer_closed", now=time.monotonic(), color=color)

    def _apply_face_color_locked(self, player_name: str, color: str, until_ts: float) -> None:
        player = self._players[player_name]
        player.face_color = color
        player.face_expires_at = until_ts
        player.last_face_color = color
        player.last_face_at = time.monotonic()
        player.last_face_expires_at = until_ts

    def _make_ghost_locked(self, player_name: str, now: float) -> str:
        player = self._players[player_name]
        if not player.alive:
            return self._ghosts[player_name].color

        if player.hand_color is not None:
            timed_out_color = player.hand_color
            player.hand_color = None
            player.hand_expires_at = 0.0
            self._enqueue_color_ready_at_locked(self._timeout_queue, timed_out_color, now)
            self._send_to_player_locked(
                player_name,
                {
                    "type": "TimeoutDestello",
                    "player": player_name,
                    "color": timed_out_color,
                },
            )

        player.alive = False
        ghost_color = player.last_face_color or self._pick_least_used_ghost_color_locked()
        self._ghosts[player_name] = FlareCurseGhostState(
            color=ghost_color,
            points=0,
            cooldown_expires_at=0.0,
            became_ghost_at=now,
        )
        self._record_match_event_locked(
            "player_became_ghost",
            now=now,
            player=player_name,
            team=player.team,
            ghost_color=ghost_color,
        )
        return ghost_color

    def _pick_least_used_ghost_color_locked(self) -> str:
        if not self._active_colors:
            return "red"

        counts = {color: 0 for color in self._active_colors}
        for ghost in self._ghosts.values():
            if ghost.color in counts:
                counts[ghost.color] += 1

        min_count = min(counts.values())
        candidates = [color for color, cnt in counts.items() if cnt == min_count]
        return random.choice(candidates)

    def _recently_expired_face_players_locked(self, color: str, now: float) -> List[str]:
        recent_players = []
        for player in self._players.values():
            if not player.alive:
                continue
            if player.face_color is not None:
                continue
            if player.last_face_color != color:
                continue

            elapsed_since_off = now - player.last_face_expires_at
            if 0.0 <= elapsed_since_off <= self.GHOST_POST_FACE_GRACE_SECONDS:
                recent_players.append(player.name)

        return recent_players

    def _ghost_chain_duration_seconds_locked(
        self,
        now: float,
        active_with_color: List[str],
        recently_expired_with_color: List[str],
    ) -> float:
        if active_with_color:
            active_until = max(self._players[name].face_expires_at for name in active_with_color)
            return max(0.2, active_until - now)

        if recently_expired_with_color:
            most_recent_off = max(self._players[name].last_face_expires_at for name in recently_expired_with_color)
            grace_left = self.GHOST_POST_FACE_GRACE_SECONDS - max(0.0, now - most_recent_off)
            return max(0.2, grace_left)

        return 0.2

    def _is_end_condition_met_locked(self) -> bool:
        alive_players = [p for p in self._players.values() if p.alive]
        if not alive_players:
            return False

        alive_teams = {p.team for p in alive_players}
        return len(alive_teams) == 1

    def _finish_game_locked(self, now: float) -> None:
        if self._game_over:
            return

        self._game_over = True
        self._end_redirect_at = now + self.END_SCREEN_SECONDS
        main_views.main_controller_.set_can_players_interact(False)

        # Keep the end screen under intense loop to emphasize match closure.
        if self._music_mode != "intense":
            self._music_mode = "intense"
            self._broadcast_locked({"type": "MusicModeChanged", "mode": "intense", "score": None})
            self._record_match_event_locked("music_mode_changed", now=now, mode="intense", score=None)

        alive_players = [p.name for p in self._players.values() if p.alive]
        alive_team = None
        if alive_players:
            alive_team = self._players[alive_players[0]].team

        self._winner_team = alive_team
        self._winner_players = alive_players

        ghost_winners = []
        if self._ghosts:
            max_points = max(ghost.points for ghost in self._ghosts.values())
            ghost_winners = sorted([name for name, ghost in self._ghosts.items() if ghost.points == max_points])
        self._ghost_winners = ghost_winners
        ghost_leaderboard = self._build_ghost_leaderboard_locked()

        self._broadcast_locked(
            {
                "type": "FinJuego",
                "winner_team": self._winner_team,
                "winner_players": self._winner_players,
                "ghost_winners": self._ghost_winners,
                "ghost_points": {name: ghost.points for name, ghost in self._ghosts.items()},
                "ghost_leaderboard": ghost_leaderboard,
                "curse_history": list(self._curse_history),
                "redirect_in_seconds": self.END_SCREEN_SECONDS,
            }
        )
        self._record_match_event_locked(
            "match_finished",
            now=now,
            winner_team=self._winner_team,
            winner_players=list(self._winner_players),
            ghost_winners=list(self._ghost_winners),
        )
        if self._running:
            self._write_match_artifacts_locked()

    def _evaluate_music_locked(self, now: float) -> None:
        if now - self._last_music_eval_at < self.MUSIC_EVAL_SECONDS:
            return

        self._last_music_eval_at = now
        self._trim_recent_events_locked(now)

        colors_in_hand = self._count_colors_in_hand_locked()
        colors_in_hand_norm = self._colors_in_hand_norm_locked(colors_in_hand)
        recent_flares = self._normalize_recent_event_count_locked(len(self._recent_flare_timestamps))
        recent_curses = self._normalize_recent_event_count_locked(len(self._recent_curse_timestamps))

        intensity = (
            self.WEIGHT_COLORS_IN_HAND * colors_in_hand_norm
            + self.WEIGHT_RECENT_FLARES * recent_flares
            + self.WEIGHT_RECENT_CURSES * recent_curses
        )
        self._last_intensity_score = float(intensity)

        self._match_music_eval_log.append(
            {
                "time_seconds": round(max(0.0, now - self._match_started_at_monotonic), 3),
                "score": round(float(intensity), 6),
                "mode_before": self._music_mode,
                "colors_in_hand": int(colors_in_hand),
                "recent_flares": int(len(self._recent_flare_timestamps)),
                "recent_curses": int(len(self._recent_curse_timestamps)),
                "colors_norm": float(colors_in_hand_norm),
                "flares_norm": float(recent_flares),
                "curses_norm": float(recent_curses),
            }
        )
        self._record_match_event_locked(
            "music_eval",
            now=now,
            score=round(float(intensity), 6),
            colors_in_hand=int(colors_in_hand),
            recent_flares=int(len(self._recent_flare_timestamps)),
            recent_curses=int(len(self._recent_curse_timestamps)),
            colors_norm=round(float(colors_in_hand_norm), 6),
            flares_norm=round(float(recent_flares), 6),
            curses_norm=round(float(recent_curses), 6),
        )

        if self._music_mode == "calm" and intensity >= self.INTENSITY_THRESHOLD_HIGH:
            self._music_mode = "intense"
            self._broadcast_locked({"type": "MusicModeChanged", "mode": "intense", "score": intensity})
            self._record_match_event_locked("music_mode_changed", now=now, mode="intense", score=round(float(intensity), 6))
        elif self._music_mode == "intense" and intensity <= self.INTENSITY_THRESHOLD_LOW:
            self._music_mode = "calm"
            self._broadcast_locked({"type": "MusicModeChanged", "mode": "calm", "score": intensity})
            self._record_match_event_locked("music_mode_changed", now=now, mode="calm", score=round(float(intensity), 6))

    def _trim_recent_events_locked(self, now: float) -> None:
        while self._recent_flare_timestamps and now - self._recent_flare_timestamps[0] > self.INTENSITY_CUTOFF_SECONDS:
            self._recent_flare_timestamps.popleft()
        while self._recent_curse_timestamps and now - self._recent_curse_timestamps[0] > self.INTENSITY_CUTOFF_SECONDS:
            self._recent_curse_timestamps.popleft()

    # -----------------------------
    # Internal helpers
    # -----------------------------

    def _count_colors_in_hand_locked(self) -> int:
        return sum(1 for p in self._players.values() if p.alive and p.hand_color is not None)

    def _colors_in_hand_norm_locked(self, colors_in_hand: int) -> float:
        return self._normalize_music_count_by_concurrency_locked(colors_in_hand)

    def _normalize_music_count_by_concurrency_locked(self, count: int) -> float:
        concurrent_limit = self._concurrent_colors_limit_locked()
        if concurrent_limit <= 0:
            return 0.0

        return float(count) / float(concurrent_limit)

    def _normalize_recent_event_count_locked(self, count: int) -> float:
        concurrent_limit = self._concurrent_colors_limit_locked()
        if concurrent_limit <= 0:
            return 0.0

        alpha = max(0.0, min(1.0, float(self.EVENT_CONCURRENCY_BLEND_ALPHA)))
        reference = self._recent_event_reference_locked()
        denominator = (alpha * float(concurrent_limit)) + ((1.0 - alpha) * reference)
        if denominator <= 0.0:
            return 0.0

        return float(count) / denominator

    def _derive_event_concurrency_reference_locked(self, initial_concurrent_limit: int) -> float:
        if initial_concurrent_limit <= 0:
            return max(0.001, float(self.EVENT_CONCURRENCY_REFERENCE))

        # Dynamic reference is midpoint between the match initial concurrency and final target 1.
        return max(0.001, (float(initial_concurrent_limit) + 1.0) / 2.0)

    def _recent_event_reference_locked(self) -> float:
        reference = float(self._event_concurrency_reference)
        if reference <= 0.0:
            return max(0.001, float(self.EVENT_CONCURRENCY_REFERENCE))
        return reference

    def _record_match_event_locked(self, event_type: str, now: Optional[float] = None, **payload) -> None:
        if now is None:
            now = time.monotonic()

        if self._match_started_at_monotonic > 0.0:
            time_seconds = max(0.0, now - self._match_started_at_monotonic)
        else:
            time_seconds = 0.0

        alive_total = sum(1 for player in self._players.values() if player.alive)
        concurrent_limit = self._concurrent_colors_limit_locked()

        self._match_event_log.append(
            {
                "time_seconds": round(time_seconds, 3),
                "type": str(event_type),
                "alive_total": int(alive_total),
                "concurrent_limit": int(concurrent_limit),
                "offered_color": self._offered_color or "",
                "music_mode": self._music_mode,
                "score": round(float(self._last_intensity_score), 6),
                "payload": dict(payload),
            }
        )

    def _match_log_directory_path(self) -> str:
        return os.path.join(os.path.dirname(__file__), self.MATCH_LOG_DIR_NAME)

    def _build_match_event_rows_locked(self) -> List[Dict]:
        rows: List[Dict] = []
        by_time: Dict[float, Dict] = {}

        for event in self._match_event_log:
            time_seconds = float(event["time_seconds"])
            row = by_time.get(time_seconds)
            if row is None:
                row = {
                    "time_seconds": time_seconds,
                    "alive_total": int(event["alive_total"]),
                    "concurrent_limit": int(event["concurrent_limit"]),
                    "offered_color": str(event.get("offered_color") or ""),
                    "music_mode": str(event.get("music_mode") or "calm"),
                    "score": float(event.get("score") or 0.0),
                    "events": [],
                    "launch_flare_colors": [],
                }
                by_time[time_seconds] = row
                rows.append(row)

            row["alive_total"] = int(event["alive_total"])
            row["concurrent_limit"] = int(event["concurrent_limit"])
            row["offered_color"] = str(event.get("offered_color") or "")
            row["music_mode"] = str(event.get("music_mode") or row["music_mode"])
            event_score = event.get("score")
            if event_score is not None:
                row["score"] = float(event_score)

            event_type = str(event["type"])
            row["events"].append(event_type)

            payload = event.get("payload") or {}
            launch_color = payload.get("color") if isinstance(payload, dict) else None
            if event_type == "launch_flare" and launch_color:
                launch_color_text = str(launch_color)
                if launch_color_text not in row["launch_flare_colors"]:
                    row["launch_flare_colors"].append(launch_color_text)

        return rows

    def _write_match_events_txt(self, rows: List[Dict], output_txt_path: str) -> None:
        lines = [
            "### Output (stdout and stderr interleaved):",
            "",
            "```",
            "time | alive | limit | offered | launch_flare_colors | mode | score | events",
        ]

        for row in rows:
            launch_colors = ";".join(row["launch_flare_colors"]) if row["launch_flare_colors"] else "-"
            offered_color = row["offered_color"] or "-"
            events_text = ";".join(row["events"])
            lines.append(
                "{time_seconds:6.2f} | {alive_total:5d} | {concurrent_limit:5d} | {offered:>6} | "
                "{launch_colors:<18} | {mode:<7} | {score:5.3f} | {events}".format(
                    time_seconds=float(row["time_seconds"]),
                    alive_total=int(row["alive_total"]),
                    concurrent_limit=int(row["concurrent_limit"]),
                    offered=offered_color,
                    launch_colors=launch_colors,
                    mode=str(row["music_mode"]),
                    score=float(row["score"]),
                    events=events_text,
                )
            )

        lines.append("```")

        with open(output_txt_path, "w", encoding="utf-8", newline="\n") as output_file:
            output_file.write("\n".join(lines) + "\n")

    def _plot_match_summary_png(self, output_png_path: str) -> None:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        eval_times = [float(row["time_seconds"]) for row in self._match_music_eval_log]
        eval_scores = [float(row["score"]) for row in self._match_music_eval_log]
        eval_hand_norm = [float(row["colors_norm"]) for row in self._match_music_eval_log]
        eval_flares_norm = [float(row["flares_norm"]) for row in self._match_music_eval_log]
        eval_curses_norm = [float(row["curses_norm"]) for row in self._match_music_eval_log]

        figure, (axis_score, axis_components) = plt.subplots(
            2,
            1,
            figsize=(16, 10),
            sharex=True,
            gridspec_kw={"height_ratios": [3.0, 2.0]},
        )

        if eval_times:
            axis_score.plot(eval_times, eval_scores, color="#00695c", linewidth=2.0, label="intensity score")
        axis_score.axhline(
            self.INTENSITY_THRESHOLD_HIGH,
            color="#d32f2f",
            linestyle="--",
            linewidth=1.4,
            label="high threshold",
        )
        axis_score.axhline(
            self.INTENSITY_THRESHOLD_LOW,
            color="#1976d2",
            linestyle="--",
            linewidth=1.4,
            label="low threshold",
        )

        event_types = sorted({str(event["type"]) for event in self._match_event_log})
        if event_types:
            palette = plt.cm.get_cmap("tab20", max(1, len(event_types)))
            score_ceiling = max(
                [self.INTENSITY_THRESHOLD_HIGH, self.INTENSITY_THRESHOLD_LOW] + (eval_scores if eval_scores else [0.0])
            )
            base_y = score_ceiling + 0.15
            level_count = max(1, min(6, len(event_types)))

            for index, event_type in enumerate(event_types):
                event_times = [
                    float(event["time_seconds"])
                    for event in self._match_event_log
                    if str(event["type"]) == event_type
                ]
                level = index % level_count
                event_y = [base_y + (0.08 * float(level)) for _ in event_times]
                axis_score.scatter(
                    event_times,
                    event_y,
                    color=palette(index),
                    marker="|",
                    s=28,
                    linewidths=1.6,
                    alpha=0.95,
                    label=event_type,
                )

            axis_score.set_ylim(top=base_y + (0.08 * float(level_count)) + 0.15)

        axis_score.set_title("Flare Curse match log: score + all events")
        axis_score.set_ylabel("score")
        axis_score.grid(alpha=0.25)
        axis_score.legend(
            loc="upper left",
            bbox_to_anchor=(1.01, 1.0),
            borderaxespad=0.0,
            fontsize=7,
        )

        if eval_times:
            axis_components.plot(
                eval_times,
                eval_hand_norm,
                color="#1565c0",
                linewidth=1.7,
                marker="o",
                markersize=4,
                label="colors_in_hand_norm",
            )
            axis_components.plot(
                eval_times,
                eval_flares_norm,
                color="#2e7d32",
                linewidth=1.7,
                marker="o",
                markersize=4,
                label="recent_flares_norm",
            )
            axis_components.plot(
                eval_times,
                eval_curses_norm,
                color="#6a1b9a",
                linewidth=1.7,
                marker="o",
                markersize=4,
                label="recent_curses_norm",
            )
        else:
            axis_components.text(
                0.5,
                0.5,
                "No score evaluations captured",
                ha="center",
                va="center",
                transform=axis_components.transAxes,
            )

        axis_components.set_title("Values used on each score evaluation")
        axis_components.set_xlabel("time (seconds)")
        axis_components.set_ylabel("normalized value")
        axis_components.grid(alpha=0.25)
        if eval_times:
            axis_components.legend(
                loc="upper left",
                bbox_to_anchor=(1.01, 1.0),
                borderaxespad=0.0,
            )

        figure.tight_layout(rect=(0.0, 0.0, 0.78, 1.0))
        figure.savefig(output_png_path, dpi=150)
        plt.close(figure)

    def _write_match_artifacts_locked(self) -> None:
        if not self._match_event_log:
            return

        output_dir = self._match_log_directory_path()
        os.makedirs(output_dir, exist_ok=True)

        basename = self._match_log_basename
        if not basename:
            basename = "flare_curse_match_{}".format(datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S"))

        txt_path = os.path.join(output_dir, basename + ".txt")
        png_path = os.path.join(output_dir, basename + ".png")

        rows = self._build_match_event_rows_locked()
        self._write_match_events_txt(rows, txt_path)

        try:
            self._plot_match_summary_png(png_path)
            print("[FlareCurse] match artifact png: {}".format(png_path))
        except Exception as exc:
            print("[FlareCurse] could not generate match png: {}".format(exc))

        print("[FlareCurse] match artifact txt: {}".format(txt_path))

    def _concurrent_colors_limit_locked(self) -> int:
        alive_count = sum(1 for p in self._players.values() if p.alive)
        target_colors = self._configured_colors_for_alive_count(alive_count)
        return min(target_colors, len(self._active_colors))

    def _initial_total_colors(self, initial_alive_count: int) -> int:
        configured_initial = self._configured_initial_total_colors()
        if configured_initial is not None:
            return configured_initial

        target_colors = self._configured_colors_for_alive_count(initial_alive_count)
        return min(target_colors, len(self.COLORS))

    def _configured_initial_total_colors(self) -> Optional[int]:
        if self.INITIAL_TOTAL_COLORS is None:
            return None

        try:
            parsed_value = int(self.INITIAL_TOTAL_COLORS)
        except (TypeError, ValueError):
            return None

        return max(0, min(parsed_value, len(self.COLORS)))

    def _configured_colors_for_alive_count(self, alive_count: int) -> int:
        for min_alive, max_colors in self.COLOR_CONCURRENCY_RULES:
            if alive_count >= min_alive:
                return max_colors
        return 0

    def _build_ghost_leaderboard_locked(self) -> List[Dict]:
        rows = [
            {
                "name": name,
                "points": ghost.points,
                "color": ghost.color,
            }
            for name, ghost in self._ghosts.items()
        ]
        rows.sort(key=lambda row: (-row["points"], row["name"]))
        return rows

    def _seconds_left(self, now: float, future_ts: float) -> float:
        if future_ts <= 0:
            return 0.0
        return round(max(0.0, future_ts - now), 3)

    def _enqueue_color_ready_at_locked(
        self,
        queue: List[Tuple[float, int, str]],
        color: str,
        ready_at: float,
    ) -> None:
        self._release_order += 1
        insort(queue, (ready_at, self._release_order, color))

    def _broadcast_locked(self, payload: Dict) -> None:
        channel_layer = get_channel_layer()
        if channel_layer is None:
            return
        try:
            async_to_sync(channel_layer.group_send)(
                ROOM_GROUP_NAME,
                {
                    "type": "flare_curse_event",
                    "payload": payload,
                },
            )
        except Exception as exc:
            print("[FlareCurse] broadcast failed (recovered): {}".format(exc))

    def _send_to_player_locked(self, player_name: str, payload: Dict) -> None:
        channel_layer = get_channel_layer()
        if channel_layer is None:
            return
        try:
            async_to_sync(channel_layer.group_send)(
                get_player_group_name(player_name),
                {
                    "type": "flare_curse_event",
                    "payload": payload,
                },
            )
        except Exception as exc:
            print("[FlareCurse] private send failed for {} (recovered): {}".format(player_name, exc))


def sanitize_group_name(value: str) -> str:
    if value is None:
        return "anon"

    # Channels group names only allow ASCII alphanumerics plus - _ .
    ascii_value = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode("ascii").lower()

    normalized = []
    for ch in ascii_value:
        if ("a" <= ch <= "z") or ("0" <= ch <= "9") or ch in {"-", "_", "."}:
            normalized.append(ch)
        else:
            normalized.append("-")

    sanitized = "".join(normalized).strip("-")
    if not sanitized:
        sanitized = "anon"

    return sanitized[:60]


def get_player_group_name(player_name: str) -> str:
    return f"flare-curse-player-{sanitize_group_name(player_name)}"


flare_curse_engine = FlareCurseEngine()
