import argparse
import csv
import datetime
import os
import random
import sys
from collections import Counter, deque
from dataclasses import dataclass
from typing import Deque, Dict, Iterable, List, Optional, Sequence, Tuple
from unittest.mock import patch

import django
import matplotlib


matplotlib.use("Agg")
import matplotlib.pyplot as plt


CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "servidor_juegos.settings")
django.setup()

from servidor.games.flare_curse.flare_curse_engine import FlareCurseEngine


@dataclass(frozen=True)
class Scenario:
    name: str
    colors_in_hand: int
    recent_flares: int
    recent_curses: int
    concurrent_limit: Optional[int] = None


@dataclass(frozen=True)
class TimelineScenario:
    name: str
    delta_seconds: float
    colors_in_hand: int
    new_flares: int
    new_curses: int
    concurrent_limit: Optional[int] = None


@dataclass(frozen=True)
class MatchBehaviorConfig:
    claim_fast_probability: float
    claim_fast_delay_range: Tuple[float, float]
    claim_slow_delay_range: Tuple[float, float]
    launch_fast_weight: float
    launch_slow_weight: float
    launch_timeout_weight: float
    launch_fast_delay_range: Tuple[float, float]
    launch_slow_delay_range: Tuple[float, float]
    curse_after_launch_probability: float
    curse_fast_probability: float
    curse_fast_delay_range: Tuple[float, float]
    curse_slow_delay_range: Tuple[float, float]
    curse_back_fast_probability: float
    curse_back_fast_delay_range: Tuple[float, float]
    curse_ally_probability: float


@dataclass
class MatchSimulationResult:
    seed: int
    attempt: int
    ended: bool
    end_reason: str
    duration_seconds: float
    initial_concurrent_limit: int
    recent_event_reference: float
    winner_team: Optional[str]
    winner_players: List[str]
    winner_alive_count: int
    alive_circle: int
    alive_square: int
    timeline_rows: List[Dict[str, object]]
    event_counts: Dict[str, int]


def _safe_range(low: float, high: float) -> Tuple[float, float]:
    if low <= high:
        return low, high
    return high, low


def _sample_delay(rng: random.Random, delay_range: Tuple[float, float]) -> float:
    low, high = _safe_range(delay_range[0], delay_range[1])
    return rng.uniform(low, high)


def _derive_launch_slow_delay_range(hold_seconds: float) -> Tuple[float, float]:
    timeout_seconds = max(0.1, hold_seconds)
    slow_min = max(0.05, (timeout_seconds * 0.5) - 0.1)
    slow_max = max(0.05, timeout_seconds - 0.1)
    return _safe_range(slow_min, slow_max)


def _resolve_launch_slow_delay_range(args: argparse.Namespace) -> Tuple[float, float]:
    derived_min, derived_max = _derive_launch_slow_delay_range(args.hold_seconds)
    manual_min = args.launch_slow_min_seconds
    manual_max = args.launch_slow_max_seconds

    if args.launch_slow_derive_from_hold:
        resolved_min = derived_min if manual_min is None else manual_min
        resolved_max = derived_max if manual_max is None else manual_max
        return _safe_range(resolved_min, resolved_max)

    # Manual mode: both bounds must be provided explicitly.
    return _safe_range(manual_min, manual_max)


def _choose_launch_profile(rng: random.Random, behavior: MatchBehaviorConfig) -> str:
    fast = max(0.0, behavior.launch_fast_weight)
    slow = max(0.0, behavior.launch_slow_weight)
    timeout = max(0.0, behavior.launch_timeout_weight)
    total = fast + slow + timeout

    if total <= 0.0:
        return "timeout"

    roll = rng.random() * total
    if roll < fast:
        return "fast"
    if roll < fast + slow:
        return "slow"
    return "timeout"


def _bounded_launch_delay(raw_delay: float, hold_seconds: float) -> float:
    if hold_seconds <= 0.1:
        return 0.05

    max_safe_delay = max(0.05, hold_seconds - 0.05)
    return max(0.05, min(raw_delay, max_safe_delay))


def _build_match_players(total_players: int) -> List[str]:
    return ["P{:02d}".format(index) for index in range(1, total_players + 1)]


def _alive_team_counts(engine: FlareCurseEngine) -> Tuple[int, int]:
    circle = 0
    square = 0
    for player in engine._players.values():
        if not player.alive:
            continue
        if player.team == "circle":
            circle += 1
        elif player.team == "square":
            square += 1
    return circle, square


def _count_recent_window(events: Deque[float], now: float, cutoff_seconds: float) -> int:
    total = 0
    for event_ts in events:
        if now - event_ts <= cutoff_seconds:
            total += 1
    return total


def _score_components_for_now(engine: FlareCurseEngine, now: float) -> Dict[str, float]:
    concurrent_limit = engine._concurrent_colors_limit_locked()
    colors_in_hand = engine._count_colors_in_hand_locked()
    recent_flares = _count_recent_window(engine._recent_flare_timestamps, now, engine.INTENSITY_CUTOFF_SECONDS)
    recent_curses = _count_recent_window(engine._recent_curse_timestamps, now, engine.INTENSITY_CUTOFF_SECONDS)

    colors_norm = colors_in_hand_norm(colors_in_hand, concurrent_limit)
    flares_norm = engine._normalize_recent_event_count_locked(recent_flares)
    curses_norm = engine._normalize_recent_event_count_locked(recent_curses)

    weighted_hand = engine.WEIGHT_COLORS_IN_HAND * colors_norm
    weighted_flares = engine.WEIGHT_RECENT_FLARES * flares_norm
    weighted_curses = engine.WEIGHT_RECENT_CURSES * curses_norm
    score = weighted_hand + weighted_flares + weighted_curses

    return {
        "concurrent_limit": float(concurrent_limit),
        "colors_in_hand": float(colors_in_hand),
        "recent_flares": float(recent_flares),
        "recent_curses": float(recent_curses),
        "colors_norm": colors_norm,
        "flares_norm": flares_norm,
        "curses_norm": curses_norm,
        "weighted_hand": weighted_hand,
        "weighted_flares": weighted_flares,
        "weighted_curses": weighted_curses,
        "score": score,
    }


def _configure_engine_for_match(engine: FlareCurseEngine, args: argparse.Namespace) -> None:
    engine.WEIGHT_COLORS_IN_HAND = args.w_hand
    engine.WEIGHT_RECENT_FLARES = args.w_flares
    engine.WEIGHT_RECENT_CURSES = args.w_curses
    engine.INTENSITY_THRESHOLD_HIGH = args.high_threshold
    engine.INTENSITY_THRESHOLD_LOW = args.low_threshold
    engine.INTENSITY_CUTOFF_SECONDS = args.cutoff_seconds
    engine.MUSIC_EVAL_SECONDS = args.eval_seconds

    engine.HOLD_COLOR_SECONDS = args.hold_seconds
    engine.INITIAL_DELAY_SECONDS = args.initial_delay_seconds
    engine.RELEASE_GAP_RANGE_SECONDS = _safe_range(args.release_gap_min, args.release_gap_max)
    engine.USED_COLOR_COOLDOWN_RANGE_SECONDS = _safe_range(args.used_cooldown_min, args.used_cooldown_max)
    engine.GHOST_COOLDOWN_SECONDS = args.ghost_cooldown_seconds
    engine.GHOST_POST_FACE_GRACE_SECONDS = args.post_face_grace_seconds
    engine.INITIAL_TOTAL_COLORS = args.initial_total_colors


