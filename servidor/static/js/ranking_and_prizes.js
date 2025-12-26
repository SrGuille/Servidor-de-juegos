var candidate_players = [];
var players_prob = []; 
var candidate_prizes = [];
var prizes_prob = []
santa_sound = new Audio('/static/sounds/santa.mp3');

TIME_BEFORE_SPINNING = 5000; // Time to wait before starting the spinning animation (with the images already loaded)
TIME_DURING_SPINNING = 6000; // Duration of the spinning animation
TIME_AFTER_SPINNING = 6000; // Time to see the result after the spinning animation

TIME_BEFORE_TRANSITION = 3000; // Time to wait before starting the ranking table animation
TIME_TRANSITION_FADE_OUT = 500; // Duration of the transition animation
TIME_TRANSITION_FADE_IN = 100; // Duration of the transition animation

TIME_TO_SEE_TABLE = 5000; // Time to see the ranking table after the transition animation

async function get_ranking_and_spin_roulettes()
{
    await get_ranking_from_scores();
    await get_available_prizes();
    await new Promise(r => setTimeout(r, TIME_TO_SEE_TABLE));
    
    // Save scores BEFORE prize is given (this is the state shown in first table after transition)
    let scores_before_prize = await get_current_scores_for_regulation();
    
    let [winner_name, prize] = await create_and_spin_roulettes('');
    //let [chosen_player, call_santa, call_special_duel] = await decide_call_special_duel_or_santa(winner_name);
    //if (call_special_duel)
    //{
    //    special_duel(winner_name, chosen_player, prize);
    //}
    //else
    //{
    //    await send_prize_to_winner(winner_name, prize, false); // Original winner
    //    if (call_santa)
    //    {
    //        await santa(chosen_player);
    //    }
    //
    await send_prize_to_winner(winner_name, prize, false); // Original winner
    
    // Get scores AFTER prize (winner already lost coins)
    let scores_after_prize = await get_current_scores_for_regulation();
    
    let regulated_players = await balance_inflation_deflation();
    console.log(regulated_players)
    // Pass both: scores_before_prize (first table) and scores_after_prize (after prize)
    await update_ranking_table(regulated_players, scores_before_prize, scores_after_prize);
    await new Promise(r => setTimeout(r, TIME_TO_SEE_TABLE));
    await admin_next_game();
    //}
}

// Get players previous scores for animated transition
async function get_players_previous_scores()
{
    console.log("[RANKING ANIMATION] Fetching previous scores...");
    return new Promise((resolve, reject) => {
        $.ajax({
            url: '../get_players_previous_scores/',
            type: 'GET',
            contentType: 'application/json;charset=UTF-8',
            success: function(previous_scores) 
            {
                console.log("[RANKING ANIMATION] Previous scores received:", previous_scores);
                resolve(previous_scores);
            },
            error: function(err) {
                console.error("[RANKING ANIMATION] Error getting previous scores:", err);
                reject(err);
            }
        });
    });
}

// Get the players scores and create the ranking table with animation from previous scores
async function get_ranking_from_scores()
{
    console.log("[RANKING ANIMATION] Starting get_ranking_from_scores...");
    
    // First get previous scores
    let previous_scores = await get_players_previous_scores();
    
    // Check if any player has previous_coins > 0
    let has_previous_scores = previous_scores.some(p => p.previous_coins > 0);
    console.log("[RANKING ANIMATION] Has previous scores > 0:", has_previous_scores);
    
    return new Promise(async (resolve, reject) => {
        $.ajax({
            url: '../get_players_scores/',
            type: 'GET',
            contentType: 'application/json;charset=UTF-8',
            success: async function(all_players) 
            {
                console.log("[RANKING ANIMATION] Current scores received:", all_players);
                
                if (has_previous_scores) {
                    console.log("[RANKING ANIMATION] Using ANIMATED ranking table");
                    // Create ranking with previous scores first
                    total_coins = await create_animated_ranking_table(all_players, previous_scores);
                } else {
                    console.log("[RANKING ANIMATION] Using STATIC ranking table (no previous scores)");
                    // No previous scores, just show current
                    total_coins = create_ranking_table(all_players);
                }
                
                // Remove the players with 0 coins
                candidate_players = all_players.filter(i => i.coins > 0);
                players_prob = candidate_players.map(x => x.coins / total_coins);
                console.log("[RANKING ANIMATION] Candidate players:", candidate_players);
                console.log("[RANKING ANIMATION] Players probabilities:", players_prob);
                resolve();
            },
            error: function(err) {
                console.error("[RANKING ANIMATION] Error getting players scores:", err);
                reject(err);
            }
        });
    });
}

