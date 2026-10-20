let host_socket = null;
let host_redirecting = false;
const HOST_STATIC_STATUS = "flare curse en curso";
const HOST_FINISHED_STATUS = "flare curse terminado";

const HOST_MUSIC = {
    enabled: false,
    target_mode: "calm",
    exit_fade_active: false,
    voice_duck_factor: 1.0,
    audio_context: null,
    calm_buffer: null,
    intense_buffer: null,
    calm_loop_buffer: null,
    intense_loop_buffer: null,
    calm_loop_window: null,
    intense_loop_window: null,
    calm_source: null,
    intense_source: null,
    calm_gain: null,
    intense_gain: null,
    load_promise: null,
    start_promise: null,
};

const HOST_VOICE = {
    base_url: "",
    enabled: false,
    queue: [],
    playing: false,
    next_phrase_id: 0,
    last_played_phrase_id: null,
    pending_timer_id: null,
};

const HOST_MUSIC_MAX_VOLUME = 0.42;
const HOST_MUSIC_FADE_MS = 450;
const HOST_LOOP_EDGE_SCAN_SECONDS = 3.0;
const HOST_LOOP_SILENCE_THRESHOLD = 0.004;
const HOST_LOOP_GUARD_SECONDS = 0.0;
const HOST_LOOP_MIN_SECONDS = 1.0;
const HOST_LOOP_HARD_WRAP_SEARCH_MS = 120;
const HOST_LOOP_HARD_WRAP_COARSE_STEP_MS = 1;
const HOST_MUSIC_DUCK_WHILE_VOICE_FACTOR = 0.32;
const HOST_MUSIC_DUCK_ATTACK_MS = 120;
const HOST_MUSIC_DUCK_RELEASE_MS = 220;
const HOST_MUSIC_EXIT_FADE_MS = 900;
const HOST_VOICE_BASE_VOLUME = 1.0;
const HOST_VOICE_CHUNK_FADE_MS = 140;
const HOST_VOICE_INTER_PHRASE_SILENCE_MS = 120;
const HOST_VOICE_FADE_TICK_MS = 20;

const HOST_VOICE_TEAM_TRACK = {
    circle: "teams/circulo.mp3",
    square: "teams/cuadrado.mp3",
};

const HOST_VOICE_CONTEXT_TRACK = {
    del_equipo: "context/del_equipo.mp3",
    ha_sido_maldito: "context/ha_sido_maldito.mp3",
    el_juego_ha_terminado: "context/el_juego_ha_terminado.mp3",
    ha_ganado_el_equipo: "context/ha_ganado_el_equipo.mp3",
    con_word: "context/con_word.mp3",
    fantasmas_ganadores: "context/fantasmas_ganadores.mp3",
};

const HOST_COLOR_HEX = {
    red: "#FF2D55",
    green: "#0DFF72",
    blue: "#00B4FF",
    purple: "#CC00FF",
    orange: "#FF8000",
};

function init_flare_curse_host() {
    set_host_status();
    init_host_music();
    connect_host_socket();
}

function init_host_music() {
    const body = document.body;
    const calm_src = body.dataset.fcLoopCalm;
    const intense_src = body.dataset.fcLoopIntense;
    HOST_VOICE.base_url = body.dataset.fcVoiceBase || "";

    if (!calm_src || !intense_src) {
        return;
    }

    if (!window.AudioContext && !window.webkitAudioContext) {
        return;
    }

    HOST_MUSIC.load_promise = prepare_host_music_buffers(calm_src, intense_src);
    bind_host_audio_unlock_events();
    start_host_music(false);
}

function bind_host_audio_unlock_events() {
    if (typeof document === "undefined" || !document || typeof document.addEventListener !== "function") {
        return;
    }

    const try_start = function () {
        start_host_music(true);
    };

    document.addEventListener("pointerdown", try_start, { once: true, passive: true });
    document.addEventListener("touchstart", try_start, { once: true, passive: true });
    document.addEventListener("keydown", try_start, { once: true });
}

function is_wav_loop_source(src) {
    if (!src) {
        return false;
    }

    const normalized = String(src).toLowerCase();
    return /\.wav(?:\?|$)/.test(normalized);
}