def _build_behavior_config(args: argparse.Namespace) -> MatchBehaviorConfig:
    launch_slow_delay_range = _resolve_launch_slow_delay_range(args)

    return MatchBehaviorConfig(
        claim_fast_probability=args.claim_fast_probability,
        claim_fast_delay_range=_safe_range(args.claim_fast_min_seconds, args.claim_fast_max_seconds),
        claim_slow_delay_range=_safe_range(args.claim_slow_min_seconds, args.claim_slow_max_seconds),
        launch_fast_weight=args.launch_fast_weight,
        launch_slow_weight=args.launch_slow_weight,
        launch_timeout_weight=args.launch_timeout_weight,
        launch_fast_delay_range=_safe_range(args.launch_fast_min_seconds, args.launch_fast_max_seconds),
        launch_slow_delay_range=launch_slow_delay_range,
        curse_after_launch_probability=args.curse_after_launch_probability,
        curse_fast_probability=args.curse_fast_probability,
        curse_fast_delay_range=_safe_range(args.curse_fast_min_seconds, args.curse_fast_max_seconds),
        curse_slow_delay_range=_safe_range(args.curse_slow_min_seconds, args.curse_slow_max_seconds),
        curse_back_fast_probability=args.curse_back_fast_probability,
        curse_back_fast_delay_range=_safe_range(args.curse_back_fast_min_seconds, args.curse_back_fast_max_seconds),
        curse_ally_probability=args.curse_ally_probability,
    )


def _attempt_curse(
    engine: FlareCurseEngine,
    origin_name: str,
    rng: random.Random,
    curse_ally_probability: float,
) -> Optional[Dict[str, str]]:
    origin = engine._players.get(origin_name)
    if origin is None or not origin.alive:
        return None

    alive_names = [name for name, player in engine._players.items() if player.alive and name != origin_name]
    if not alive_names:
        return None

    allies = [name for name in alive_names if engine._players[name].team == origin.team]
    enemies = [name for name in alive_names if engine._players[name].team != origin.team]

    choose_ally = rng.random() < curse_ally_probability
    if choose_ally and allies:
        target_name = rng.choice(allies)
    elif (not choose_ally) and enemies:
        target_name = rng.choice(enemies)
    elif enemies:
        target_name = rng.choice(enemies)
    elif allies:
        target_name = rng.choice(allies)
    else:
        return None

    accepted, victim_is_enemy, cursed_name = engine.cast_curse(origin_name, target_name)
    if not accepted or cursed_name is None:
        return None

    return {
        "type": "curse_enemy_hit" if victim_is_enemy else "curse_self_rebound",
        "origin": origin_name,
        "target": target_name,
        "cursed": cursed_name,
    }


def _attempt_curse_against_target(
    engine: FlareCurseEngine,
    target_name: str,
    rng: random.Random,
) -> Optional[Dict[str, str]]:
    target = engine._players.get(target_name)
    if target is None or not target.alive:
        return None

    enemy_attackers = [
        name
        for name, player in engine._players.items()
        if player.alive and name != target_name and player.team != target.team
    ]
    if not enemy_attackers:
        return None

    origin_name = rng.choice(enemy_attackers)
    accepted, victim_is_enemy, cursed_name = engine.cast_curse(origin_name, target_name)
    if not accepted or cursed_name is None:
        return None

    return {
        "type": "curse_enemy_hit" if victim_is_enemy else "curse_self_rebound",
        "origin": origin_name,
        "target": target_name,
        "cursed": cursed_name,
    }


def _validate_match_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.players < 2:
        parser.error("--players must be >= 2")
    if args.dt_seconds <= 0:
        parser.error("--dt-seconds must be > 0")
    if args.max_sim_seconds <= 0:
        parser.error("--max-sim-seconds must be > 0")
    if args.max_attempts <= 0:
        parser.error("--max-attempts must be > 0")

    if args.high_threshold < args.low_threshold:
        parser.error("--high-threshold must be >= --low-threshold")

    for probability_name in [
        "claim_fast_probability",
        "curse_after_launch_probability",
        "curse_fast_probability",
        "curse_back_fast_probability",
        "curse_ally_probability",
    ]:
        probability_value = getattr(args, probability_name)
        if not (0.0 <= probability_value <= 1.0):
            parser.error("--{} must be in [0, 1]".format(probability_name.replace("_", "-")))

    for range_name in [
        "hold_seconds",
        "initial_delay_seconds",
        "release_gap_min",
        "release_gap_max",
        "used_cooldown_min",
        "used_cooldown_max",
        "ghost_cooldown_seconds",
        "post_face_grace_seconds",
        "claim_fast_min_seconds",
        "claim_fast_max_seconds",
        "claim_slow_min_seconds",
        "claim_slow_max_seconds",
        "launch_fast_min_seconds",
        "launch_fast_max_seconds",
        "curse_fast_min_seconds",
        "curse_fast_max_seconds",
        "curse_slow_min_seconds",
        "curse_slow_max_seconds",
        "curse_back_fast_min_seconds",
        "curse_back_fast_max_seconds",
    ]:
        if getattr(args, range_name) < 0.0:
            parser.error("--{} must be >= 0".format(range_name.replace("_", "-")))

    for optional_range_name in [
        "launch_slow_min_seconds",
        "launch_slow_max_seconds",
    ]:
        optional_value = getattr(args, optional_range_name)
        if optional_value is not None and optional_value < 0.0:
            parser.error("--{} must be >= 0".format(optional_range_name.replace("_", "-")))

    if (not args.launch_slow_derive_from_hold) and (
        args.launch_slow_min_seconds is None or args.launch_slow_max_seconds is None
    ):
        parser.error(
            "When --no-launch-slow-derive-from-hold is used, set both --launch-slow-min-seconds and --launch-slow-max-seconds"
        )

    if args.initial_total_colors is not None and args.initial_total_colors < 0:
        parser.error("--initial-total-colors must be >= 0")

    total_launch_weight = args.launch_fast_weight + args.launch_slow_weight + args.launch_timeout_weight
    if total_launch_weight <= 0.0:
        parser.error("launch weights must add to a value > 0")