// Create ranking table with animation from previous to current scores
async function create_animated_ranking_table(current_scores, previous_scores)
{
    console.log("[RANKING ANIMATION] Creating animated ranking table...");
    
    // Merge previous coins into current scores
    let players_with_both = current_scores.map(player => {
        let prev = previous_scores.find(p => p.name === player.name);
        return {
            ...player,
            coins_before: prev ? prev.previous_coins : 0,
            coins_after: player.coins,
            coin_change: player.coins - (prev ? prev.previous_coins : 0)
        };
    });
    
    // Run the generic animation
    await animate_ranking_transition(players_with_both, 'coins_before', 'coins_after', '[RANKING ANIMATION]');
    
    // Calculate total coins
    let total_coins = players_with_both.reduce((sum, p) => sum + parseInt(p.coins), 0);
    return total_coins;
}

// Generic function to animate ranking transition
async function animate_ranking_transition(players, before_key, after_key, log_prefix) {
    display_ranking();
    
    let ranking_left_body = document.getElementById("tbody-ranking-left");
    let ranking_right_body = document.getElementById("tbody-ranking-right");
    let ranking_columns = document.querySelector('.ranking-columns');
    
    // Clear previous content
    ranking_left_body.innerHTML = '';
    ranking_right_body.innerHTML = '';
    
    // Sort by BEFORE coins
    let players_by_before = [...players].sort((a, b) => b[before_key] - a[before_key]);
    console.log(`${log_prefix} Sorted by BEFORE:`, players_by_before.map(p => `${p.nick}: ${p[before_key]}`));
    
    // Sort by AFTER coins to get new positions
    let players_by_after = [...players].sort((a, b) => b[after_key] - a[after_key]);
    console.log(`${log_prefix} Sorted by AFTER:`, players_by_after.map(p => `${p.nick}: ${p[after_key]}`));
    
    // Calculate position changes
    players.forEach(player => {
        let prev_pos = players_by_before.findIndex(p => p.name === player.name);
        let curr_pos = players_by_after.findIndex(p => p.name === player.name);
        player.position_change = prev_pos - curr_pos; // Positive = moved up
        console.log(`${log_prefix} ${player.nick}: pos ${prev_pos+1} -> ${curr_pos+1} (change: ${player.position_change}), coins ${player[before_key]} -> ${player[after_key]} (change: ${player.coin_change})`);
    });
    
    const SPLIT_THRESHOLD = 3;
    const needs_split = players_by_before.length >= SPLIT_THRESHOLD;
    const mid_point = Math.ceil(players_by_before.length / 2);
    
    console.log(`${log_prefix} Split threshold: ${SPLIT_THRESHOLD}, needs_split: ${needs_split}`);
    
    // First, display with BEFORE scores and positions
    console.log(`${log_prefix} Displaying BEFORE scores...`);
    if (needs_split) {
        ranking_columns.classList.add('split-columns');
        
        for (let i = 0; i < mid_point; i++) {
            create_simple_player_row(players_by_before[i], ranking_left_body, players_by_before[i][before_key]);
        }
        for (let i = mid_point; i < players_by_before.length; i++) {
            create_simple_player_row(players_by_before[i], ranking_right_body, players_by_before[i][before_key]);
        }
    } else {
        ranking_columns.classList.remove('split-columns');
        for (let i = 0; i < players_by_before.length; i++) {
            create_simple_player_row(players_by_before[i], ranking_left_body, players_by_before[i][before_key]);
        }
    }
    
    // Wait showing before scores
    console.log(`${log_prefix} Waiting ${TIME_BEFORE_TRANSITION}ms showing before scores...`);
    await new Promise(r => setTimeout(r, TIME_BEFORE_TRANSITION));
    
    // Fade out
    console.log(`${log_prefix} Fading out...`);
    document.querySelectorAll('.ranking-row').forEach(row => {
        row.classList.add('fade-out');
    });
    await new Promise(r => setTimeout(r, TIME_TRANSITION_FADE_OUT));
    
    // Clear and rebuild with after scores
    console.log(`${log_prefix} Rebuilding with AFTER scores...`);
    ranking_left_body.innerHTML = '';
    ranking_right_body.innerHTML = '';
    
    if (needs_split) {
        for (let i = 0; i < mid_point; i++) {
            create_final_player_row(players_by_after[i], ranking_left_body, after_key);
        }
        for (let i = mid_point; i < players_by_after.length; i++) {
            create_final_player_row(players_by_after[i], ranking_right_body, after_key);
        }
    } else {
        for (let i = 0; i < players_by_after.length; i++) {
            create_final_player_row(players_by_after[i], ranking_left_body, after_key);
        }
    }
    
    // Fade in
    await new Promise(r => setTimeout(r, TIME_TRANSITION_FADE_IN));
    document.querySelectorAll('.ranking-row').forEach(row => {
        row.classList.add('fade-in');
    });
    
    // Show final state for longer
    console.log(`${log_prefix} Showing final table for ${TIME_TO_SEE_TABLE}ms...`);
    await new Promise(r => setTimeout(r, TIME_TO_SEE_TABLE));
    console.log(`${log_prefix} Animation complete`);
}