async function prepare_host_music_buffers(calm_src, intense_src) {
    const AudioContextCtor = window.AudioContext || window.webkitAudioContext;
    HOST_MUSIC.audio_context = new AudioContextCtor();

    const [calm_buffer, intense_buffer] = await Promise.all([
        fetch_audio_buffer(HOST_MUSIC.audio_context, calm_src),
        fetch_audio_buffer(HOST_MUSIC.audio_context, intense_src),
    ]);

    HOST_MUSIC.calm_buffer = calm_buffer;
    HOST_MUSIC.intense_buffer = intense_buffer;
    const calm_is_wav = is_wav_loop_source(calm_src);
    const intense_is_wav = is_wav_loop_source(intense_src);

    HOST_MUSIC.calm_loop_window = calm_is_wav
        ? { start: 0.0, end: calm_buffer.duration }
        : refine_loop_window_for_hard_wrap(calm_buffer, detect_loop_window(calm_buffer));
    HOST_MUSIC.intense_loop_window = intense_is_wav
        ? { start: 0.0, end: intense_buffer.duration }
        : refine_loop_window_for_hard_wrap(intense_buffer, detect_loop_window(intense_buffer));
    HOST_MUSIC.calm_loop_buffer = null;
    HOST_MUSIC.intense_loop_buffer = null;

    if (calm_is_wav && intense_is_wav) {
        console.info("Flare Curse host loops en modo WAV estricto (loop 0->duracion completa).");
    }

    const duration_delta = Math.abs(calm_buffer.duration - intense_buffer.duration);
    if (duration_delta > 0.02) {
        console.warn(
            `Flare Curse loops tienen distinta duracion (${calm_buffer.duration.toFixed(3)} vs ${intense_buffer.duration.toFixed(3)}). `
            + "Para sincronizacion perfecta, exportalas con la misma longitud exacta."
        );
    }

    const calm_span = HOST_MUSIC.calm_loop_window.end - HOST_MUSIC.calm_loop_window.start;
    const intense_span = HOST_MUSIC.intense_loop_window.end - HOST_MUSIC.intense_loop_window.start;
    const span_delta = Math.abs(calm_span - intense_span);
    if (span_delta > 0.02) {
        console.warn(
            `Flare Curse loop spans distintos (${calm_span.toFixed(3)} vs ${intense_span.toFixed(3)}). `
            + "Para transiciones perfectas, usa archivos con igual contenido util."
        );
    }

}

function detect_loop_window(buffer) {
    if (!buffer || buffer.length <= 0 || buffer.sampleRate <= 0 || buffer.numberOfChannels <= 0) {
        return { start: 0.0, end: buffer ? buffer.duration : 0.0 };
    }

    const total_samples = buffer.length;
    const sample_rate = buffer.sampleRate;
    const scan_samples = Math.min(total_samples, Math.max(1, Math.floor(sample_rate * HOST_LOOP_EDGE_SCAN_SECONDS)));

    const channel_data = [];
    for (let channel = 0; channel < buffer.numberOfChannels; channel += 1) {
        channel_data.push(buffer.getChannelData(channel));
    }

    const is_silent_at = function (sample_index) {
        for (let channel = 0; channel < channel_data.length; channel += 1) {
            if (Math.abs(channel_data[channel][sample_index]) > HOST_LOOP_SILENCE_THRESHOLD) {
                return false;
            }
        }
        return true;
    };

    let first_non_silent = 0;
    while (first_non_silent < scan_samples && is_silent_at(first_non_silent)) {
        first_non_silent += 1;
    }

    const trailing_scan_start = Math.max(0, total_samples - scan_samples);
    let last_non_silent = total_samples - 1;
    while (last_non_silent >= trailing_scan_start && is_silent_at(last_non_silent)) {
        last_non_silent -= 1;
    }

    let start_seconds = first_non_silent / sample_rate;
    let end_seconds = (last_non_silent + 1) / sample_rate;

    if (!Number.isFinite(start_seconds) || !Number.isFinite(end_seconds) || end_seconds <= start_seconds) {
        return { start: 0.0, end: buffer.duration };
    }

    start_seconds = Math.max(0.0, start_seconds + HOST_LOOP_GUARD_SECONDS);
    end_seconds = Math.min(buffer.duration, end_seconds - HOST_LOOP_GUARD_SECONDS);

    if ((end_seconds - start_seconds) < HOST_LOOP_MIN_SECONDS) {
        return { start: 0.0, end: buffer.duration };
    }

    return {
        start: start_seconds,
        end: end_seconds,
    };
}

