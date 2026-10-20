let fc_socket = null;
let fc_player_name = null;
let fc_redirecting = false;
let fc_players_fit_timer = null;
let fc_flash_overlay_timer_id = null;
let fc_flash_overlay_is_visible = false;

const FC_COLORS = {
    red:    "#FF2D55",  // rojo vibrante, bien reconocible
    green:  "#0DFF72",  // verde neón pero sin ser agresivo
    blue:   "#00B4FF",  // cyan brillante, mucho mejor que el azul puro
    purple: "#CC00FF",  // violeta intenso, muy emisivo
    orange: "#FF8000",  // naranja eléctrico equilibrado
    gray: "#9E9E9E",
};

const fc_state = {
    role: "alive",
    team_symbol: null,
    offered_color: null,
    hand_color: null,
    hand_expires_at_ms: 0,
    hand_total_ms: 7000,
    ghost_color: null,
    ghost_points: 0,
    ghost_cooldown_expires_at_ms: 0,
    ghost_cooldown_total_ms: 9000,
    players: [],
    randomized_player_order: [],
    game_over: false,
    music_mode: "calm",
    face_flash_expires_at_ms: 0,
};

function is_face_flash_block_active() {
    return Date.now() < fc_state.face_flash_expires_at_ms;
}

function release_face_flash_block_if_expired() {
    if (is_face_flash_block_active() || !fc_flash_overlay_is_visible) {
        return;
    }

    const overlay = document.getElementById("flash-overlay");
    if (overlay) {
        overlay.style.opacity = "0";
        overlay.style.pointerEvents = "none";
    }

    fc_flash_overlay_is_visible = false;
    render_all();
}

function init_flare_curse_player() {
    fc_player_name = sessionStorage.getItem("player_name");
    if (!fc_player_name) {
        window.location.href = "../";
        return;
    }

    document.getElementById("flare-button").addEventListener("click", on_flare_button_click);
    document.getElementById("ghost-flare-button").addEventListener("click", on_ghost_button_click);
    window.addEventListener("resize", schedule_players_grid_fit);
    window.addEventListener("orientationchange", schedule_players_grid_fit);

    connect_flare_curse_socket();
    window.setInterval(update_timers_ui, 100);
}

function connect_flare_curse_socket() {
    const socket_url = `ws://${window.location.host}/ws/flare_curse_room/?name=${encodeURIComponent(fc_player_name)}`;
    fc_socket = new WebSocket(socket_url);

    fc_socket.onopen = function () {
        send_fc_action("GetJugadores", {});
    };

    fc_socket.onmessage = function (event) {
        const data = JSON.parse(event.data);
        handle_fc_message(data);
    };

    fc_socket.onclose = function () {
        if (!fc_redirecting) {
            window.setTimeout(connect_flare_curse_socket, 1500);
        }
    };
}