// Create a simple player row (with position column placeholder on the left)
function create_simple_player_row(player, table_body, coins) {
    let ranking_row = document.createElement("tr");
    ranking_row.classList.add('ranking-row');
    
    // Position change indicator (empty placeholder for "before" state)
    let position_cell = document.createElement("td");
    position_cell.className = 'position-change-cell';
    position_cell.innerHTML = ''; // Empty before transition
    ranking_row.appendChild(position_cell);
    
    let player_name_cell = document.createElement("td");
    player_name_cell.innerHTML = player.nick;
    ranking_row.appendChild(player_name_cell);
    
    let player_coins_cell = document.createElement("td");
    player_coins_cell.className = 'coins-cell';
    player_coins_cell.innerHTML = coins;
    ranking_row.appendChild(player_coins_cell);
    
    table_body.appendChild(ranking_row);
}

// Create final player row with coin change and position indicators
function create_final_player_row(player, table_body, coins_key) {
    let ranking_row = document.createElement("tr");
    ranking_row.classList.add('ranking-row');
    
    // Position change indicator (on the left)
    let position_cell = document.createElement("td");
    position_cell.className = 'position-change-cell';
    
    let pos_change = player.position_change || 0;
    if (pos_change > 0) {
        position_cell.innerHTML = `<span class="position-up">▲${pos_change}</span>`;
    } else if (pos_change < 0) {
        position_cell.innerHTML = `<span class="position-down">▼${Math.abs(pos_change)}</span>`;
    } else {
        position_cell.innerHTML = `<span class="position-same">=</span>`;
    }
    ranking_row.appendChild(position_cell);
    
    // Name cell
    let player_name_cell = document.createElement("td");
    player_name_cell.innerHTML = player.nick;
    ranking_row.appendChild(player_name_cell);
    
    // Coins cell with change indicator
    let player_coins_cell = document.createElement("td");
    player_coins_cell.className = 'coins-cell';
    
    let final_coins = player[coins_key];
    let coin_change = player.coin_change || 0;
    let sign = coin_change >= 0 ? '+' : '';
    let change_class = coin_change > 0 ? 'coin-gain' : (coin_change < 0 ? 'coin-loss' : '');
    
    if (coin_change !== 0) {
        player_coins_cell.innerHTML = `${final_coins} <span class="${change_class}">(${sign}${coin_change})</span>`;
    } else {
        player_coins_cell.innerHTML = final_coins;
    }
    ranking_row.appendChild(player_coins_cell);
    
    table_body.appendChild(ranking_row);
}