function normalize_loop_window(buffer, loop_window) {
    if (!buffer || buffer.length <= 0 || buffer.sampleRate <= 0) {
        return { start: 0.0, end: buffer ? buffer.duration : 0.0 };
    }

    const min_span_seconds = 1 / buffer.sampleRate;
    let start_seconds = loop_window && Number.isFinite(loop_window.start) ? Number(loop_window.start) : 0.0;
    let end_seconds = loop_window && Number.isFinite(loop_window.end) ? Number(loop_window.end) : buffer.duration;

    start_seconds = Math.max(0.0, Math.min(buffer.duration, start_seconds));
    end_seconds = Math.max(start_seconds + min_span_seconds, Math.min(buffer.duration, end_seconds));

    if ((end_seconds - start_seconds) < min_span_seconds) {
        return { start: 0.0, end: buffer.duration };
    }

    return {
        start: start_seconds,
        end: end_seconds,
    };
}

function score_hard_wrap_pair(channel_data, start_sample, end_sample) {
    let total_score = 0.0;
    const channel_count = Math.max(1, channel_data.length);

    for (let channel = 0; channel < channel_data.length; channel += 1) {
        const data = channel_data[channel];
        const head_index = Math.max(0, Math.min(data.length - 1, start_sample));
        const head_next_index = Math.max(0, Math.min(data.length - 1, head_index + 1));
        const tail_index = Math.max(1, Math.min(data.length - 1, end_sample - 1));
        const tail_prev_index = Math.max(0, tail_index - 1);

        const head = data[head_index];
        const head_next = data[head_next_index];
        const tail = data[tail_index];
        const tail_prev = data[tail_prev_index];

        const amplitude_jump = Math.abs(head - tail);
        const slope_jump = Math.abs((head_next - head) - (tail - tail_prev));
        total_score += amplitude_jump + (0.25 * slope_jump);
    }

    return total_score / channel_count;
}

function refine_loop_window_for_hard_wrap(buffer, loop_window) {
    const normalized = normalize_loop_window(buffer, loop_window);
    if (!buffer || buffer.length <= 4 || buffer.sampleRate <= 0 || buffer.numberOfChannels <= 0) {
        return normalized;
    }

    const sample_rate = buffer.sampleRate;
    const total_samples = buffer.length;
    const min_span_samples = Math.max(2, Math.floor(HOST_LOOP_MIN_SECONDS * sample_rate));
    let start_base = Math.max(0, Math.min(total_samples - 2, Math.floor(normalized.start * sample_rate)));
    let end_base = Math.max(start_base + 2, Math.min(total_samples, Math.ceil(normalized.end * sample_rate)));

    if ((end_base - start_base) < min_span_samples) {
        start_base = 0;
        end_base = total_samples;
    }

    if ((end_base - start_base) < 3) {
        return { start: normalized.start, end: normalized.end };
    }

    const max_adjust_samples = Math.min(
        Math.floor(sample_rate * (HOST_LOOP_HARD_WRAP_SEARCH_MS / 1000.0)),
        Math.max(0, Math.floor(((end_base - start_base) - min_span_samples) / 2)),
    );

    if (max_adjust_samples <= 0) {
        return {
            start: start_base / sample_rate,
            end: end_base / sample_rate,
        };
    }

    const coarse_step_samples = Math.max(1, Math.floor(sample_rate * (HOST_LOOP_HARD_WRAP_COARSE_STEP_MS / 1000.0)));
    const start_min = start_base;
    const start_max = Math.min(end_base - 2, start_base + max_adjust_samples);
    const end_min_base = Math.max(start_base + 2, end_base - max_adjust_samples);
    const end_max = end_base;

    const channel_data = [];
    for (let channel = 0; channel < buffer.numberOfChannels; channel += 1) {
        channel_data.push(buffer.getChannelData(channel));
    }

    let best_start = start_base;
    let best_end = end_base;
    let best_score = score_hard_wrap_pair(channel_data, best_start, best_end);

    for (let start_sample = start_min; start_sample <= start_max; start_sample += coarse_step_samples) {
        const end_min = Math.max(end_min_base, start_sample + min_span_samples);
        for (let end_sample = end_min; end_sample <= end_max; end_sample += coarse_step_samples) {
            const score = score_hard_wrap_pair(channel_data, start_sample, end_sample);
            if (score < best_score) {
                best_score = score;
                best_start = start_sample;
                best_end = end_sample;
            }
        }
    }

    const refine_start_min = Math.max(start_min, best_start - coarse_step_samples);
    const refine_start_max = Math.min(start_max, best_start + coarse_step_samples);
    const refine_end_min_base = Math.max(end_min_base, best_end - coarse_step_samples);
    const refine_end_max = Math.min(end_max, best_end + coarse_step_samples);

    for (let start_sample = refine_start_min; start_sample <= refine_start_max; start_sample += 1) {
        const end_min = Math.max(refine_end_min_base, start_sample + min_span_samples);
        for (let end_sample = end_min; end_sample <= refine_end_max; end_sample += 1) {
            const score = score_hard_wrap_pair(channel_data, start_sample, end_sample);
            if (score < best_score) {
                best_score = score;
                best_start = start_sample;
                best_end = end_sample;
            }
        }
    }

    return {
        start: best_start / sample_rate,
        end: best_end / sample_rate,
    };
}

