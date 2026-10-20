# Flare Curse Backlog

- Pending hardening: avoid player private-channel collisions caused by name sanitization (get_player_group_name). Move to stable unique identity (player id) for group naming.
- Pending performance/concurrency hardening: remove channel sends from the critical lock path using an outbound queue flushed outside the lock.
- Pending ordering hardening for out-of-lock sends: enforce deterministic order with event_seq plus single dispatcher, or add client stale-event guards.
- Pending player-client guard: prevent stale DestelloNoDisponible from closing a newly opened offer of the same color (offer_id/version).
- Pending host-client guard: ignore late MusicModeChanged after FinJuego is processed.
- Pending security hardening in consumer: do not trust player identity from query string alone; bind websocket identity to authenticated session/user.
- Pending transport hardening in frontend: build websocket URL with ws/wss based on window.location.protocol to avoid mixed-content failures.
- Pending consumer connection lifecycle hardening: avoid joining groups/accepting socket before readiness checks pass, and close connection when game is not ready.
- Pending consumer error-flow hardening: on internal startup/snapshot failures, ensure stale room subscriptions are not kept alive.