async function after_special_duel()
{
    special_duel_winner = sessionStorage.getItem('special_duel_winner');
    special_duel_prize = sessionStorage.getItem('special_duel_prize');
    
    sessionStorage.setItem('special_duel', false);
    sessionStorage.setItem('special_duel_player1', null);
    sessionStorage.setItem('special_duel_player2', null);
    sessionStorage.setItem('special_duel_prize', null);
    sessionStorage.setItem('special_duel_winner', null);

    // Get scores BEFORE prize is given (first table state)
    let scores_before_prize = await get_current_scores_for_regulation();
    
    await send_prize_to_winner(special_duel_winner, special_duel_prize, false);
    
    // Get scores AFTER prize (winner already lost coins)
    let scores_after_prize = await get_current_scores_for_regulation();
    
    regulated_players = await balance_inflation_deflation();
    console.log(regulated_players)
    await update_ranking_table(regulated_players, scores_before_prize, scores_after_prize);
    await new Promise(r => setTimeout(r, TIME_TO_SEE_TABLE));
    admin_next_game();
}

// Get the players scores and create the ranking table
async function get_available_prizes()
{
    await $.ajax({
        url: '../get_available_prizes/',
        type: 'GET',
        contentType: 'application/json;charset=UTF-8',
        success: function(all_prizes) 
        {
            candidate_prizes = all_prizes.filter(i => i.amount > 0);
            prizes_prob = candidate_prizes.map(x => x.prob);
            console.log(candidate_prizes)
            console.log(prizes_prob)
        }
    });

}

// Sort the players scores by coins and create the ranking table
function create_ranking_table(players_scores)
{
    display_ranking(); // Display all the ranking elements and hide the roulette elements
    
    let ranking_left_body = document.getElementById("tbody-ranking-left");
    let ranking_right_body = document.getElementById("tbody-ranking-right");
    let ranking_columns = document.querySelector('.ranking-columns');
    
    // Clear previous content
    ranking_left_body.innerHTML = '';
    ranking_right_body.innerHTML = '';

    // Sort the players by coins in a copy of the array
    let players_ranking = [...players_scores].sort((a, b) => (a.coins < b.coins) ? 1 : -1)
    let total_coins = 0;

    const SPLIT_THRESHOLD = 3;
    const needs_split = players_ranking.length >= SPLIT_THRESHOLD;

    if (needs_split)
    {
        ranking_columns.classList.add('split-columns');
        mid_point = Math.ceil(players_ranking.length / 2);
    
        // Left ranking table
        for (let i = 0; i < mid_point; i++)
        {
            create_player_row(players_ranking[i], ranking_left_body);
            total_coins += parseInt(players_ranking[i].coins);
        }
        // Right ranking table
        for (let i = mid_point; i < players_ranking.length; i++)
        {
            create_player_row(players_ranking[i], ranking_right_body);
            total_coins += parseInt(players_ranking[i].coins);
        }
    }
    else
    {
        ranking_columns.classList.remove('split-columns');
        for(i = 0; i < players_ranking.length; i++)
        {
            create_player_row(players_ranking[i], ranking_left_body);
            total_coins += parseInt(players_ranking[i].coins);
        }
    }

    return total_coins;
}

// Helper function to create a player row
function create_player_row(player, table_body) {
    let ranking_row = document.createElement("tr");
    
    let player_name_cell = document.createElement("td");
    player_name_cell.innerHTML = player.nick;
    ranking_row.appendChild(player_name_cell);
    
    let player_coins_cell = document.createElement("td");
    player_coins_cell.innerHTML = player.coins;
    ranking_row.appendChild(player_coins_cell);
    
    table_body.appendChild(ranking_row);
}