function handle_fc_message(data) {
    const type = data.type;

    if (type === "Error") {
        show_result_message(data.message || "Error inesperado del servidor.");
        return;
    }

    if (type === "GameSnapshot") {
        apply_snapshot(data);
        return;
    }

    if (type === "PedirDestelloResult") {
        if (!data.accepted) {
            show_result_message("No has conseguido ese destello.");
        }
        return;
    }

    if (type === "LanzarDestelloResult") {
        if (!data.accepted) {
            show_result_message("No puedes lanzar destello ahora.");
        }
        return;
    }

    if (type === "LanzarDestelloFantasmaResult") {
        fc_state.ghost_points = data.points || fc_state.ghost_points;
        const cooldown_ms = seconds_to_ms(data.cooldown_seconds, fc_state.ghost_cooldown_total_ms);
        fc_state.ghost_cooldown_total_ms = cooldown_ms;
        fc_state.ghost_cooldown_expires_at_ms = Date.now() + cooldown_ms;
        animate_ghost_points_feedback(Boolean(data.in_time));
        render_ghost_controls();
        return;
    }

    if (type === "MaldecirResult") {
        if (!data.accepted) {
            show_result_message("Maldicion no valida en este momento.");
        }
        return;
    }

    if (type === "DestelloDisponible") {
        if (fc_state.role === "alive" && !fc_state.hand_color && !fc_state.game_over) {
            fc_state.offered_color = data.color;
            render_alive_controls();
        }
        return;
    }

    if (type === "DestelloNoDisponible") {
        if (fc_state.offered_color === data.color) {
            fc_state.offered_color = null;
            render_alive_controls();
        }
        return;
    }

    if (type === "TeHanLanzadoDestello") {
        if (data.player === fc_player_name) {
            show_flash_overlay(data.color, data.duration_seconds);
        }
        return;
    }

    if (type === "TimeoutDestello") {
        if (data.player === fc_player_name) {
            fc_state.hand_color = null;
            fc_state.hand_expires_at_ms = 0;
            render_alive_controls();
        }
        return;
    }

    if (type === "NuevoJugadorMaldito") {
        mark_player_as_ghost_in_table(data.player, data.team);
        if (data.player === fc_player_name) {
            fc_state.role = "ghost";
            fc_state.hand_color = null;
            fc_state.hand_expires_at_ms = 0;
            fc_state.ghost_color = data.ghost_color || fc_state.ghost_color;
            fc_state.ghost_points = 0;
            fc_state.ghost_cooldown_expires_at_ms = 0;
        }
        render_all();
        return;
    }

    if (type === "MusicModeChanged") {
        fc_state.music_mode = data.mode;
        return;
    }

    if (type === "FinJuego") {
        fc_state.game_over = true;
        show_final_result(data);
        render_all();
        return;
    }

    if (type === "GoToWaitRoom") {
        fc_redirecting = true;
        sessionStorage.setItem("played", true);
        window.location.href = "../wait_room/";
        return;
    }
}

function apply_snapshot(snapshot) {
    const now_ms = Date.now();
    const timings = snapshot.timings || {};

    fc_state.role = snapshot.you.role;
    fc_state.team_symbol = snapshot.you.team_symbol;
    fc_state.offered_color = snapshot.offered_color;
    fc_state.hand_total_ms = seconds_to_ms(timings.hold_color_seconds, fc_state.hand_total_ms);
    fc_state.ghost_cooldown_total_ms = seconds_to_ms(timings.ghost_cooldown_seconds, fc_state.ghost_cooldown_total_ms);
    fc_state.hand_color = snapshot.you.hand_color;
    fc_state.hand_expires_at_ms = now_ms + (snapshot.you.hand_seconds_left || 0) * 1000;
    fc_state.ghost_color = snapshot.you.ghost_color;
    fc_state.ghost_points = snapshot.you.ghost_points || 0;
    fc_state.ghost_cooldown_expires_at_ms = now_ms + (snapshot.you.ghost_cooldown_seconds_left || 0) * 1000;
    fc_state.players = snapshot.players || [];
    sync_randomized_player_order();
    fc_state.game_over = Boolean(snapshot.game_over);
    fc_state.music_mode = snapshot.music_mode || "calm";

    render_all();
}

function on_flare_button_click() {
    if (fc_state.game_over || fc_state.role !== "alive" || is_face_flash_block_active()) {
        return;
    }

    if (fc_state.hand_color) {
        send_fc_action("LanzarDestello", {});
        return;
    }

    if (fc_state.offered_color) {
        send_fc_action("PedirDestello", { color: fc_state.offered_color });
    }
}

function on_ghost_button_click() {
    if (fc_state.game_over || fc_state.role !== "ghost" || is_face_flash_block_active()) {
        return;
    }

    if (Date.now() < fc_state.ghost_cooldown_expires_at_ms) {
        return;
    }

    send_fc_action("LanzarDestelloFantasma", {});
}