async function fetch_audio_buffer(audio_context, src) {
    const response = await fetch(src);
    if (!response.ok) {
        throw new Error(`No se pudo cargar audio: ${src}`);
    }

    const array_buffer = await response.arrayBuffer();
    return await audio_context.decodeAudioData(array_buffer);
}

async function start_host_music(manual_trigger) {
    if (!HOST_MUSIC.load_promise) {
        return;
    }

    if (HOST_MUSIC.enabled) {
        apply_music_mode(HOST_MUSIC.target_mode);
        return;
    }

    if (HOST_MUSIC.start_promise) {
        await HOST_MUSIC.start_promise;
        return;
    }

    HOST_MUSIC.start_promise = start_host_music_internal(manual_trigger);
    try {
        await HOST_MUSIC.start_promise;
    } finally {
        HOST_MUSIC.start_promise = null;
    }
}

async function start_host_music_internal(manual_trigger) {
    try {
        await HOST_MUSIC.load_promise;
        await HOST_MUSIC.audio_context.resume();
        ensure_music_graph_started();

        HOST_MUSIC.exit_fade_active = false;
        HOST_MUSIC.enabled = true;
        HOST_VOICE.enabled = HOST_VOICE.base_url.length > 0;
        apply_music_mode(HOST_MUSIC.target_mode, true);
        play_next_voice_track();
    } catch (error) {
        if (manual_trigger) {
            console.warn("Flare Curse audio unlock failed", error);
        }
    }
}

function ensure_music_graph_started() {
    if (HOST_MUSIC.calm_source || HOST_MUSIC.intense_source) {
        return;
    }

    const audio_context = HOST_MUSIC.audio_context;
    const calm_source = audio_context.createBufferSource();
    const intense_source = audio_context.createBufferSource();
    const calm_gain = audio_context.createGain();
    const intense_gain = audio_context.createGain();
    const calm_buffer = HOST_MUSIC.calm_buffer;
    const intense_buffer = HOST_MUSIC.intense_buffer;
    const calm_window = normalize_loop_window(calm_buffer, HOST_MUSIC.calm_loop_window);
    const intense_window = normalize_loop_window(intense_buffer, HOST_MUSIC.intense_loop_window);

    calm_source.buffer = calm_buffer;
    intense_source.buffer = intense_buffer;
    calm_source.loop = true;
    intense_source.loop = true;
    calm_source.loopStart = calm_window.start;
    calm_source.loopEnd = calm_window.end;
    intense_source.loopStart = intense_window.start;
    intense_source.loopEnd = intense_window.end;

    calm_gain.gain.value = 0.0;
    intense_gain.gain.value = 0.0;

    calm_source.connect(calm_gain);
    intense_source.connect(intense_gain);
    calm_gain.connect(audio_context.destination);
    intense_gain.connect(audio_context.destination);

    // Both loops start on the same audio clock tick for sample-locked sync.
    const start_at = audio_context.currentTime + 0.05;
    calm_source.start(start_at, calm_window.start);
    intense_source.start(start_at, intense_window.start);

    HOST_MUSIC.calm_source = calm_source;
    HOST_MUSIC.intense_source = intense_source;
    HOST_MUSIC.calm_gain = calm_gain;
    HOST_MUSIC.intense_gain = intense_gain;
}