def _simulate_single_match(args: argparse.Namespace, seed: int, attempt: int) -> MatchSimulationResult:
    behavior = _build_behavior_config(args)
    policy_rng = random.Random(seed + 1000003)
    random.seed(seed)

    engine = FlareCurseEngine()
    _configure_engine_for_match(engine, args)

    player_names = _build_match_players(args.players)
    now = 0.0
    step = 0

    timeline_rows: List[Dict[str, object]] = []
    event_log: List[Dict[str, object]] = []
    pending_launch_at: Dict[str, float] = {}
    pending_curse_actions: List[Dict[str, object]] = []
    offer_plan: Optional[Dict[str, object]] = None

    def record_event(event_type: str, **payload) -> None:
        row = {
            "time_seconds": round(now, 3),
            "type": event_type,
        }
        row.update(payload)
        event_log.append(row)

    def capture_broadcast(payload: Dict) -> None:
        payload_type = payload.get("type")
        if payload_type == "DestelloDisponible":
            record_event("offer_opened", color=payload.get("color"))
        elif payload_type == "DestelloNoDisponible":
            record_event("offer_closed", color=payload.get("color"))
        elif payload_type == "MusicModeChanged":
            record_event("music_mode_changed", mode=payload.get("mode"), score=payload.get("score"))
        elif payload_type == "NuevoJugadorMaldito":
            record_event(
                "nuevo_jugador_maldito",
                player=payload.get("player"),
                team=payload.get("team"),
                ghost_color=payload.get("ghost_color"),
            )
        elif payload_type == "FinJuego":
            record_event("fin_juego_broadcast", winner_team=payload.get("winner_team"))

    def capture_private(player_name: str, payload: Dict) -> None:
        payload_type = payload.get("type")
        if payload_type == "TimeoutDestello":
            pending_launch_at.pop(player_name, None)
            record_event("timeout", player=player_name, color=payload.get("color"))

    engine._broadcast_locked = capture_broadcast
    engine._send_to_player_locked = capture_private

    with patch("servidor.games.flare_curse.flare_curse_engine.main_views.main_controller_.set_can_players_join"), patch(
        "servidor.games.flare_curse.flare_curse_engine.main_views.main_controller_.set_can_players_interact"
    ), patch("servidor.games.flare_curse.flare_curse_engine.time.monotonic", side_effect=lambda: now):
        engine._initialize_locked(player_names)
        initial_concurrent_limit = int(engine._initial_concurrent_limit_for_match)
        recent_event_reference = float(engine._event_concurrency_reference)

        while now <= args.max_sim_seconds and not engine._game_over:
            events_before = len(event_log)

            with engine._lock:
                engine._process_hand_timeouts_locked(now)
                engine._expire_faces_locked(now)
                engine._try_release_color_locked(now)

                if engine._offered_color is None:
                    offer_plan = None
                else:
                    if offer_plan is None or offer_plan.get("color") != engine._offered_color:
                        candidates = [
                            name
                            for name, player in engine._players.items()
                            if player.alive and player.hand_color is None
                        ]
                        if candidates:
                            chosen_player = policy_rng.choice(candidates)
                            use_fast_claim = policy_rng.random() < behavior.claim_fast_probability
                            if use_fast_claim:
                                delay = _sample_delay(policy_rng, behavior.claim_fast_delay_range)
                                claim_profile = "fast"
                            else:
                                delay = _sample_delay(policy_rng, behavior.claim_slow_delay_range)
                                claim_profile = "slow"

                            offer_plan = {
                                "color": engine._offered_color,
                                "claimer": chosen_player,
                                "claim_at": now + delay,
                            }
                            record_event(
                                "planned_claim_{}".format(claim_profile),
                                player=chosen_player,
                                color=engine._offered_color,
                                at_seconds=round(now + delay, 3),
                            )
                        else:
                            offer_plan = None

                if offer_plan is not None and now >= float(offer_plan["claim_at"]):
                    claimer = str(offer_plan["claimer"])
                    planned_color = str(offer_plan["color"])
                    claim_color = engine._offered_color

                    claimed = False
                    if claim_color == planned_color:
                        claimed = engine.claim_flare(claimer, claim_color)

                    if claimed:
                        record_event("claim", player=claimer, color=planned_color)
                        profile = _choose_launch_profile(policy_rng, behavior)
                        if profile == "timeout":
                            pending_launch_at.pop(claimer, None)
                            record_event("planned_timeout", player=claimer, color=planned_color)
                        else:
                            if profile == "fast":
                                raw_delay = _sample_delay(policy_rng, behavior.launch_fast_delay_range)
                            else:
                                raw_delay = _sample_delay(policy_rng, behavior.launch_slow_delay_range)

                            launch_delay = _bounded_launch_delay(raw_delay, engine.HOLD_COLOR_SECONDS)
                            launch_at = now + launch_delay
                            pending_launch_at[claimer] = launch_at
                            record_event(
                                "planned_launch_{}".format(profile),
                                player=claimer,
                                color=planned_color,
                                at_seconds=round(launch_at, 3),
                            )

                    offer_plan = None

                due_launchers = [player_name for player_name, launch_at in pending_launch_at.items() if now >= launch_at]
                for launcher_name in sorted(due_launchers):
                    pending_launch_at.pop(launcher_name, None)

                    launcher = engine._players.get(launcher_name)
                    if launcher is None or (not launcher.alive) or launcher.hand_color is None:
                        continue

                    launch_color = launcher.hand_color

                    launched = engine.launch_flare(launcher_name)
                    if not launched:
                        continue

                    record_event("launch_flare", player=launcher_name, color=launch_color)

                    if policy_rng.random() < behavior.curse_after_launch_probability:
                        curse_is_fast = policy_rng.random() < behavior.curse_fast_probability
                        curse_delay = _sample_delay(
                            policy_rng,
                            behavior.curse_fast_delay_range if curse_is_fast else behavior.curse_slow_delay_range,
                        )
                        curse_at = now + curse_delay
                        pending_curse_actions.append(
                            {
                                "kind": "normal",
                                "origin": launcher_name,
                                "at": curse_at,
                            }
                        )
                        record_event(
                            "planned_curse_{}".format("fast" if curse_is_fast else "slow"),
                            origin=launcher_name,
                            at_seconds=round(curse_at, 3),
                        )

                due_curse_actions = [action for action in pending_curse_actions if now >= float(action["at"])]
                pending_curse_actions = [action for action in pending_curse_actions if now < float(action["at"])]
                due_curse_actions.sort(key=lambda action: float(action["at"]))

                for action in due_curse_actions:
                    action_kind = str(action["kind"])

                    if action_kind == "normal":
                        origin_name = str(action["origin"])
                        curse_result = _attempt_curse(
                            engine=engine,
                            origin_name=origin_name,
                            rng=policy_rng,
                            curse_ally_probability=behavior.curse_ally_probability,
                        )
                        if curse_result is None:
                            continue

                        record_event(
                            str(curse_result["type"]),
                            origin=curse_result["origin"],
                            target=curse_result["target"],
                            cursed=curse_result["cursed"],
                        )
                        pending_launch_at.pop(str(curse_result["cursed"]), None)

                        origin_state = engine._players.get(origin_name)
                        if (
                            origin_state is not None
                            and origin_state.alive
                            and (policy_rng.random() < behavior.curse_back_fast_probability)
                        ):
                            retaliation_delay = _sample_delay(policy_rng, behavior.curse_back_fast_delay_range)
                            retaliation_at = now + retaliation_delay
                            pending_curse_actions.append(
                                {
                                    "kind": "back_fast",
                                    "target": origin_name,
                                    "at": retaliation_at,
                                }
                            )
                            record_event(
                                "planned_curse_back_fast",
                                target=origin_name,
                                at_seconds=round(retaliation_at, 3),
                            )

                    elif action_kind == "back_fast":
                        target_name = str(action["target"])
                        retaliation_result = _attempt_curse_against_target(
                            engine=engine,
                            target_name=target_name,
                            rng=policy_rng,
                        )
                        if retaliation_result is None:
                            continue

                        record_event(
                            str(retaliation_result["type"]),
                            origin=retaliation_result["origin"],
                            target=retaliation_result["target"],
                            cursed=retaliation_result["cursed"],
                            source="retaliation",
                        )
                        pending_launch_at.pop(str(retaliation_result["cursed"]), None)

                eval_before = engine._last_music_eval_at
                engine._evaluate_music_locked(now)
                evaluated = engine._last_music_eval_at != eval_before

                circle_alive, square_alive = _alive_team_counts(engine)
                score_data = _score_components_for_now(engine, now)

                events_since_last_tick = event_log[events_before:]
                events_this_tick = [event["type"] for event in events_since_last_tick]
                launch_flare_colors_this_tick = sorted(
                    {
                        str(event["color"])
                        for event in events_since_last_tick
                        if event["type"] == "launch_flare" and event.get("color")
                    }
                )
                timeline_rows.append(
                    {
                        "step": step,
                        "time_seconds": round(now, 3),
                        "evaluated": 1 if evaluated else 0,
                        "music_mode": engine._music_mode,
                        "intensity_score": round(score_data["score"], 6),
                        "colors_in_hand": int(score_data["colors_in_hand"]),
                        "concurrent_limit": int(score_data["concurrent_limit"]),
                        "recent_flares": int(score_data["recent_flares"]),
                        "recent_curses": int(score_data["recent_curses"]),
                        "colors_in_hand_norm": round(score_data["colors_norm"], 6),
                        "recent_flares_norm": round(score_data["flares_norm"], 6),
                        "recent_curses_norm": round(score_data["curses_norm"], 6),
                        "weighted_hand": round(score_data["weighted_hand"], 6),
                        "weighted_flares": round(score_data["weighted_flares"], 6),
                        "weighted_curses": round(score_data["weighted_curses"], 6),
                        "alive_total": circle_alive + square_alive,
                        "alive_circle": circle_alive,
                        "alive_square": square_alive,
                        "offered_color": engine._offered_color or "",
                        "launch_flare_colors": launch_flare_colors_this_tick,
                        "dominant_event": events_this_tick[0] if events_this_tick else "",
                        "events": sorted(set(events_this_tick)),
                    }
                )

            now = round(now + args.dt_seconds, 6)
            step += 1

    final_circle, final_square = _alive_team_counts(engine)
    duration_seconds = timeline_rows[-1]["time_seconds"] if timeline_rows else 0.0
    winner_alive_count = len(engine._winner_players)
    if winner_alive_count == 0:
        winner_alive_count = max(final_circle, final_square)

    event_counts = Counter(event["type"] for event in event_log)

    return MatchSimulationResult(
        seed=seed,
        attempt=attempt,
        ended=engine._game_over,
        end_reason="game_over" if engine._game_over else "max_sim_seconds_reached",
        duration_seconds=float(duration_seconds),
        initial_concurrent_limit=initial_concurrent_limit,
        recent_event_reference=recent_event_reference,
        winner_team=engine._winner_team,
        winner_players=list(engine._winner_players),
        winner_alive_count=winner_alive_count,
        alive_circle=final_circle,
        alive_square=final_square,
        timeline_rows=timeline_rows,
        event_counts=dict(event_counts),
    )


