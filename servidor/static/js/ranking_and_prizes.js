var candidate_players = [];
var players_prob = []; 
var candidate_prizes = [];
var prizes_prob = []
santa_sound = new Audio('/static/sounds/santa.mp3');

async function get_ranking_and_spin_roulettes()
{
    await get_ranking_from_scores();
    await get_available_prizes();
    await new Promise(r => setTimeout(r, 5000));
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
    let regulated_players = await balance_inflation_deflation();
    console.log(regulated_players)
    await update_ranking_table(regulated_players);
    await new Promise(r => setTimeout(r, 5000));
    await admin_next_game();
    //}
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

    await send_prize_to_winner(special_duel_winner, special_duel_prize, false);
    regulated_players = await balance_inflation_deflation();
    console.log(regulated_players)
    await update_ranking_table(regulated_players);
    await new Promise(r => setTimeout(r, 5000));
    admin_next_game();
}

// Get the players scores and create the ranking table
async function get_ranking_from_scores()
{
    await $.ajax({
        url: '../get_players_scores/',
        type: 'GET',
        contentType: 'application/json;charset=UTF-8',
        success: function(all_players) 
        {
            console.log(all_players)
            total_coins = create_ranking_table(all_players);
            // Remove the players with 0 coins
            candidate_players = all_players.filter(i => i.coins > 0)
            players_prob = candidate_players.map(x => x.coins / total_coins);
            console.log(candidate_players)
            console.log(players_prob)
        }
    });

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

    await new Promise(r => setTimeout(r, 5000));

    // Spin the roulettes
    let winner = spin_roulette(players_roulette_img, players_prob, candidate_players);
    let prize = spin_roulette(prizes_roulette_img, prizes_prob, candidate_prizes).type;

    let winner_name = winner.name; // Unique name
    let winner_nick = winner.nick; // For displaying purposes
    
    document.getElementById("enable_sounds").click(); // Trick browser to enable sounds
    spinning_roulette_audio.volume = 0.2;
    spinning_roulette_audio.currentTime = 3;
    spinning_roulette_audio.play();

    await new Promise(r => setTimeout(r, 6000));

    document.getElementById("result").innerHTML = winner_nick + " ha ganado <br> un " + prize;

    await new Promise(r => setTimeout(r, 6000));

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
async function update_ranking_table(regulated_players)
{
    console.log(regulated_players)
    await get_ranking_from_scores();
    let ranking_left_body = document.getElementById("tbody-ranking-left");
    let ranking_right_body = document.getElementById("tbody-ranking-right");
    console.log('new ranking table')

    // Update both sides of the ranking table
    update_ranking_side(ranking_left_body, regulated_players);
    update_ranking_side(ranking_right_body, regulated_players);
}
    
function update_ranking_side(ranking_side, regulated_players)
{
    console.log(regulated_players)
    // Iterate through table rows
    for(let i = 0; i < ranking_side.rows.length; i++) {
        let row = ranking_side.rows[i];
        let player_nick = row.cells[0].innerHTML;
        let regulated_player = null;
        for (let j = 0; j < regulated_players.length; j++) 
        {
            if (regulated_players[j].nick === player_nick) {
                regulated_player = regulated_players[j];
                break; // Stop looping once a match is found
            }
        }        
        if (regulated_player != null) {
            update_player_row(row, regulated_player);
        }
    }
}

function update_player_row(player_row, regulated_player)
{
    let coin_change = regulated_player.coin_change;
    if (coin_change > 0)
    {
        sign = '+';
    }
    else
    {
        sign = '';
    }
    player_row.cells[1].innerHTML = `${player_row.cells[1].innerHTML} (${sign}${coin_change})`;
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