function apply_music_mode(mode, immediate) {
    HOST_MUSIC.target_mode = mode === "intense" ? "intense" : "calm";

    const fade_ms = immediate ? 0 : HOST_MUSIC_FADE_MS;
    apply_music_targets(fade_ms);
}

function apply_music_targets(duration_ms) {
    if (!HOST_MUSIC.enabled) {
        return;
    }

    if (HOST_MUSIC.exit_fade_active) {
        crossfade_music(0.0, 0.0, duration_ms);
        return;
    }

    const duck_factor = clamp_audio_volume(HOST_MUSIC.voice_duck_factor);
    const base_volume = HOST_MUSIC_MAX_VOLUME * duck_factor;
    const calm_target = HOST_MUSIC.target_mode === "calm" ? base_volume : 0.0;
    const intense_target = HOST_MUSIC.target_mode === "intense" ? base_volume : 0.0;
    crossfade_music(calm_target, intense_target, duration_ms);
}

function start_host_music_exit_fade() {
    if (!HOST_MUSIC.enabled) {
        return;
    }

    HOST_MUSIC.exit_fade_active = true;
    crossfade_music(0.0, 0.0, HOST_MUSIC_EXIT_FADE_MS);
}

function set_music_voice_ducking(enabled) {
    const next_factor = enabled ? HOST_MUSIC_DUCK_WHILE_VOICE_FACTOR : 1.0;
    if (Math.abs(HOST_MUSIC.voice_duck_factor - next_factor) < 0.0001) {
        return;
    }

    HOST_MUSIC.voice_duck_factor = next_factor;
    apply_music_targets(enabled ? HOST_MUSIC_DUCK_ATTACK_MS : HOST_MUSIC_DUCK_RELEASE_MS);
}

function crossfade_music(calm_target, intense_target, duration_ms) {
    if (!HOST_MUSIC.calm_gain || !HOST_MUSIC.intense_gain || !HOST_MUSIC.audio_context) {
        return;
    }

    const now = HOST_MUSIC.audio_context.currentTime;
    const fade_seconds = Math.max(0, duration_ms / 1000.0);
    const calm_param = HOST_MUSIC.calm_gain.gain;
    const intense_param = HOST_MUSIC.intense_gain.gain;

    calm_param.cancelScheduledValues(now);
    intense_param.cancelScheduledValues(now);
    calm_param.setValueAtTime(calm_param.value, now);
    intense_param.setValueAtTime(intense_param.value, now);

    if (fade_seconds <= 0) {
        calm_param.setValueAtTime(calm_target, now);
        intense_param.setValueAtTime(intense_target, now);
        return;
    }

    calm_param.linearRampToValueAtTime(calm_target, now + fade_seconds);
    intense_param.linearRampToValueAtTime(intense_target, now + fade_seconds);
}

function connect_host_socket() {
    const socket_url = `ws://${window.location.host}/ws/flare_curse_room/?role=host`;
    host_socket = new WebSocket(socket_url);

    host_socket.onopen = function () {
        set_host_status();
    };

    host_socket.onmessage = function (event) {
        const data = JSON.parse(event.data);
        handle_host_message(data);
    };

    host_socket.onclose = function () {
        if (!host_redirecting) {
            set_host_status();
            window.setTimeout(connect_host_socket, 1500);
        }
    };
}

function handle_host_message(data) {
    if (data.type === "Error") {
        console.warn("Flare Curse host socket error", data.message || "Error inesperado");
        return;
    }

    if (data.type === "MusicModeChanged") {
        apply_music_mode(data.mode);
        return;
    }

    if (data.type === "NuevoJugadorMaldito") {
        announce_curse(data);
        return;
    }

    if (data.type === "FinJuego") {
        apply_music_mode("intense");
        announce_game_finished(data);
        render_host_final_summary(data);
        return;
    }

    if (data.type === "GoToWaitRoom") {
        host_redirecting = true;
        start_host_music_exit_fade();
        if (typeof admin_next_game === "function") {
            // Give players a brief moment to reach wait_room and subscribe.
            window.setTimeout(function () {
                admin_next_game();
            }, 1500);
        } else {
            window.location.href = "../game_selector/";
        }
    }
}

function set_host_status() {
    const status = document.getElementById("host-status");
    if (status) {
        status.textContent = HOST_STATIC_STATUS;
    }
}