function send_fc_action(action, payload) {
    if (!fc_socket || fc_socket.readyState !== WebSocket.OPEN) {
        return;
    }

    const message = Object.assign({ action: action }, payload || {});
    fc_socket.send(JSON.stringify(message));
}

function render_all() {
    render_layout_mode();
    render_team_box();
    render_alive_controls();
    render_ghost_controls();
    render_players_table();
}

function render_layout_mode() {
    const header_card = document.getElementById("alive-header-card");
    if (!header_card) {
        return;
    }

    header_card.style.display = fc_state.role === "ghost" ? "none" : "flex";
}

function render_team_box() {
    const team_box = document.getElementById("team-box");
    team_box.classList.remove("fc-team-circle", "fc-team-square", "fc-team-ghost-initial", "fc-team-unknown");
    const shape_class = team_symbol_to_reveal_shape_class(fc_state.team_symbol);
    team_box.classList.add(shape_class || "fc-team-unknown");
}

function render_alive_controls() {
    const alive_header_controls = document.getElementById("alive-header-controls");
    const button = document.getElementById("flare-button");
    const flash_blocked = is_face_flash_block_active();

    if (fc_state.role !== "alive") {
        alive_header_controls.style.display = "none";
        return;
    }

    alive_header_controls.style.display = "grid";

    button.classList.remove("fc-state-idle", "fc-state-offered", "fc-state-held");
    button.style.background = FC_COLORS.gray;
    button.textContent = "";
    button.disabled = false;
    button.setAttribute("aria-label", "flare idle");

    if (fc_state.hand_color) {
        button.classList.add("fc-state-held");
        button.style.background = color_to_hex(fc_state.hand_color);
        button.setAttribute("aria-label", "flare launch");
        button.disabled = fc_state.game_over || flash_blocked;
        return;
    }

    if (fc_state.offered_color) {
        button.classList.add("fc-state-offered");
        button.style.background = color_to_hex(fc_state.offered_color);
        button.setAttribute("aria-label", "flare claim");
        button.disabled = fc_state.game_over || flash_blocked;
        return;
    }

    button.classList.add("fc-state-idle");
    button.disabled = true;
}

function render_ghost_controls() {
    const ghost_panel = document.getElementById("ghost-panel");
    const ghost_button = document.getElementById("ghost-flare-button");
    const ghost_points = document.getElementById("ghost-points-text");

    if (fc_state.role !== "ghost") {
        ghost_panel.style.display = "none";
        return;
    }

    ghost_panel.style.display = "block";
    ghost_points.textContent = `${fc_state.ghost_points}`;

    const ready_to_fire = !fc_state.game_over
        && !is_face_flash_block_active()
        && Date.now() >= fc_state.ghost_cooldown_expires_at_ms;
    ghost_button.disabled = !ready_to_fire;
    ghost_button.style.background = ready_to_fire
        ? color_to_hex(fc_state.ghost_color || "gray")
        : FC_COLORS.gray;
    ghost_button.style.color = ready_to_fire ? "#fff" : "#efefef";
}

function animate_ghost_points_feedback(in_time) {
    const points_badge = document.getElementById("ghost-points-text");
    if (!points_badge) {
        return;
    }

    const class_name = in_time ? "fc-ghost-points-glow" : "fc-ghost-points-vibrate";
    points_badge.classList.remove("fc-ghost-points-glow", "fc-ghost-points-vibrate");

    if (in_time) {
        points_badge.style.setProperty("--fc-ghost-accent", color_to_hex(fc_state.ghost_color || "gray"));
    }

    void points_badge.offsetWidth;
    points_badge.classList.add(class_name);
    points_badge.addEventListener(
        "animationend",
        function cleanup_points_feedback() {
            points_badge.classList.remove(class_name);
        },
        { once: true }
    );
}