def _simulate_match_with_retries(
    args: argparse.Namespace,
) -> Tuple[MatchSimulationResult, List[Dict[str, object]], bool]:
    attempt_summaries: List[Dict[str, object]] = []
    chosen_result: Optional[MatchSimulationResult] = None

    for attempt in range(1, args.max_attempts + 1):
        seed = args.seed + ((attempt - 1) * 10007)
        result = _simulate_single_match(args, seed=seed, attempt=attempt)

        attempt_summaries.append(
            {
                "attempt": attempt,
                "seed": seed,
                "ended": result.ended,
                "duration_seconds": round(result.duration_seconds, 3),
                "winner_team": result.winner_team,
                "winner_alive_count": result.winner_alive_count,
                "alive_circle": result.alive_circle,
                "alive_square": result.alive_square,
                "end_reason": result.end_reason,
            }
        )

        if not args.require_single_survivor:
            chosen_result = result
            break

        if result.ended and result.winner_alive_count == 1:
            chosen_result = result
            break

    if chosen_result is None:
        chosen_result = result

    requirement_met = (not args.require_single_survivor) or (
        chosen_result.ended and chosen_result.winner_alive_count == 1
    )
    return chosen_result, attempt_summaries, requirement_met


def _write_match_csv(rows: Sequence[Dict[str, object]], output_csv_path: str) -> None:
    fieldnames = [
        "step",
        "time_seconds",
        "evaluated",
        "music_mode",
        "intensity_score",
        "colors_in_hand",
        "concurrent_limit",
        "recent_flares",
        "recent_curses",
        "colors_in_hand_norm",
        "recent_flares_norm",
        "recent_curses_norm",
        "weighted_hand",
        "weighted_flares",
        "weighted_curses",
        "alive_total",
        "alive_circle",
        "alive_square",
        "offered_color",
        "launch_flare_colors",
        "dominant_event",
        "events",
    ]

    with open(output_csv_path, "w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer_row = dict(row)
            writer_row["launch_flare_colors"] = ";".join(row.get("launch_flare_colors", []))
            writer_row["events"] = ";".join(row["events"])
            writer.writerow(writer_row)


def _write_match_events_context_output(rows: Sequence[Dict[str, object]], output_txt_path: str) -> None:
    lines = [
        "### Output (stdout and stderr interleaved):",
        "",
        "```",
        "time | alive | limit | offered | launch_flare_colors | mode | score | events",
    ]

    for row in rows:
        events = row.get("events", [])
        if not events:
            continue

        launch_flare_colors = row.get("launch_flare_colors", [])
        launch_flare_colors_text = ";".join(launch_flare_colors) if launch_flare_colors else "-"
        line = (
            "{time_seconds:6.2f} | {alive_total:5d} | {concurrent_limit:5d} | {offered_color:>6} | "
            "{launch_flare_colors:<18} | {music_mode:<7} | {intensity_score:5.3f} | {events}"
        ).format(
            time_seconds=float(row["time_seconds"]),
            alive_total=int(row["alive_total"]),
            concurrent_limit=int(row["concurrent_limit"]),
            offered_color=(row.get("offered_color") or "-"),
            launch_flare_colors=launch_flare_colors_text,
            music_mode=str(row["music_mode"]),
            intensity_score=float(row["intensity_score"]),
            events=";".join(events),
        )
        lines.append(line)

    lines.append("```")

    with open(output_txt_path, "w", encoding="utf-8", newline="\n") as output_file:
        output_file.write("\n".join(lines) + "\n")


def _plot_match_intensity(
    rows: Sequence[Dict[str, object]],
    output_png_path: str,
    high_threshold: float,
    low_threshold: float,
) -> None:
    if not rows:
        return

    times = [float(row["time_seconds"]) for row in rows]
    scores = [float(row["intensity_score"]) for row in rows]
    modes = [str(row["music_mode"]) for row in rows]

    evaluated_rows = [row for row in rows if int(row["evaluated"]) == 1]
    eval_times = [float(row["time_seconds"]) for row in evaluated_rows]
    eval_scores = [float(row["intensity_score"]) for row in evaluated_rows]
    eval_hand_norm = [float(row["colors_in_hand_norm"]) for row in evaluated_rows]
    eval_flares_norm = [float(row["recent_flares_norm"]) for row in evaluated_rows]
    eval_curses_norm = [float(row["recent_curses_norm"]) for row in evaluated_rows]

    figure, (axis_score, axis_components) = plt.subplots(
        2,
        1,
        figsize=(14, 9),
        sharex=True,
        gridspec_kw={"height_ratios": [3.0, 2.0]},
    )

    for index in range(1, len(rows)):
        if modes[index - 1] == "intense":
            axis_score.axvspan(times[index - 1], times[index], color="#ffcc80", alpha=0.18, linewidth=0)

    axis_score.plot(times, scores, color="#00695c", linewidth=2.0, label="intensity score")
    axis_score.axhline(high_threshold, color="#d32f2f", linestyle="--", linewidth=1.4, label="high threshold")
    axis_score.axhline(low_threshold, color="#1976d2", linestyle="--", linewidth=1.4, label="low threshold")

    if eval_times:
        axis_score.scatter(eval_times, eval_scores, color="#212121", s=22, alpha=0.85, label="score evaluation")

    markers = [
        ("launch_flare", "#1b5e20", "o", "launch flare"),
        ("timeout", "#f57f17", "s", "timeout"),
        ("curse_enemy_hit", "#b71c1c", "x", "curse enemy hit"),
        ("curse_self_rebound", "#4a148c", "D", "curse self rebound"),
    ]

    for event_type, color, marker, label in markers:
        event_points = [
            (float(row["time_seconds"]), float(row["intensity_score"]))
            for row in rows
            if event_type in row["events"]
        ]
        if not event_points:
            continue

        xs = [point[0] for point in event_points]
        ys = [point[1] for point in event_points]
        axis_score.scatter(xs, ys, color=color, marker=marker, s=28, alpha=0.85, label=label)

    axis_score.set_title("Flare Curse match intensity simulation")
    axis_score.set_ylabel("intensity score")
    axis_score.grid(alpha=0.25)
    axis_score.legend(
        loc="upper left",
        bbox_to_anchor=(1.01, 1.0),
        borderaxespad=0.0,
        ncol=1,
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
    axis_components.legend(
        loc="upper left",
        bbox_to_anchor=(1.01, 1.0),
        borderaxespad=0.0,
    )

    figure.tight_layout(rect=(0.0, 0.0, 0.78, 1.0))
    figure.savefig(output_png_path, dpi=150)
    plt.close(figure)


def _run_match_model(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    _validate_match_args(parser, args)

    launch_slow_delay_min, launch_slow_delay_max = _resolve_launch_slow_delay_range(args)

    result, attempt_summaries, requirement_met = _simulate_match_with_retries(args)

    os.makedirs(args.output_dir, exist_ok=True)
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_basename = "flare_curse_match_seed{}_attempt{}_{}".format(result.seed, result.attempt, timestamp)

    csv_path = os.path.join(args.output_dir, file_basename + ".csv")
    png_path = os.path.join(args.output_dir, file_basename + ".png")
    context_txt_path = os.path.join(args.output_dir, file_basename + "_context.txt")

    _write_match_csv(result.timeline_rows, csv_path)
    _write_match_events_context_output(result.timeline_rows, context_txt_path)
    _plot_match_intensity(
        rows=result.timeline_rows,
        output_png_path=png_path,
        high_threshold=args.high_threshold,
        low_threshold=args.low_threshold,
    )

    print("Flare Curse realistic match simulation")
    print("model: match")
    print("players: {}".format(args.players))
    print(
        "launch slow window: [{:.2f}, {:.2f}]s (mode={} hold={:.2f}s)".format(
            launch_slow_delay_min,
            launch_slow_delay_max,
            "derived" if args.launch_slow_derive_from_hold else "manual",
            args.hold_seconds,
        )
    )
    print(
        "recent event normalization: alpha={:.2f} reference={:.2f} (initial_concurrency={})".format(
            FlareCurseEngine.EVENT_CONCURRENCY_BLEND_ALPHA,
            result.recent_event_reference,
            result.initial_concurrent_limit,
        )
    )
    print("score evaluation cadence: every {:.2f}s".format(args.eval_seconds))
    print("attempts run: {} / {}".format(len(attempt_summaries), args.max_attempts))
    print("single survivor required: {} | met: {}".format(args.require_single_survivor, requirement_met))
    print(
        "selected attempt: {} | seed: {} | ended: {} | reason: {} | duration_s: {:.2f}".format(
            result.attempt,
            result.seed,
            result.ended,
            result.end_reason,
            result.duration_seconds,
        )
    )
    print(
        "winner_team: {} | winner_alive_count: {} | alive_circle: {} | alive_square: {}".format(
            result.winner_team,
            result.winner_alive_count,
            result.alive_circle,
            result.alive_square,
        )
    )
    print("rows written: {}".format(len(result.timeline_rows)))
    print("csv: {}".format(csv_path))
    print("context txt: {}".format(context_txt_path))
    print("png: {}".format(png_path))
    print()
    print("attempt summary:")
    for summary in attempt_summaries:
        print(
            "  attempt {attempt:02d} seed={seed} ended={ended} reason={end_reason} "
            "duration={duration_seconds:.2f}s winner={winner_team} winner_alive={winner_alive_count}".format(**summary)
        )

    print()
    print("event counts (selected attempt):")
    for event_name in sorted(result.event_counts.keys()):
        print("  {}: {}".format(event_name, result.event_counts[event_name]))


def parse_case(raw_case: str) -> Scenario:
    parts = [part.strip() for part in raw_case.split(",")]
    if len(parts) not in {4, 5}:
        raise argparse.ArgumentTypeError(
            "Invalid --case format. Use: name,colors_in_hand,recent_flares,recent_curses[,concurrent_limit]"
        )

    name = parts[0]
    try:
        colors_in_hand = int(parts[1])
        recent_flares = int(parts[2])
        recent_curses = int(parts[3])
        concurrent_limit = int(parts[4]) if len(parts) == 5 else None
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Scenario values must be integers") from exc

    if colors_in_hand < 0 or recent_flares < 0 or recent_curses < 0:
        raise argparse.ArgumentTypeError("Scenario values must be >= 0")
    if concurrent_limit is not None and concurrent_limit < 0:
        raise argparse.ArgumentTypeError("concurrent_limit must be >= 0")

    return Scenario(
        name=name,
        colors_in_hand=colors_in_hand,
        recent_flares=recent_flares,
        recent_curses=recent_curses,
        concurrent_limit=concurrent_limit,
    )


def parse_timeline_case(raw_case: str) -> TimelineScenario:
    parts = [part.strip() for part in raw_case.split(",")]
    if len(parts) not in {5, 6}:
        raise argparse.ArgumentTypeError(
            "Invalid --timeline-case format. Use: name,delta_seconds,colors_in_hand,new_flares,new_curses[,concurrent_limit]"
        )

    name = parts[0]
    try:
        delta_seconds = float(parts[1])
        colors_in_hand = int(parts[2])
        new_flares = int(parts[3])
        new_curses = int(parts[4])
        concurrent_limit = int(parts[5]) if len(parts) == 6 else None
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "Timeline values must be numeric (delta_seconds float, others int)"
        ) from exc

    if delta_seconds < 0:
        raise argparse.ArgumentTypeError("delta_seconds must be >= 0")
    if colors_in_hand < 0 or new_flares < 0 or new_curses < 0:
        raise argparse.ArgumentTypeError("Timeline values must be >= 0")
    if concurrent_limit is not None and concurrent_limit < 0:
        raise argparse.ArgumentTypeError("concurrent_limit must be >= 0")

    return TimelineScenario(
        name=name,
        delta_seconds=delta_seconds,
        colors_in_hand=colors_in_hand,
        new_flares=new_flares,
        new_curses=new_curses,
        concurrent_limit=concurrent_limit,
    )


def default_scenarios() -> List[Scenario]:
    return [
        Scenario("Opening calm", 0, 0, 0),
        Scenario("Small pressure", 1, 1, 0),
        Scenario("Mid pressure", 2, 1, 0),
        Scenario("Burst action", 2, 2, 0),
        Scenario("Curses spike", 1, 1, 2),
        Scenario("Falling down", 1, 0, 1),
        Scenario("Back to calm", 0, 0, 0),
    ]


def default_timeline_scenarios(eval_seconds: float) -> List[TimelineScenario]:
    # Defaults are spaced around the engine eval cadence to make transitions easier to reason about.
    return [
        TimelineScenario("Opening calm", eval_seconds, 0, 0, 0),
        TimelineScenario("Small pressure", eval_seconds, 1, 1, 0),
        TimelineScenario("Burst action", eval_seconds, 2, 2, 0),
        TimelineScenario("Sustained pace", eval_seconds, 2, 1, 0),
        TimelineScenario("Short lull", eval_seconds, 1, 0, 0),
        TimelineScenario("Long lull", eval_seconds * 3.0, 0, 0, 0),
        TimelineScenario("Curse spike", eval_seconds, 1, 1, 2),
        TimelineScenario("Cool down", eval_seconds * 2.0, 0, 0, 0),
    ]


def intensity_score(
    colors_in_hand_norm: float,
    recent_flares_norm: float,
    recent_curses_norm: float,
    w_hand: float,
    w_flares: float,
    w_curses: float,
) -> float:
    return (w_hand * colors_in_hand_norm) + (w_flares * recent_flares_norm) + (w_curses * recent_curses_norm)


def colors_in_hand_norm(colors_in_hand: int, concurrent_limit: int) -> float:
    if concurrent_limit <= 0:
        return 0.0
    return float(colors_in_hand) / float(concurrent_limit)


def derive_recent_event_reference(initial_concurrent_limit: int) -> float:
    if initial_concurrent_limit <= 0:
        return max(0.001, float(FlareCurseEngine.EVENT_CONCURRENCY_REFERENCE))
    return max(0.001, (float(initial_concurrent_limit) + 1.0) / 2.0)


def normalized_recent_event_count(
    recent_count: int,
    concurrent_limit: int,
    alpha: Optional[float] = None,
    reference: Optional[float] = None,
) -> float:
    if concurrent_limit <= 0:
        return 0.0

    if alpha is None:
        alpha = float(FlareCurseEngine.EVENT_CONCURRENCY_BLEND_ALPHA)
    if reference is None:
        reference = max(0.001, float(FlareCurseEngine.EVENT_CONCURRENCY_REFERENCE))

    alpha = max(0.0, min(1.0, float(alpha)))
    reference = max(0.001, float(reference))
    denominator = (alpha * float(concurrent_limit)) + ((1.0 - alpha) * reference)
    if denominator <= 0.0:
        return 0.0

    return float(recent_count) / denominator


def next_mode_hysteresis(current_mode: str, score: float, high: float, low: float) -> str:
    if current_mode == "calm" and score >= high:
        return "intense"
    if current_mode == "intense" and score <= low:
        return "calm"
    return current_mode


def next_mode_single_threshold(score: float, threshold: float) -> str:
    if score >= threshold:
        return "intense"
    return "calm"


def classify_zone(score: float, high: float, low: float) -> str:
    if score >= high:
        return "switch_up_zone"
    if score <= low:
        return "switch_down_zone"
    return "hysteresis_band"


def _add_timed_events(queue: Deque[float], start_time: float, end_time: float, count: int) -> None:
    if count <= 0:
        return

    if end_time <= start_time:
        for _ in range(count):
            queue.append(end_time)
        return

    spacing = (end_time - start_time) / float(count)
    for index in range(count):
        queue.append(start_time + spacing * float(index + 1))


def _trim_recent_events(queue: Deque[float], now: float, cutoff_seconds: float) -> None:
    while queue and (now - queue[0]) > cutoff_seconds:
        queue.popleft()


def _collect_rows(
    scenarios: Iterable[Scenario],
    start_mode: str,
    high: float,
    low: float,
    single_threshold: float,
    w_hand: float,
    w_flares: float,
    w_curses: float,
    default_concurrent_limit: int,
) -> List[List[str]]:
    rows: List[List[str]] = []
    mode_hysteresis = start_mode
    mode_single = start_mode
    recent_event_reference = derive_recent_event_reference(default_concurrent_limit)

    for index, scenario in enumerate(scenarios, start=1):
        concurrent_limit = default_concurrent_limit if scenario.concurrent_limit is None else scenario.concurrent_limit
        colors_norm = colors_in_hand_norm(scenario.colors_in_hand, concurrent_limit)
        recent_flares_norm = normalized_recent_event_count(
            scenario.recent_flares,
            concurrent_limit,
            reference=recent_event_reference,
        )
        recent_curses_norm = normalized_recent_event_count(
            scenario.recent_curses,
            concurrent_limit,
            reference=recent_event_reference,
        )
        score = intensity_score(
            colors_norm,
            recent_flares_norm,
            recent_curses_norm,
            w_hand,
            w_flares,
            w_curses,
        )

        next_hyst = next_mode_hysteresis(mode_hysteresis, score, high, low)
        next_single = next_mode_single_threshold(score, single_threshold)

        hyst_cell = next_hyst
        if next_hyst != mode_hysteresis:
            hyst_cell = "{}->{}".format(mode_hysteresis, next_hyst)

        single_cell = next_single
        if next_single != mode_single:
            single_cell = "{}->{}".format(mode_single, next_single)

        rows.append(
            [
                str(index),
                scenario.name,
                str(scenario.colors_in_hand),
                str(concurrent_limit),
                "{:.2f}".format(colors_norm),
                str(scenario.recent_flares),
                str(scenario.recent_curses),
                "{:.2f}".format(recent_flares_norm),
                "{:.2f}".format(recent_curses_norm),
                "{:.2f}".format(score),
                classify_zone(score, high, low),
                hyst_cell,
                single_cell,
            ]
        )

        mode_hysteresis = next_hyst
        mode_single = next_single

    return rows


def _collect_timeline_rows(
    scenarios: Iterable[TimelineScenario],
    start_mode: str,
    high: float,
    low: float,
    single_threshold: float,
    w_hand: float,
    w_flares: float,
    w_curses: float,
    cutoff_seconds: float,
    eval_seconds: float,
    ignore_eval_interval: bool,
    default_concurrent_limit: int,
) -> List[List[str]]:
    rows: List[List[str]] = []
    mode_hysteresis = start_mode
    mode_single = start_mode
    recent_event_reference = derive_recent_event_reference(default_concurrent_limit)
    flares: Deque[float] = deque()
    curses: Deque[float] = deque()
    now = 0.0
    last_eval_at = 0.0

    for index, scenario in enumerate(scenarios, start=1):
        step_start = now
        now = now + scenario.delta_seconds

        _add_timed_events(flares, step_start, now, scenario.new_flares)
        _add_timed_events(curses, step_start, now, scenario.new_curses)
        _trim_recent_events(flares, now, cutoff_seconds)
        _trim_recent_events(curses, now, cutoff_seconds)

        recent_flares = len(flares)
        recent_curses = len(curses)
        concurrent_limit = default_concurrent_limit if scenario.concurrent_limit is None else scenario.concurrent_limit
        colors_norm = colors_in_hand_norm(scenario.colors_in_hand, concurrent_limit)
        recent_flares_norm = normalized_recent_event_count(
            recent_flares,
            concurrent_limit,
            reference=recent_event_reference,
        )
        recent_curses_norm = normalized_recent_event_count(
            recent_curses,
            concurrent_limit,
            reference=recent_event_reference,
        )
        score = intensity_score(
            colors_norm,
            recent_flares_norm,
            recent_curses_norm,
            w_hand,
            w_flares,
            w_curses,
        )

        should_evaluate = ignore_eval_interval or (now - last_eval_at >= eval_seconds)
        if should_evaluate:
            next_hyst = next_mode_hysteresis(mode_hysteresis, score, high, low)
            next_single = next_mode_single_threshold(score, single_threshold)
            last_eval_at = now
            evaluated_cell = "yes"
        else:
            next_hyst = mode_hysteresis
            next_single = mode_single
            evaluated_cell = "no"

        hyst_cell = next_hyst
        if next_hyst != mode_hysteresis:
            hyst_cell = "{}->{}".format(mode_hysteresis, next_hyst)

        single_cell = next_single
        if next_single != mode_single:
            single_cell = "{}->{}".format(mode_single, next_single)

        rows.append(
            [
                str(index),
                scenario.name,
                "{:.2f}".format(scenario.delta_seconds),
                "{:.2f}".format(now),
                str(scenario.colors_in_hand),
                str(concurrent_limit),
                "{:.2f}".format(colors_norm),
                str(scenario.new_flares),
                str(scenario.new_curses),
                str(recent_flares),
                str(recent_curses),
                "{:.2f}".format(recent_flares_norm),
                "{:.2f}".format(recent_curses_norm),
                "{:.2f}".format(score),
                classify_zone(score, high, low),
                evaluated_cell,
                hyst_cell,
                single_cell,
            ]
        )

        mode_hysteresis = next_hyst
        mode_single = next_single

    return rows


def _print_table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> None:
    widths = [len(header) for header in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def format_row(cells: Sequence[str]) -> str:
        return " | ".join(cell.ljust(widths[i]) for i, cell in enumerate(cells))

    separator = "-+-".join("-" * width for width in widths)
    print(format_row(headers))
    print(separator)
    for row in rows:
        print(format_row(row))


def _count_transitions(mode_column_index: int, rows: Sequence[Sequence[str]]) -> int:
    transitions = 0
    for row in rows:
        if "->" in row[mode_column_index]:
            transitions += 1
    return transitions


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Explore Flare Curse music score behavior for match scenarios and compare "
            "dual-threshold hysteresis against a single-threshold policy, including "
            "recent-events cutoff effects."
        )
    )
    parser.add_argument(
        "--model",
        choices=["timeline", "snapshot", "match"],
        default="match",
        help=(
            "Scenario model: timeline computes recent flares/curses from event timestamps "
            "and cutoff window; snapshot uses direct counters per row; match runs a full "
            "engine-driven simulation with varied actions and exports CSV/PNG."
        ),
    )
    parser.add_argument(
        "--case",
        action="append",
        type=parse_case,
        help=(
            "Custom scenario: name,colors_in_hand,recent_flares,recent_curses[,concurrent_limit]. "
            "Repeat multiple times to build a sequence."
        ),
    )
    parser.add_argument(
        "--timeline-case",
        action="append",
        type=parse_timeline_case,
        help=(
            "Timeline scenario: name,delta_seconds,colors_in_hand,new_flares,new_curses[,concurrent_limit]. "
            "Repeat multiple times to build a sequence."
        ),
    )
    parser.add_argument(
        "--start-mode",
        choices=["calm", "intense"],
        default="calm",
        help="Initial music mode before first scenario.",
    )
    parser.add_argument(
        "--high-threshold",
        type=float,
        default=FlareCurseEngine.INTENSITY_THRESHOLD_HIGH,
        help="Hysteresis upper threshold used to switch from calm to intense.",
    )
    parser.add_argument(
        "--low-threshold",
        type=float,
        default=FlareCurseEngine.INTENSITY_THRESHOLD_LOW,
        help="Hysteresis lower threshold used to switch from intense to calm.",
    )
    parser.add_argument(
        "--single-threshold",
        type=float,
        default=(
            FlareCurseEngine.INTENSITY_THRESHOLD_HIGH + FlareCurseEngine.INTENSITY_THRESHOLD_LOW
        )
        / 2.0,
        help="Single-threshold comparator for alternate policy.",
    )
    parser.add_argument(
        "--w-hand",
        type=float,
        default=FlareCurseEngine.WEIGHT_COLORS_IN_HAND,
        help="Weight for colors_in_hand.",
    )
    parser.add_argument(
        "--w-flares",
        type=float,
        default=FlareCurseEngine.WEIGHT_RECENT_FLARES,
        help="Weight for recent_flares.",
    )
    parser.add_argument(
        "--w-curses",
        type=float,
        default=FlareCurseEngine.WEIGHT_RECENT_CURSES,
        help="Weight for recent_curses.",
    )
    parser.add_argument(
        "--default-concurrent-limit",
        type=int,
        default=2,
        help=(
            "Fallback concurrent colors limit used to normalize hand pressure when a scenario "
            "does not provide concurrent_limit."
        ),
    )
    parser.add_argument(
        "--cutoff-seconds",
        type=float,
        default=FlareCurseEngine.INTENSITY_CUTOFF_SECONDS,
        help="Window size to keep events as recent (timeline model).",
    )
    parser.add_argument(
        "--eval-seconds",
        type=float,
        default=FlareCurseEngine.MUSIC_EVAL_SECONDS,
        help="Engine music evaluation interval (timeline model).",
    )
    parser.add_argument(
        "--ignore-eval-interval",
        action="store_true",
        help="Evaluate mode decisions in every row, even when delta_seconds < eval_seconds.",
    )

    parser.add_argument(
        "--players",
        type=int,
        default=9,
        help="Total players for match simulation.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=20260411,
        help="Base random seed for deterministic match simulation.",
    )
    parser.add_argument(
        "--dt-seconds",
        type=float,
        default=0.25,
        help="Simulation tick size in seconds for match model.",
    )
    parser.add_argument(
        "--max-sim-seconds",
        type=float,
        default=600.0,
        help="Safety cap for match duration in seconds.",
    )
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=16,
        help="Maximum retry attempts with derived seeds.",
    )
    parser.add_argument(
        "--require-single-survivor",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=(
            "When enabled, retries until match ends with exactly one alive winner or max attempts is reached."
        ),
    )
    parser.add_argument(
        "--output-dir",
        default=os.path.join(CURRENT_DIR, "simulation_outputs"),
        help="Directory for match CSV and PNG artifacts.",
    )

    parser.add_argument(
        "--hold-seconds",
        type=float,
        default=FlareCurseEngine.HOLD_COLOR_SECONDS,
        help="Override HOLD_COLOR_SECONDS for match simulation.",
    )
    parser.add_argument(
        "--initial-delay-seconds",
        type=float,
        default=FlareCurseEngine.INITIAL_DELAY_SECONDS,
        help="Override INITIAL_DELAY_SECONDS for match simulation.",
    )
    parser.add_argument(
        "--release-gap-min",
        type=float,
        default=FlareCurseEngine.RELEASE_GAP_RANGE_SECONDS[0],
        help="Minimum release gap between offered colors.",
    )
    parser.add_argument(
        "--release-gap-max",
        type=float,
        default=FlareCurseEngine.RELEASE_GAP_RANGE_SECONDS[1],
        help="Maximum release gap between offered colors.",
    )
    parser.add_argument(
        "--used-cooldown-min",
        type=float,
        default=FlareCurseEngine.USED_COLOR_COOLDOWN_RANGE_SECONDS[0],
        help="Minimum cooldown for colors sent to used queue.",
    )
    parser.add_argument(
        "--used-cooldown-max",
        type=float,
        default=FlareCurseEngine.USED_COLOR_COOLDOWN_RANGE_SECONDS[1],
        help="Maximum cooldown for colors sent to used queue.",
    )
    parser.add_argument(
        "--ghost-cooldown-seconds",
        type=float,
        default=FlareCurseEngine.GHOST_COOLDOWN_SECONDS,
        help="Override ghost flare cooldown for match simulation.",
    )
    parser.add_argument(
        "--post-face-grace-seconds",
        type=float,
        default=FlareCurseEngine.GHOST_POST_FACE_GRACE_SECONDS,
        help="Override grace window for ghost chain validation.",
    )
    parser.add_argument(
        "--initial-total-colors",
        type=int,
        default=FlareCurseEngine.INITIAL_TOTAL_COLORS,
        help="Override INITIAL_TOTAL_COLORS (default None keeps current engine behavior).",
    )

    parser.add_argument(
        "--claim-fast-probability",
        type=float,
        default=0.72,
        help="Probability of assigning a fast claim delay when a color is offered.",
    )
    parser.add_argument(
        "--claim-fast-min-seconds",
        type=float,
        default=0.25,
        help="Minimum seconds for fast claim delays.",
    )
    parser.add_argument(
        "--claim-fast-max-seconds",
        type=float,
        default=1.10,
        help="Maximum seconds for fast claim delays.",
    )
    parser.add_argument(
        "--claim-slow-min-seconds",
        type=float,
        default=1.20,
        help="Minimum seconds for slow claim delays.",
    )
    parser.add_argument(
        "--claim-slow-max-seconds",
        type=float,
        default=3.80,
        help="Maximum seconds for slow claim delays.",
    )

    parser.add_argument(
        "--launch-fast-weight",
        type=float,
        default=0.55,
        help="Weight of fast launch behavior after a claim.",
    )
    parser.add_argument(
        "--launch-slow-weight",
        type=float,
        default=0.30,
        help="Weight of slow launch behavior after a claim.",
    )
    parser.add_argument(
        "--launch-timeout-weight",
        type=float,
        default=0.15,
        help="Weight of intentional timeout behavior after a claim.",
    )
    parser.add_argument(
        "--launch-fast-min-seconds",
        type=float,
        default=0.15,
        help="Minimum delay for fast launches (manual absolute value).",
    )
    parser.add_argument(
        "--launch-fast-max-seconds",
        type=float,
        default=1.30,
        help="Maximum delay for fast launches (manual absolute value).",
    )
    parser.add_argument(
        "--launch-slow-derive-from-hold",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=(
            "Derive slow launch delay bounds from hold_seconds as min=hold/2-0.1 and max=hold-0.1. "
            "In derived mode, manual min/max (if provided) override each bound individually."
        ),
    )
    parser.add_argument(
        "--launch-slow-min-seconds",
        type=float,
        default=None,
        help=(
            "Manual minimum delay for slow launches. "
            "Used as override in derived mode or required in manual mode."
        ),
    )
    parser.add_argument(
        "--launch-slow-max-seconds",
        type=float,
        default=None,
        help=(
            "Manual maximum delay for slow launches. "
            "Used as override in derived mode or required in manual mode."
        ),
    )

    parser.add_argument(
        "--curse-after-launch-probability",
        type=float,
        default=0.38,
        help="Probability of scheduling a curse attempt after a successful flare launch.",
    )
    parser.add_argument(
        "--curse-fast-probability",
        type=float,
        default=0.65,
        help="Probability that a scheduled curse uses fast timing (else slow timing).",
    )
    parser.add_argument(
        "--curse-fast-min-seconds",
        type=float,
        default=0.20,
        help="Minimum delay for fast curse timing.",
    )
    parser.add_argument(
        "--curse-fast-max-seconds",
        type=float,
        default=1.20,
        help="Maximum delay for fast curse timing.",
    )
    parser.add_argument(
        "--curse-slow-min-seconds",
        type=float,
        default=1.30,
        help="Minimum delay for slow curse timing.",
    )
    parser.add_argument(
        "--curse-slow-max-seconds",
        type=float,
        default=9.80,
        help="Maximum delay for slow curse timing.",
    )
    parser.add_argument(
        "--curse-back-fast-probability",
        type=float,
        default=0.35,
        help="Probability of scheduling a fast retaliation curse against the original curser.",
    )
    parser.add_argument(
        "--curse-back-fast-min-seconds",
        type=float,
        default=0.25,
        help="Minimum delay for fast retaliation curse timing.",
    )
    parser.add_argument(
        "--curse-back-fast-max-seconds",
        type=float,
        default=1.20,
        help="Maximum delay for fast retaliation curse timing.",
    )
    parser.add_argument(
        "--curse-ally-probability",
        type=float,
        default=0.27,
        help="Probability of selecting an ally target to force occasional rebound outcomes.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.high_threshold < args.low_threshold:
        parser.error("--high-threshold must be >= --low-threshold")
    if args.default_concurrent_limit < 0:
        parser.error("--default-concurrent-limit must be >= 0")
    if args.cutoff_seconds < 0:
        parser.error("--cutoff-seconds must be >= 0")
    if args.eval_seconds <= 0:
        parser.error("--eval-seconds must be > 0")

    if args.model == "match":
        _run_match_model(parser, args)
        return

    if args.model == "snapshot":
        scenarios = args.case if args.case else default_scenarios()
        rows = _collect_rows(
            scenarios=scenarios,
            start_mode=args.start_mode,
            high=args.high_threshold,
            low=args.low_threshold,
            single_threshold=args.single_threshold,
            w_hand=args.w_hand,
            w_flares=args.w_flares,
            w_curses=args.w_curses,
            default_concurrent_limit=args.default_concurrent_limit,
        )
    else:
        scenarios = args.timeline_case if args.timeline_case else default_timeline_scenarios(args.eval_seconds)
        rows = _collect_timeline_rows(
            scenarios=scenarios,
            start_mode=args.start_mode,
            high=args.high_threshold,
            low=args.low_threshold,
            single_threshold=args.single_threshold,
            w_hand=args.w_hand,
            w_flares=args.w_flares,
            w_curses=args.w_curses,
            cutoff_seconds=args.cutoff_seconds,
            eval_seconds=args.eval_seconds,
            ignore_eval_interval=args.ignore_eval_interval,
            default_concurrent_limit=args.default_concurrent_limit,
        )

    print("Flare Curse music score explorer")
    print(
        "score = ({:.2f} * colors_in_hand_norm) + ({:.2f} * recent_flares_norm) + ({:.2f} * recent_curses_norm)".format(
            args.w_hand,
            args.w_flares,
            args.w_curses,
        )
    )
    derived_reference = derive_recent_event_reference(args.default_concurrent_limit)
    print("colors_in_hand_norm = colors_in_hand / concurrent_limit")
    print("recent_*_norm = recent_* / (alpha * concurrent_limit + (1 - alpha) * reference)")
    print(
        "recent event normalization: alpha={:.2f} reference={:.2f}".format(
            FlareCurseEngine.EVENT_CONCURRENCY_BLEND_ALPHA,
            derived_reference,
        )
    )
    print("default concurrent_limit: {}".format(args.default_concurrent_limit))
    print(
        "hysteresis thresholds: high={:.2f} low={:.2f} | single threshold={:.2f}".format(
            args.high_threshold,
            args.low_threshold,
            args.single_threshold,
        )
    )
    print("start mode: {}".format(args.start_mode))
    print("model: {}".format(args.model))
    if args.model == "timeline":
        print(
            "cutoff_seconds={:.2f} | eval_seconds={:.2f} | ignore_eval_interval={}".format(
                args.cutoff_seconds,
                args.eval_seconds,
                args.ignore_eval_interval,
            )
        )
        print("recent_flares/recent_curses are derived from event timestamps inside the cutoff window")
    print()

    if args.model == "snapshot":
        headers = [
            "step",
            "scenario",
            "in_hand",
            "limit",
            "colors_in_hand_norm",
            "flares",
            "curses",
            "flares_norm",
            "curses_norm",
            "score",
            "zone",
            "mode_hysteresis",
            "mode_single",
        ]
        hyst_col = 11
        single_col = 12
    else:
        headers = [
            "step",
            "scenario",
            "dt_s",
            "t_s",
            "in_hand",
            "limit",
            "colors_in_hand_norm",
            "new_flares",
            "new_curses",
            "recent_flares",
            "recent_curses",
            "flares_norm",
            "curses_norm",
            "score",
            "zone",
            "evaluated",
            "mode_hysteresis",
            "mode_single",
        ]
        hyst_col = 16
        single_col = 17

    _print_table(headers, rows)
    print()
    print("transitions (less is stabler):")
    print("hysteresis: {}".format(_count_transitions(hyst_col, rows)))
    print("single threshold: {}".format(_count_transitions(single_col, rows)))


if __name__ == "__main__":
    main()