function team_symbol_to_text(team_symbol) {
    if (team_symbol === "circle") {
        return "Circulo";
    }
    if (team_symbol === "square") {
        return "Cuadrado";
    }
    if (team_symbol === "ghost") {
        return "Fantasma";
    }
    return "-";
}

function team_symbol_to_icon_class(team_symbol) {
    if (team_symbol === "circle") {
        return "circle";
    }
    if (team_symbol === "square") {
        return "square";
    }
    return "unknown";
}

function is_initial_player_team(team_symbol) {
    return team_symbol === "circle" || team_symbol === "square";
}

function build_history_initial_team_index(curse_history) {
    const initial_team_by_player = {};
    if (!Array.isArray(curse_history)) {
        return initial_team_by_player;
    }

    for (const row of curse_history) {
        const references = [
            [row.origin, row.origin_team],
            [row.target, row.target_team],
            [row.cursed_player, row.cursed_team],
        ];

        for (const [player_name, team_symbol] of references) {
            if (!player_name || !is_initial_player_team(team_symbol)) {
                continue;
            }

            const key = String(player_name);
            if (!Object.prototype.hasOwnProperty.call(initial_team_by_player, key)) {
                initial_team_by_player[key] = team_symbol;
            }
        }
    }

    return initial_team_by_player;
}

function resolve_history_player_team(player_name, payload_team_symbol, initial_team_by_player) {
    if (is_initial_player_team(payload_team_symbol)) {
        return payload_team_symbol;
    }

    const key = String(player_name || "");
    if (!key) {
        return null;
    }

    if (Object.prototype.hasOwnProperty.call(initial_team_by_player, key)) {
        return initial_team_by_player[key];
    }

    return null;
}

function team_icon_markup(team_symbol) {
    const icon_class = team_symbol_to_icon_class(team_symbol);
    const team_label = team_symbol_to_text(team_symbol);
    return `<span class="fc-team-mini fc-team-mini-${icon_class}" aria-label="equipo ${escape_html(team_label)}"></span>`;
}

function normalize_color_token(color_value) {
    const token = String(color_value || "").trim().toLowerCase();
    if (Object.prototype.hasOwnProperty.call(HOST_COLOR_HEX, token)) {
        return token;
    }
    return "";
}

function color_swatch_markup(color_value) {
    const token = normalize_color_token(color_value);
    if (!token) {
        return `<span class="fc-color-swatch fc-color-swatch-unknown" aria-label="sin color" title="sin color"></span>`;
    }

    return `<span class="fc-color-swatch" style="--fc-color-swatch: ${HOST_COLOR_HEX[token]};" aria-label="color ${escape_html(token)}" title="${escape_html(token)}"></span>`;
}