async function create_and_spin_roulettes(santa_player)
{
    display_roulettes(santa_player); // Display all the roulette elements and hide the ranking elements
    let players_roulette_div = document.getElementById("players_roulette_div");
    let prizes_roulette_div = document.getElementById("prizes_roulette_div");

    await $.ajax({
        url: '../create_roulettes/',
        type: 'GET',
        data: {santa_player: santa_player},
        contentType: 'application/json;charset=UTF-8',
    });

    let players_roulette_img = document.createElement("img");
    players_roulette_img.id = "players_roulette";
    players_roulette_img.src = "/static/img/players_roulette.png";
    players_roulette_div.appendChild(players_roulette_img);

    let prizes_roulette_img = document.createElement("img");
    prizes_roulette_img.id = "prizes_roulette";
    prizes_roulette_img.src = "/static/img/prizes_roulette.png";
    prizes_roulette_div.appendChild(prizes_roulette_img);

    if (santa_player != '')
    {
        santa_sound.play();
    }

    await new Promise(r => setTimeout(r, TIME_BEFORE_SPINNING));

    // Spin the roulettes
    let winner = spin_roulette(players_roulette_img, players_prob, candidate_players);
    let prize = spin_roulette(prizes_roulette_img, prizes_prob, candidate_prizes).type;

    let winner_name = winner.name; // Unique name
    let winner_nick = winner.nick; // For displaying purposes
    
    document.getElementById("enable_sounds").click(); // Trick browser to enable sounds
    spinning_roulette_audio.volume = 0.2;
    spinning_roulette_audio.currentTime = 3;
    spinning_roulette_audio.play();

    await new Promise(r => setTimeout(r, TIME_DURING_SPINNING));

    document.getElementById("result").innerHTML = winner_nick + " ha ganado <br> un " + prize;

    await new Promise(r => setTimeout(r, TIME_AFTER_SPINNING));

    return [winner_name, prize];
}

// Spin the roulette certain random degrees
function spin_roulette(roulette, probs, candidates)
{
    let extra_spins = 5;
    let extra_degrees = extra_spins * 360;

    let crutial_degrees = Math.floor(Math.random() * 360);
    console.log(crutial_degrees)
    let counterclockwise_spin = -1 *(extra_degrees + crutial_degrees)

    roulette.style.setProperty('--rotation_degrees', counterclockwise_spin + 'deg');
    let roulette_result = find_roulette_result(crutial_degrees, probs, candidates)
    roulette.classList.add("pie_spin_animation");
    
    return roulette_result
}

// Find the slice that is located in the spin degrees zone
function find_roulette_result(spin_degrees, probs, candidates)
{
    let spin_percentage = spin_degrees / 360;

    for (let i = 0; i < probs.length; i++)
    {
        // This is the player if the percentage is less than the relative frequency
        if (spin_percentage < probs[i])
        {
            console.log(candidates[i])
            return candidates[i];
        }
        else // If not, we substract the relative frequency to the percentage
        {
            spin_percentage -= probs[i];
        }
    }

    console.log('Error: roulette result not found, returning the last option');
    console.log(probs)
    return candidates[candidates.length - 1];
}

// Send the winner and the prize to the server and go to the next game
async function send_prize_to_winner(winner, prize, free)
{
    await $.ajax({
        url: '../send_prize_to_winner/',
        type: 'GET',
        data: {winner: winner, prize: prize, free: free},
        contentType: 'application/json;charset=UTF-8',
    });
}

// Decide if santa or special duel is called
function decide_call_special_duel_or_santa(winner_name)
{
    return new Promise(resolve => {
        $.ajax({
            url: '../decide_call_special_duel_or_santa/',
            type: 'GET',
            data: {winner: winner_name},
            contentType: 'application/json;charset=UTF-8',
            success: function(response) 
            {
                console.log(response)
                let chosen_player = response.chosen_player;
                let call_santa = response.call_santa;
                let call_special_duel = response.call_special_duel;
                resolve([chosen_player, call_santa, call_special_duel]);
            }
        });
    });
}

