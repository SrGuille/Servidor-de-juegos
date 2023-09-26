var candidate_players = [];
var players_prob = []; 
var candidate_prizes = [];
var prizes_prob = []

async function get_ranking_and_spin_roulettes()
{
    await get_ranking_from_scores();
    await get_available_prizes();
    create_and_spin_roulettes();
}

// Get the players scores and create the ranking table
async function get_ranking_from_scores()
{

    $.ajax({
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

    $.ajax({
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
    ranking_table = document.getElementById("tbody-ranking");
    // Sort the players by coins in a copy of the array
    players_ranking = [...players_scores].sort((a, b) => (a.coins < b.coins) ? 1 : -1)
    total_coins = 0;

    for(i = 0; i < players_ranking.length; i++)
    {
        ranking_row = document.createElement("tr");
        player_name_cell = document.createElement("td");
        player_name_cell.innerHTML = players_ranking[i].nick; // Name is the nick
        ranking_row.appendChild(player_name_cell);
        
        player_coins_cell = document.createElement("td");
        player_coins_cell.innerHTML = players_ranking[i].coins;
        ranking_row.appendChild(player_coins_cell);
        total_coins += parseInt(players_ranking[i].coins);

        ranking_table.appendChild(ranking_row);

    }

    return total_coins;
}

async function create_and_spin_roulettes()
{
    await new Promise(r => setTimeout(r, 5000));

    players_roulette_div = document.getElementById("players_roulette_div");
    prizes_roulette_div = document.getElementById("prizes_roulette_div");

    await $.ajax({
        url: '../create_roulettes/',
        type: 'GET',
        contentType: 'application/json;charset=UTF-8',
    });

    document.getElementById("ranking").style="display:none;";
    document.getElementById("result").style="display:flex;";
    document.getElementById("indicador1").style="display:flex;";
    document.getElementById("indicador2").style="display:flex;";

    players_roulette_img = document.createElement("img");
    players_roulette_img.id = "players_roulette";
    players_roulette_img.src = "/static/img/players_roulette.png";
    players_roulette_div.appendChild(players_roulette_img);

    prizes_roulette_img = document.createElement("img");
    prizes_roulette_img.id = "prizes_roulette";
    prizes_roulette_img.src = "/static/img/prizes_roulette.png";
    prizes_roulette_div.appendChild(prizes_roulette_img);

    await new Promise(r => setTimeout(r, 5000));

    // Spin the roulettes
    winner = spin_roulette(players_roulette_img, players_prob, candidate_players);
    prize = spin_roulette(prizes_roulette_img, prizes_prob, candidate_prizes).type;

    winner_name = winner.name; // Unique name
    winner_nick = winner.nick; // For displaying purposes

    await new Promise(r => setTimeout(r, 6000));

    document.getElementById("result").innerHTML = winner_nick + " ha ganado <br> un " + prize;

    await new Promise(r => setTimeout(r, 10000));

    send_prize_to_winner(winner_name, prize);
}

// Spin the roulette certain random degrees
function spin_roulette(roulette, probs, candidates)
{
    extra_spins = 5;
    extra_degrees = extra_spins * 360;

    crutial_degrees = Math.floor(Math.random() * 360);
    console.log(crutial_degrees)
    counterclockwise_spin = -1 *(extra_degrees + crutial_degrees)

    roulette.style.setProperty('--rotation_degrees', counterclockwise_spin + 'deg');
    roulette_result = find_roulette_result(crutial_degrees, probs, candidates)
    roulette.classList.add("pie_spin_animation");
    
    return roulette_result
}

// Find the slice that is located in the spin degrees zone
function find_roulette_result(spin_degrees, probs, candidates)
{
    spin_percentage = spin_degrees / 360;

    for (i = 0; i < probs.length; i++)
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

    console.log('Error: spin percentage is greater than 1');
    console.log(probs)
    // If the percentage is greater than 1, we return the last player
    return candidates[candidates.length - 1];
}

// Send the winner and the prize to the server and go to the next game
function send_prize_to_winner(winner, prize)
{
    $.ajax({
        url: '../send_prize_to_winner/',
        type: 'GET',
        data: {winner: winner, prize: prize},
        contentType: 'application/json;charset=UTF-8',
        success: function(response) 
        {
            admin_next_game();
        }
    });
}