function render_host_final_summary(payload) {
    const results = document.getElementById("host-results");
    if (!results) {
        return;
    }

    const status = document.getElementById("host-status");
    if (status) {
        status.textContent = HOST_FINISHED_STATUS;
    }

    results.style.display = "block";

    const winner_team_icon = team_icon_markup(payload.winner_team);
    const winners = (payload.winner_players || []).join(", ") || "-";
    const curse_history = Array.isArray(payload.curse_history) ? payload.curse_history : [];
    const initial_team_by_player = build_history_initial_team_index(curse_history);

    let ghost_leaderboard = [];
    if (Array.isArray(payload.ghost_leaderboard)) {
        ghost_leaderboard = payload.ghost_leaderboard;
    } else {
        ghost_leaderboard = Object.entries(payload.ghost_points || {}).map(function ([name, points]) {
            return { name: name, points: points, color: "-" };
        });
        ghost_leaderboard.sort(function (a, b) {
            if (b.points !== a.points) {
                return b.points - a.points;
            }
            return String(a.name).localeCompare(String(b.name));
        });
    }

    const curse_rows_html = curse_history.length === 0
        ? `<tr><td colspan="4">Sin maldiciones registradas.</td></tr>`
        : curse_history.map(function (row) {
            const is_rebound = !row.victim_is_enemy;
            const row_class = is_rebound ? "fc-curse-row-rebound" : "fc-curse-row-hit";
            const result_class = is_rebound ? "fc-curse-result-rebound" : "fc-curse-result-hit";
            const result = is_rebound ? "Rebote" : "Acierto";
            const origin_team = resolve_history_player_team(row.origin, row.origin_team, initial_team_by_player);
            const target_team = resolve_history_player_team(row.target, row.target_team, initial_team_by_player);
            return `
                <tr class="${row_class}">
                    <td>${row.order ?? "-"}</td>
                    <td>
                        <span class="fc-player-with-team">
                            ${team_icon_markup(origin_team)}
                            <span>${escape_html(row.origin || "-")}</span>
                        </span>
                    </td>
                    <td>
                        <span class="fc-player-with-team">
                            ${team_icon_markup(target_team)}
                            <span>${escape_html(row.target || "-")}</span>
                        </span>
                    </td>
                    <td><span class="fc-curse-result-chip ${result_class}">${result}</span></td>
                </tr>
            `;
        }).join("");

    const ghost_rows_html = ghost_leaderboard.length === 0
        ? `<tr><td colspan="4">No hay fantasmas.</td></tr>`
        : ghost_leaderboard.map(function (row, index) {
            return `
                <tr>
                    <td>${index + 1}</td>
                    <td>${escape_html(row.name || "-")}</td>
                    <td>${Number(row.points ?? 0)}</td>
                    <td><span class="fc-color-cell">${color_swatch_markup(row.color)}</span></td>
                </tr>
            `;
        }).join("");

    results.innerHTML = `
        <div class="fc-host-summary-line">Ha ganado el equipo <span class="fc-host-summary-team-icon">${winner_team_icon}</span> con <strong>${escape_html(winners)}</strong>.</div>

        <div class="fc-host-results-columns">
            <section class="fc-host-results-column">
                <h3>Historial de maldiciones</h3>
                <table class="fc-host-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Origen</th>
                            <th>Objetivo</th>
                            <th>Resultado</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${curse_rows_html}
                    </tbody>
                </table>
            </section>

            <section class="fc-host-results-column">
                <h3>Leaderboard de fantasmas</h3>
                <table class="fc-host-table">
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Fantasma</th>
                            <th>Puntos</th>
                            <th>Color</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${ghost_rows_html}
                    </tbody>
                </table>
            </section>
        </div>
    `;
}