// Call santa
async function santa(chosen_player)
{
    console.log("Santa is called for " + chosen_player);
    await get_available_prizes();
    await create_and_spin_roulettes(chosen_player);
    await send_prize_to_winner(chosen_player, "Santa", true);
}

// Call special duel
function special_duel(player1, player2, prize)
{
    console.log("Special duel is called for " + player1 + " against " + player2);
    sessionStorage.setItem('special_duel', true);
    sessionStorage.setItem('special_duel_player1', player1);
    sessionStorage.setItem('special_duel_player2', player2);
    sessionStorage.setItem('special_duel_prize', prize);
    window.location.href = "../gunman_admin/";
}

// Balance inflation and deflation
async function balance_inflation_deflation()
{
    return new Promise((resolve, reject) => {
        $.ajax({
            url: '../balance_inflation_deflation/',
            type: 'GET',
            contentType: 'application/json;charset=UTF-8',
            success: function(response) 
            {
                console.log(response);
                let regulated_players = response.regulated_players;
                resolve(regulated_players);
            },
            error: function(err) {
                console.error("Error in balance_inflation_deflation:", err);
                reject(err); // Reject the promise if there's an error
            }
        });
    });
}

// Charge the ranking table with the new coins and express the change in the coins
async function update_ranking_table(regulated_players, scores_before_prize, scores_after_prize)
{
    console.log("[REGULATION ANIMATION] Starting update_ranking_table...");
    console.log("[REGULATION ANIMATION] Regulated players:", regulated_players);
    console.log("[REGULATION ANIMATION] Scores before prize:", scores_before_prize);
    console.log("[REGULATION ANIMATION] Scores after prize:", scores_after_prize);
    
    // Check if any player has regulation changes or if prize changed someone's coins
    let has_regulation_changes = regulated_players.some(p => p.coin_change !== 0);
    let has_prize_changes = scores_after_prize.some(p => {
        let before = scores_before_prize.find(b => b.name === p.name);
        return before && before.coins !== p.coins;
    });
    
    console.log("[REGULATION ANIMATION] Has regulation changes:", has_regulation_changes);
    console.log("[REGULATION ANIMATION] Has prize changes:", has_prize_changes);
    
    if (has_regulation_changes || has_prize_changes) {
        await create_animated_regulation_table(scores_before_prize, scores_after_prize, regulated_players);
    } else {
        console.log("[REGULATION ANIMATION] No changes, skipping animation");
    }
}

// Get current scores for regulation animation
async function get_current_scores_for_regulation() {
    return new Promise((resolve, reject) => {
        $.ajax({
            url: '../get_players_scores/',
            type: 'GET',
            contentType: 'application/json;charset=UTF-8',
            success: function(all_players) {
                console.log("[REGULATION ANIMATION] Current scores for regulation:", all_players);
                resolve(all_players);
            },
            error: function(err) {
                console.error("[REGULATION ANIMATION] Error getting scores:", err);
                reject(err);
            }
        });
    });
}