function render_players_table() {
    const players_panel = document.getElementById("players-panel");
    const container = document.getElementById("players-container");

    if (fc_state.role === "ghost") {
        players_panel.style.display = "none";
        container.innerHTML = "";
        reset_players_grid_layout(container);
        return;
    }

    players_panel.style.display = "block";
    container.innerHTML = "";

    const order_index = new Map(fc_state.randomized_player_order.map(function (name, index) {
        return [name, index];
    }));

    const others = fc_state.players
        .filter(function (p) {
            return p.name !== fc_player_name;
        })
        .slice()
        .sort(function (a, b) {
            const a_index = order_index.has(a.name) ? order_index.get(a.name) : Number.MAX_SAFE_INTEGER;
            const b_index = order_index.has(b.name) ? order_index.get(b.name) : Number.MAX_SAFE_INTEGER;
            return a_index - b_index;
        });

    for (const player of others) {
        const button = document.createElement("button");
        button.className = "fc-player-button";
        const name_badge = document.createElement("span");
        name_badge.className = "fc-player-name-badge";
        name_badge.textContent = player.name;

        if (player.status === "ghost") {
            button.classList.add("fc-player-revealed");
            const reveal_shape_class = team_symbol_to_reveal_shape_class(player.team_symbol);
            if (reveal_shape_class) {
                name_badge.classList.add(reveal_shape_class);
            }
            button.disabled = true;
        } else {
            button.classList.add("fc-player-hidden");
            button.disabled = fc_state.game_over || fc_state.role !== "alive" || is_face_flash_block_active();
            button.addEventListener("click", function () {
                if (is_face_flash_block_active()) {
                    return;
                }
                send_fc_action("Maldecir", { target: player.name });
            });
        }

        button.appendChild(name_badge);
        container.appendChild(button);
    }

    schedule_players_grid_fit();
}

function schedule_players_grid_fit() {
    if (fc_players_fit_timer !== null) {
        window.clearTimeout(fc_players_fit_timer);
    }

    fc_players_fit_timer = window.setTimeout(function () {
        fc_players_fit_timer = null;
        fit_players_grid_to_container();
    }, 0);
}

function reset_players_grid_layout(container) {
    if (!container) {
        return;
    }

    container.style.removeProperty("grid-template-columns");
    container.style.removeProperty("grid-auto-rows");
    container.style.removeProperty("--fc-player-cell-size");
    container.style.removeProperty("--fc-player-font-size");
    container.style.removeProperty("--fc-player-button-padding");
    container.style.removeProperty("--fc-player-badge-padding");
    container.style.removeProperty("--fc-player-badge-border-width");
    container.style.removeProperty("--fc-player-ghost-outline-inset");
    container.style.removeProperty("--fc-player-ghost-x-offset");
}