function escape_html(value) {
    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

function announce_curse(payload) {
    const tracks = [player_voice_track(payload.player)];

    enqueue_voice_tracks(tracks);
}

function announce_game_finished(payload) {
    const tracks = [
        context_voice_track("el_juego_ha_terminado"),
        context_voice_track("ha_ganado_el_equipo"),
        team_voice_track(payload.winner_team),
        context_voice_track("con_word"),
    ];

    for (const name of payload.winner_players || []) {
        tracks.push(player_voice_track(name));
    }

    tracks.push(context_voice_track("fantasmas_ganadores"));

    for (const name of payload.ghost_winners || []) {
        tracks.push(player_voice_track(name));
    }

    enqueue_voice_tracks(tracks);
}

function enqueue_voice_tracks(tracks) {
    if (!HOST_VOICE.enabled || !tracks || tracks.length === 0) {
        return;
    }

    const valid_tracks = tracks.filter(function (track) {
        return Boolean(track);
    });
    if (valid_tracks.length === 0) {
        return;
    }

    const phrase_id = HOST_VOICE.next_phrase_id + 1;
    HOST_VOICE.next_phrase_id = phrase_id;

    for (const track of valid_tracks) {
        HOST_VOICE.queue.push({
            src: track,
            phrase_id: phrase_id,
        });
    }

    play_next_voice_track();
}

function play_next_voice_track() {
    if (!HOST_VOICE.enabled || HOST_VOICE.playing) {
        return;
    }

    if (HOST_VOICE.pending_timer_id !== null) {
        return;
    }

    if (HOST_VOICE.queue.length === 0) {
        return;
    }

    const entry = HOST_VOICE.queue.shift();
    const audio = new Audio(entry.src);
    const same_phrase_as_previous = HOST_VOICE.last_played_phrase_id === entry.phrase_id;
    HOST_VOICE.playing = true;
    audio.preload = "auto";
    audio.volume = same_phrase_as_previous ? 0.0 : HOST_VOICE_BASE_VOLUME;

    set_music_voice_ducking(true);

    let finished = false;
    let fade_out_started = false;
    let fade_in_timer_id = null;
    let fade_out_timer_id = null;

    const clear_fades = function () {
        if (fade_in_timer_id !== null) {
            window.clearInterval(fade_in_timer_id);
            fade_in_timer_id = null;
        }
        if (fade_out_timer_id !== null) {
            window.clearInterval(fade_out_timer_id);
            fade_out_timer_id = null;
        }
    };

    const finish = function () {
        if (finished) {
            return;
        }
        finished = true;
        clear_fades();
        HOST_VOICE.playing = false;
        HOST_VOICE.last_played_phrase_id = entry.phrase_id;

        const next_entry = HOST_VOICE.queue.length > 0 ? HOST_VOICE.queue[0] : null;
        if (!next_entry) {
            set_music_voice_ducking(false);
            return;
        }

        const needs_phrase_gap = next_entry.phrase_id !== entry.phrase_id;
        if (!needs_phrase_gap) {
            play_next_voice_track();
            return;
        }

        HOST_VOICE.pending_timer_id = window.setTimeout(function () {
            HOST_VOICE.pending_timer_id = null;
            play_next_voice_track();
        }, HOST_VOICE_INTER_PHRASE_SILENCE_MS);
    };

    audio.ontimeupdate = function () {
        if (fade_out_started) {
            return;
        }

        const next_entry = HOST_VOICE.queue.length > 0 ? HOST_VOICE.queue[0] : null;
        if (!next_entry || next_entry.phrase_id !== entry.phrase_id) {
            return;
        }

        if (!Number.isFinite(audio.duration) || audio.duration <= 0) {
            return;
        }

        const remaining_ms = Math.max(0, (audio.duration - audio.currentTime) * 1000);
        if (remaining_ms <= (HOST_VOICE_CHUNK_FADE_MS + HOST_VOICE_FADE_TICK_MS)) {
            fade_out_started = true;
            fade_out_timer_id = fade_audio_volume(audio, audio.volume, 0.0, Math.max(40, remaining_ms));
        }
    };

    audio.onended = finish;
    audio.onerror = finish;
    audio.play().then(function () {
        if (same_phrase_as_previous) {
            fade_in_timer_id = fade_audio_volume(audio, 0.0, HOST_VOICE_BASE_VOLUME, HOST_VOICE_CHUNK_FADE_MS);
        }
    }).catch(finish);
}

function fade_audio_volume(audio, from_volume, to_volume, duration_ms) {
    if (!audio) {
        return null;
    }

    const start_volume = clamp_audio_volume(from_volume);
    const end_volume = clamp_audio_volume(to_volume);
    const fade_ms = Math.max(0, Number(duration_ms) || 0);

    audio.volume = start_volume;

    if (fade_ms <= 0) {
        audio.volume = end_volume;
        return null;
    }

    const started_at = performance.now();
    const delta = end_volume - start_volume;

    const timer_id = window.setInterval(function () {
        const elapsed = performance.now() - started_at;
        const progress = Math.min(1, elapsed / fade_ms);
        audio.volume = clamp_audio_volume(start_volume + (delta * progress));

        if (progress >= 1 || audio.ended) {
            window.clearInterval(timer_id);
        }
    }, HOST_VOICE_FADE_TICK_MS);

    return timer_id;
}

function clamp_audio_volume(value) {
    const parsed = Number(value);
    if (!Number.isFinite(parsed)) {
        return 1.0;
    }
    return Math.max(0, Math.min(1, parsed));
}

function context_voice_track(key) {
    const relative = HOST_VOICE_CONTEXT_TRACK[key];
    return relative ? join_voice_track(relative) : null;
}

function team_voice_track(team_symbol) {
    const relative = HOST_VOICE_TEAM_TRACK[team_symbol];
    return relative ? join_voice_track(relative) : null;
}

function player_voice_track(player_name) {
    if (!player_name) {
        return null;
    }

    const token = sanitize_voice_token(player_name);
    return join_voice_track(`players/${token}.mp3`);
}

function join_voice_track(relative_path) {
    if (!HOST_VOICE.base_url) {
        return null;
    }

    return `${HOST_VOICE.base_url}${relative_path}`;
}

function sanitize_voice_token(value) {
    const lower = String(value).toLowerCase();
    const normalized = lower.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    const replaced = normalized.replace(/[^a-z0-9.-]+/g, "-").replace(/^-+|-+$/g, "");
    if (replaced.length === 0) {
        return "anon";
    }
    return replaced.slice(0, 60);
}