// Create animated table for regulation changes
// Shows two transitions:
// 1. "Before" state: scores_after_prize with indicators comparing to scores_before_prize
// 2. "After" state: scores after regulation with indicators comparing to scores_after_prize
async function create_animated_regulation_table(scores_before_prize, scores_after_prize, regulated_players) {
    console.log("[REGULATION ANIMATION] Creating animated regulation table...");
    display_ranking();
    
    let ranking_left_body = document.getElementById("tbody-ranking-left");
    let ranking_right_body = document.getElementById("tbody-ranking-right");
    let ranking_columns = document.querySelector('.ranking-columns');
    
    // Clear previous content
    ranking_left_body.innerHTML = '';
    ranking_right_body.innerHTML = '';
    
    // Build players data with all three states
    let players_data = scores_after_prize.map(player => {
        let before_prize = scores_before_prize.find(p => p.name === player.name);
        let reg = regulated_players.find(p => p.nick === player.nick);
        let regulation_change = reg ? reg.coin_change : 0;
        
        return {
            ...player,
            coins_first_table: before_prize ? before_prize.coins : player.coins,
            coins_after_prize: player.coins,
            coins_after_regulation: player.coins + regulation_change,
            prize_change: player.coins - (before_prize ? before_prize.coins : player.coins),
            regulation_change: regulation_change
        };
    });
    
    // Sort by first table scores (to calculate position changes vs first table)
    let sorted_by_first = [...players_data].sort((a, b) => b.coins_first_table - a.coins_first_table);
    // Sort by after prize scores
    let sorted_by_after_prize = [...players_data].sort((a, b) => b.coins_after_prize - a.coins_after_prize);
    // Sort by after regulation scores
    let sorted_by_after_regulation = [...players_data].sort((a, b) => b.coins_after_regulation - a.coins_after_regulation);
    
    // Calculate position changes for "before" state (after prize vs first table)
    players_data.forEach(player => {
        let pos_first = sorted_by_first.findIndex(p => p.name === player.name);
        let pos_after_prize = sorted_by_after_prize.findIndex(p => p.name === player.name);
        player.position_change_prize = pos_first - pos_after_prize; // vs first table
    });
    
    // Calculate position changes for "after" state (after regulation vs after prize)
    players_data.forEach(player => {
        let pos_after_prize = sorted_by_after_prize.findIndex(p => p.name === player.name);
        let pos_after_regulation = sorted_by_after_regulation.findIndex(p => p.name === player.name);
        player.position_change_regulation = pos_after_prize - pos_after_regulation; // vs after prize
    });
    
    console.log("[REGULATION ANIMATION] Players data:", players_data);
    
    const SPLIT_THRESHOLD = 3;
    const needs_split = sorted_by_after_prize.length >= SPLIT_THRESHOLD;
    const mid_point = Math.ceil(sorted_by_after_prize.length / 2);
    
    // FIRST: Display "after prize" state with indicators vs first table
    console.log("[REGULATION ANIMATION] Displaying AFTER PRIZE scores with indicators...");
    if (needs_split) {
        ranking_columns.classList.add('split-columns');
        for (let i = 0; i < mid_point; i++) {
            create_final_player_row_with_data(sorted_by_after_prize[i], ranking_left_body, 
                sorted_by_after_prize[i].coins_after_prize, 
                sorted_by_after_prize[i].prize_change, 
                sorted_by_after_prize[i].position_change_prize);
        }
        for (let i = mid_point; i < sorted_by_after_prize.length; i++) {
            create_final_player_row_with_data(sorted_by_after_prize[i], ranking_right_body, 
                sorted_by_after_prize[i].coins_after_prize, 
                sorted_by_after_prize[i].prize_change, 
                sorted_by_after_prize[i].position_change_prize);
        }
    } else {
        ranking_columns.classList.remove('split-columns');
        for (let i = 0; i < sorted_by_after_prize.length; i++) {
            create_final_player_row_with_data(sorted_by_after_prize[i], ranking_left_body, 
                sorted_by_after_prize[i].coins_after_prize, 
                sorted_by_after_prize[i].prize_change, 
                sorted_by_after_prize[i].position_change_prize);
        }
    }
    
    // Wait showing after prize scores
    console.log("[REGULATION ANIMATION] Waiting to show after prize scores...");
    await new Promise(r => setTimeout(r, TIME_BEFORE_TRANSITION));
    
    // Check if there are regulation changes to animate
    let has_regulation_changes = regulated_players.some(p => p.coin_change !== 0);
    
    if (has_regulation_changes) {
        // Fade out
        console.log("[REGULATION ANIMATION] Fading out...");
        document.querySelectorAll('.ranking-row').forEach(row => {
            row.classList.add('fade-out');
        });
        await new Promise(r => setTimeout(r, TIME_TRANSITION_FADE_OUT));
        
        // Clear and rebuild with after regulation scores
        console.log("[REGULATION ANIMATION] Rebuilding with AFTER REGULATION scores...");
        ranking_left_body.innerHTML = '';
        ranking_right_body.innerHTML = '';
        
        if (needs_split) {
            for (let i = 0; i < mid_point; i++) {
                create_final_player_row_with_data(sorted_by_after_regulation[i], ranking_left_body, 
                    sorted_by_after_regulation[i].coins_after_regulation, 
                    sorted_by_after_regulation[i].regulation_change, 
                    sorted_by_after_regulation[i].position_change_regulation);
            }
            for (let i = mid_point; i < sorted_by_after_regulation.length; i++) {
                create_final_player_row_with_data(sorted_by_after_regulation[i], ranking_right_body, 
                    sorted_by_after_regulation[i].coins_after_regulation, 
                    sorted_by_after_regulation[i].regulation_change, 
                    sorted_by_after_regulation[i].position_change_regulation);
            }
        } else {
            for (let i = 0; i < sorted_by_after_regulation.length; i++) {
                create_final_player_row_with_data(sorted_by_after_regulation[i], ranking_left_body, 
                    sorted_by_after_regulation[i].coins_after_regulation, 
                    sorted_by_after_regulation[i].regulation_change, 
                    sorted_by_after_regulation[i].position_change_regulation);
            }
        }
        
        // Fade in
        await new Promise(r => setTimeout(r, TIME_TRANSITION_FADE_IN));
        document.querySelectorAll('.ranking-row').forEach(row => {
            row.classList.add('fade-in');
        });
        
        // Show final state
        console.log("[REGULATION ANIMATION] Showing final table...");
        await new Promise(r => setTimeout(r, TIME_TO_SEE_TABLE));
    }
    
    console.log("[REGULATION ANIMATION] Animation complete");
}