function fit_players_grid_to_container() {
    const players_panel = document.getElementById("players-panel");
    const container = document.getElementById("players-container");

    if (!players_panel || !container || players_panel.style.display === "none") {
        return;
    }

    const item_count = container.children.length;
    if (item_count <= 0) {
        reset_players_grid_layout(container);
        return;
    }

    const width = Math.floor(container.clientWidth);
    const height = Math.floor(container.clientHeight);

    if (width <= 0 || height <= 0) {
        return;
    }

    const styles = window.getComputedStyle(container);
    const gap_x = parseFloat(styles.columnGap || styles.gap || "0") || 0;
    const gap_y = parseFloat(styles.rowGap || styles.gap || "0") || 0;

    const container_aspect = width / Math.max(1, height);
    let rows = 1;
    let cols = item_count;
    let best_size = 0;
    let best_aspect_delta = Number.POSITIVE_INFINITY;

    for (let candidate_rows = 1; candidate_rows <= item_count; candidate_rows += 1) {
        const candidate_cols = Math.max(1, Math.ceil(item_count / candidate_rows));
        const free_width = width - gap_x * (candidate_cols - 1);
        const free_height = height - gap_y * (candidate_rows - 1);

        if (free_width <= 0 || free_height <= 0) {
            continue;
        }

        const candidate_size = Math.floor(Math.min(free_width / candidate_cols, free_height / candidate_rows));
        if (candidate_size <= 0) {
            continue;
        }

        const candidate_aspect = candidate_cols / Math.max(1, candidate_rows);
        const candidate_aspect_delta = Math.abs(candidate_aspect - container_aspect);
        const is_better_size = candidate_size > best_size;
        const is_better_tie = candidate_size === best_size && candidate_aspect_delta < best_aspect_delta;

        if (is_better_size || is_better_tie) {
            best_size = candidate_size;
            best_aspect_delta = candidate_aspect_delta;
            rows = candidate_rows;
            cols = candidate_cols;
        }
    }

    if (best_size <= 0) {
        rows = Math.max(1, Math.floor(Math.sqrt(item_count)));
        cols = Math.max(1, Math.ceil(item_count / rows));
        const free_width = width - gap_x * (cols - 1);
        const free_height = height - gap_y * (rows - 1);
        best_size = Math.floor(Math.min(Math.max(1, free_width / cols), Math.max(1, free_height / rows)));
    }

    const final_size = Math.max(10, best_size);
    const final_font_size = Math.max(8, Math.min(22, Math.floor(final_size * 0.22)));
    const final_button_padding = Math.max(1, Math.min(3, Math.floor(final_size * 0.045)));
    const final_badge_padding = Math.max(2, Math.min(9, Math.floor(final_size * 0.12)));
    const final_badge_border_width = Math.max(1, Math.min(3, Math.floor(final_size * 0.045)));
    const final_ghost_outline_inset = -Math.max(1, final_badge_border_width);
    const final_ghost_x_offset = Math.max(1, Math.round(final_size * 0.016));

    container.style.gridTemplateColumns = `repeat(${cols}, ${final_size}px)`;
    container.style.gridAutoRows = `${final_size}px`;
    container.style.setProperty("--fc-player-cell-size", `${final_size}px`);
    container.style.setProperty("--fc-player-font-size", `${final_font_size}px`);
    container.style.setProperty("--fc-player-button-padding", `${final_button_padding}px`);
    container.style.setProperty("--fc-player-badge-padding", `${final_badge_padding}px`);
    container.style.setProperty("--fc-player-badge-border-width", `${final_badge_border_width}px`);
    container.style.setProperty("--fc-player-ghost-outline-inset", `${final_ghost_outline_inset}px`);
    container.style.setProperty("--fc-player-ghost-x-offset", `${final_ghost_x_offset}px`);
}

function mark_player_as_ghost_in_table(player_name, team_symbol) {
    for (let i = 0; i < fc_state.players.length; i += 1) {
        if (fc_state.players[i].name === player_name) {
            fc_state.players[i].status = "ghost";
            fc_state.players[i].team_symbol = team_symbol;
            return;
        }
    }
}

function sync_randomized_player_order() {
    const current_names = fc_state.players
        .filter(function (player) {
            return player.name !== fc_player_name;
        })
        .map(function (player) {
            return player.name;
        });

    if (current_names.length === 0) {
        fc_state.randomized_player_order = [];
        return;
    }

    if (fc_state.randomized_player_order.length === 0) {
        fc_state.randomized_player_order = shuffled_copy(current_names);
        return;
    }

    const current_name_set = new Set(current_names);
    const existing_order = fc_state.randomized_player_order.filter(function (name) {
        return current_name_set.has(name);
    });

    const existing_set = new Set(existing_order);
    const missing_names = current_names.filter(function (name) {
        return !existing_set.has(name);
    });

    fc_state.randomized_player_order = existing_order.concat(shuffled_copy(missing_names));
}

function shuffled_copy(values) {
    const arr = values.slice();
    for (let i = arr.length - 1; i > 0; i -= 1) {
        const j = Math.floor(Math.random() * (i + 1));
        const tmp = arr[i];
        arr[i] = arr[j];
        arr[j] = tmp;
    }
    return arr;
}