// Create a player row with specific coin value, coin change, and position change
function create_final_player_row_with_data(player, table_body, coins, coin_change, position_change) {
    let ranking_row = document.createElement("tr");
    ranking_row.classList.add('ranking-row');
    
    // Position change indicator (on the left)
    let position_cell = document.createElement("td");
    position_cell.className = 'position-change-cell';
    
    if (position_change > 0) {
        position_cell.innerHTML = `<span class="position-up">▲${position_change}</span>`;
    } else if (position_change < 0) {
        position_cell.innerHTML = `<span class="position-down">▼${Math.abs(position_change)}</span>`;
    } else {
        position_cell.innerHTML = `<span class="position-same">=</span>`;
    }
    ranking_row.appendChild(position_cell);
    
    // Name cell
    let player_name_cell = document.createElement("td");
    player_name_cell.innerHTML = player.nick;
    ranking_row.appendChild(player_name_cell);
    
    // Coins cell with change indicator
    let player_coins_cell = document.createElement("td");
    player_coins_cell.className = 'coins-cell';
    
    let sign = coin_change >= 0 ? '+' : '';
    let change_class = coin_change > 0 ? 'coin-gain' : (coin_change < 0 ? 'coin-loss' : '');
    
    if (coin_change !== 0) {
        player_coins_cell.innerHTML = `${coins} <span class="${change_class}">(${sign}${coin_change})</span>`;
    } else {
        player_coins_cell.innerHTML = coins;
    }
    ranking_row.appendChild(player_coins_cell);
    
    table_body.appendChild(ranking_row);
}


function display_ranking()
{ // Make ranking visible and roulette invisible
    document.getElementById("title").innerHTML = "Ranking";
    document.getElementById("ranking_container").style="display:flex;";
    document.getElementById("roulettes_container").style="display:none;";
    document.getElementById("result").style="display:none;";
}

function display_roulettes(santa_player)
{ // Make ranking invisible and roulette visible
    if (santa_player != '')
    {
        document.getElementById("title").innerHTML = "Regalo de Santa";
    }
    else
    {
        document.getElementById("title").innerHTML = "Premios";
    }
    document.getElementById("ranking_container").style="display:none;";
    document.getElementById("roulettes_container").style="display:flex;";
    document.getElementById("result").style="display:flex;";
}