function seconds_to_ms(seconds_value, fallback_ms) {
    const parsed = Number(seconds_value);
    if (Number.isFinite(parsed) && parsed > 0) {
        return parsed * 1000;
    }
    return fallback_ms;
}

function update_timers_ui() {
    const now = Date.now();

    const hand_fill = document.getElementById("flare-timer");
    if (fc_state.role === "alive" && fc_state.hand_color) {
        const total = Math.max(1, fc_state.hand_total_ms);
        const left = Math.max(0, fc_state.hand_expires_at_ms - now);
        const pct = Math.max(0, Math.min(100, (left / total) * 100));
        hand_fill.style.width = `${pct}%`;
        hand_fill.style.background = color_to_hex(fc_state.hand_color);

        if (left <= 0) {
            fc_state.hand_color = null;
            fc_state.hand_expires_at_ms = 0;
            render_alive_controls();
        }
    } else {
        hand_fill.style.width = "0%";
    }

    const ghost_fill = document.getElementById("ghost-cooldown-timer");
    if (fc_state.role === "ghost") {
        const total = Math.max(1, fc_state.ghost_cooldown_total_ms);
        const left = Math.max(0, fc_state.ghost_cooldown_expires_at_ms - now);
        const pct = 100 - Math.max(0, Math.min(100, (left / total) * 100));
        ghost_fill.style.width = `${pct}%`;
        ghost_fill.style.background = color_to_hex(fc_state.ghost_color || "gray");
        render_ghost_controls();
    } else {
        ghost_fill.style.width = "0%";
    }

    release_face_flash_block_if_expired();
}

function show_flash_overlay(color_name, duration_seconds) {
    const overlay = document.getElementById("flash-overlay");
    if (!overlay) {
        return;
    }

    const now = Date.now();
    const duration_ms = Math.max(150, (duration_seconds || 1) * 1000);
    const candidate_expires_at = now + duration_ms;
    fc_state.face_flash_expires_at_ms = Math.max(fc_state.face_flash_expires_at_ms, candidate_expires_at);

    overlay.style.background = color_to_hex(color_name);
    overlay.style.opacity = "1";
    overlay.style.pointerEvents = "auto";
    fc_flash_overlay_is_visible = true;

    if (fc_flash_overlay_timer_id !== null) {
        window.clearTimeout(fc_flash_overlay_timer_id);
    }

    const release_in_ms = Math.max(0, fc_state.face_flash_expires_at_ms - now);
    fc_flash_overlay_timer_id = window.setTimeout(function () {
        fc_flash_overlay_timer_id = null;
        release_face_flash_block_if_expired();
    }, release_in_ms);

    render_all();
}

function show_final_result(payload) {
    const panel = document.getElementById("result-panel");
    if (!panel) {
        return;
    }

    // Final result text is host-only; player UI stays text-free at match end.
    panel.textContent = "";
    panel.style.display = "none";
    schedule_players_grid_fit();
}

function show_result_message(msg) {
    const panel = document.getElementById("result-panel");
    panel.style.display = "block";
    panel.textContent = msg;
    schedule_players_grid_fit();
}

function color_to_hex(color_name) {
    return FC_COLORS[color_name] || FC_COLORS.gray;
}

function team_symbol_to_icon(team_symbol) {
    if (team_symbol === "circle") {
        return "O";
    }
    if (team_symbol === "square") {
        return "[]";
    }
    if (team_symbol === "ghost") {
        return "~[]";
    }
    return "?";
}

function team_symbol_to_reveal_shape_class(team_symbol) {
    if (team_symbol === "circle") {
        return "fc-team-circle";
    }
    if (team_symbol === "square") {
        return "fc-team-square";
    }
    if (team_symbol === "ghost") {
        return "fc-team-ghost-initial";
    }
    return null;
}
