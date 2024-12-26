let duel_players = {};
let duel_players_names = [];
let next_duel_new_players = {};
let next_duel_new_players_names = [];

// Double sounds to be able to play them at the same time
shoot_sound_1 = new Audio("/static/sounds/gunman/shoot.mp3"); 
shoot_sound_2 = new Audio("/static/sounds/gunman/shoot.mp3");
reload_sound_1 = new Audio("/static/sounds/gunman/reload.mp3");
reload_sound_2 = new Audio("/static/sounds/gunman/reload.mp3");
shield_sound = new Audio("/static/sounds/gunman/shield.mp3");
western_sound = new Audio("/static/sounds/gunman/western.mp3");

image_path = "/static/img/gunman/";
/*shoot_image = "/static/img/gunman/shoot.png";
reload_image = "/static/img/gunman/reload.png";
shield_image = "/static/img/gunman/shield.png";*/

game_id = 3 // Gunman

async function play_rey_de_la_pista()
{
    duel_players = {};
    duel_players_names = [];
    next_duel_new_players = {};
    next_duel_new_players_names = [];

    end_game = false;
    await create_initial_duel(); // We know the two players
    display_players_duel(duel_players, false, null);
    //await new Promise(r => setTimeout(r, 5000)); // Wait 5 seconds to start the duel
    players_changed = true;
    while (!end_game)
    {
        display_message("Duelo");
        await notify_clients_game_ready(game_id) // Tell them to rejoin the game
        display_players_duel(duel_players, false, null);
        if (players_changed) // Leave some time to prepare for the duel
        {
            western_sound.play();
            await new Promise(r => setTimeout(r, 4000)); // Wait more seconds to start the duel
            players_changed = false;
        }

        // Start listening, but don't wait for it to resolve yet
        let listeningPromise = listen_in_game_room();

        // Do the countdown now (we are already listening in background!)
        await countdown(); // 4 seconds

        /* Only now await the listening promise. If it got the message during countdown,
        it will resolve immediately. If not, we'll wait until the message comes.
        */
        await listeningPromise;

        await duel_step();
        let result = check_duel_result(duel_players);
        display_players_duel(duel_players, true, result); 
        await new Promise(r => setTimeout(r, 3000)); // Wait 3 seconds to see the result
        end_game = handle_duel_after_result(result);

        if (result.loser != null) {
            display_message_box_result(result);
            players_changed = true;
        }
    }
    // Return to normal state for prizes
    await set_can_players_join(false); 
    await new Promise(r => setTimeout(r, 5000)); // Wait 5 seconds 
    window.location.href = "../ranking_and_prizes/";
}

function handle_duel_after_result(result)
{
    end_game = false;
    if (result.loser != null) // There is a loser
        {
            if (next_duel_new_players_names.length > 0) // There are more players to add
            {
                if (result.winner == null) // Both players died, replace both (the order doesn't matter)
                {
                    // Remove both players
                    delete duel_players[duel_players_names[0]];
                    delete duel_players[duel_players_names[1]];
                    // Add the new players
                    duel_players[next_duel_new_players_names[0]] = next_duel_new_players[next_duel_new_players_names[0]];
                    duel_players[next_duel_new_players_names[1]] = next_duel_new_players[next_duel_new_players_names[1]];
                }
                else if (result.winner == duel_players_names[0]) // Replace the loser with the new player (the only one at the next_duel_new_players)
                {
                    delete duel_players[duel_players_names[1]];
                    duel_players[next_duel_new_players_names[0]] = next_duel_new_players[next_duel_new_players_names[0]];
                }
                else // Number 1 has won, replace the loser with the new player (the only one at the next_duel_new_players)
                {   
                    delete duel_players[duel_players_names[0]];
                    duel_players[next_duel_new_players_names[0]] = next_duel_new_players[next_duel_new_players_names[0]];
                }
                duel_players_names = Object.keys(duel_players); // Update the names
            }
            else // End of the "rey de la pista", no more players
            {
                end_game = true;
            }
        }
    return end_game;
}

async function play_special_duel(player1, player2)
{   
    duel_players = {};
    duel_players_names = [];

    end_game = false;
    await create_special_duel(player1, player2);
    await new Promise(r => setTimeout(r, 5000)); // Prepare for the duel

    // Show the lives of the players
    document.getElementById("lives").style.display = "block";

    while (!end_game)
    {
        display_message("Duelo");
        await notify_clients_game_ready(game_id) // Tell them to rejoin the game
        display_players_special_duel(duel_players, false, null);

        // Start listening, but don't wait for it to resolve yet
        let listeningPromise = listen_in_game_room();

        // Do the countdown now (we are already listening in background!)
        await countdown(); // 4 seconds

        /* Only now await the listening promise. If it got the message during countdown,
        it will resolve immediately. If not, we'll wait until the message comes.
        */
        await listeningPromise;

        await special_duel_step();
        let special_duel_result = check_special_duel_result(duel_players);
        display_players_special_duel(duel_players, true, special_duel_result);
        await new Promise(r => setTimeout(r, 3000)); // Wait 3 seconds to see the result

        if (special_duel_result.winner != null) // The loser has died (lives = 0)
        {
            end_game = true;
            display_message_box_result(special_duel_result);
        }
    }
    await set_can_players_join(false); 
}

async function duel_step()
{
    await $.ajax({
        url: "../duel_step",
        type: "GET",
        success: function(response) { 
            // We need to see the result of the current duel (duel_players) and the next duel new players (next_duel_new_players)
            duel_players = response.current_duel_players;
            duel_players_names = Object.keys(duel_players);
            next_duel_new_players = response.next_duel_new_players;
            next_duel_new_players_names = Object.keys(next_duel_new_players);
        }
    });
}

async function special_duel_step()
{
    await $.ajax({
        url: "../special_duel_step",
        type: "GET",
        success: function(response) {
            // The next duel is going to be the same as the current one as players are not changing
            duel_players = response.duel_players;
            duel_players_names = Object.keys(duel_players);
        }
    });
}

async function create_initial_duel()
{
    await $.ajax({
        url: "../create_initial_duel",
        type: "GET",
        success: function(response) {
            duel_players = response.duel_players;
            duel_players_names = Object.keys(duel_players);
        }
    });
}

function check_duel_result(duel_players) {
    let action1 = duel_players[duel_players_names[0]].action;
    let action2 = duel_players[duel_players_names[1]].action;
    let result = {
        winner: null,
        loser: null
    };
    if (action1 === "shoot" && action2 === "shoot") // Both players die, play shoot sound twice
    {
        result.winner = null;
        result.loser = [duel_players_names[0], duel_players_names[1]];
        play_two_sounds(shoot_sound_1, shoot_sound_2);
    }
    else if (action1 === "shoot" && action2 === "reload") 
    {
        result.winner = duel_players_names[0];
        result.loser = duel_players_names[1];
        play_two_sounds(reload_sound_1, shoot_sound_1); // Reload first, then shoot
    } 
    else if (action1 === "reload" && action2 === "shoot") {
        result.winner = duel_players_names[1];
        result.loser = duel_players_names[0];
        play_two_sounds(reload_sound_1, shoot_sound_1); // Reload first, then shoot
    }
    else if (action1 === "reload" && action2 === "reload") 
    {
        play_two_sounds(reload_sound_1, reload_sound_2); // Reload sound twice
    }
    else if (action1 === "shield" && action2 === "shoot" || action1 === "shoot" && action2 === "shield") 
    {
        play_two_sounds(shoot_sound_1, shield_sound); // Shoot first, then shield
    }
    else if (action1 === "shield" && action2 === "reload" || action1 === "reload" && action2 === "shield") 
    {
        reload_sound_1.play(); // Play reload sound only (the shield sound is only if it gets shot)
    }

    // If both shoot or any other combination, winner/loser remain null
    return result;
}

// Play sound 1, small delay, then play sound 2
async function play_two_sounds(sound1, sound2)
{
    sound1.play();
    await new Promise(r => setTimeout(r, 200)); // Wait 1 second
    sound2.play();
}

async function create_special_duel(player1, player2)
{
    await $.ajax({
        url: "../create_special_duel",
        type: "GET",
        data: {player1: player1, player2: player2},
        success: function(response) {
            duel_players = response.duel_players;
            duel_players_names = Object.keys(duel_players);
        }
    });
}

function check_special_duel_result(duel_players)
{
    let lives1 = duel_players[duel_players_names[0]].lives;
    let lives2 = duel_players[duel_players_names[1]].lives;
    let result = {
        winner: null,
        loser: null
    };
    if (lives1 == 0 && lives2 == 0) // Both players died
    {
        result.winner = null;
        result.loser = [duel_players_names[0], duel_players_names[1]];
    }
    else if (lives1 == 0)
    {
        result.winner = duel_players_names[1];
        result.loser = duel_players_names[0];
    }
    else if (lives2 == 0)
    {
        result.winner = duel_players_names[0];
        result.loser = duel_players_names[1];
    }
    return result;
}

function display_players_duel(duel_players, after_duel, result)
{
    // Iterate through the dictionary entries
    let player_id = 1;
    for (let [name, data] of Object.entries(duel_players)) {
        let bullets = data.bullets;
        let shields = data.shields;
        let action = data.action;
        display_player_duel(player_id, name, bullets, shields, action, result, after_duel);
        player_id++;
    }
}

function display_players_special_duel(duel_players, after_duel, result_special_duel)
{
    let player_id = 1;
    for (let [name, data] of Object.entries(duel_players)) {
        let bullets = data.bullets;
        let action = data.action;
        let shields = data.shields;
        let lives = data.lives;
        display_player_special_duel(player_id, name, bullets, shields, lives, action, result_special_duel, after_duel);
        player_id++;
    }
}

function display_player_duel(player_id, name, bullets, shields, action, result, after_duel) {
    console.log(player_id, name, bullets, shields, action, result, after_duel);
    let player_div = document.getElementById("player" + player_id);
    
    let name_div = player_div.querySelector(".name");
    name_div.innerHTML = name;

    let bullets_div = player_div.querySelector("#bullet-count");
    bullets_div.innerHTML = bullets;

    let shields_div = player_div.querySelector("#shield-count");
    shields_div.innerHTML = shields;

    let action_div = player_div.querySelector(".action");
    let action_image = action_div.querySelector("#action_image");

    if (!after_duel)
    {
        action_image.style.display = "none";
    }
    else
    {
        // add the image according to the action
        action_image.style.display = "block";
        action_image.src = image_path + action + ".png";
    }
}

function display_message_box_result(result) {
    let message_box = document.getElementById("message-box");
    
    if (result.winner != null) {
        message_box.innerHTML = result.winner +" ha ganado!";
    }
    else { // Can't happen in the special duel
        message_box.innerHTML = result.loser[0] +" y "+ result.loser[1] +" han muerto";
    }
}

function display_message(message) {
    let message_box = document.getElementById("message-box");
    message_box.innerHTML = message;
}

function display_player_special_duel(player_id, name, bullets, shields, lives, action, result_special_duel, after_duel) {
    console.log(player_id, name, bullets, shields, lives, action, result_special_duel, after_duel);
    let player_div = document.getElementById("player" + player_id);
    
    let name_div = player_div.querySelector(".name");
    name_div.innerHTML = name;

    let bullets_div = player_div.querySelector("#bullet-count");
    bullets_div.innerHTML = bullets;

    let shields_div = player_div.querySelector("#shield-count");
    shields_div.innerHTML = shields;

    let lives_div = player_div.querySelector("#lives-count");
    lives_div.innerHTML = lives;

    let action_div = player_div.querySelector(".action");
    let action_image = action_div.querySelector("#action_image");

    if (!after_duel)
    {
        action_div.style.display = "none";
    }
    else
    {
        action_div.style.display = "block";
        action_image.src = image_path + action + ".png";
    }
}

async function countdown()
{
    document.getElementById("enable_sounds").click(); // Trick browser to enable sounds
    document.getElementById("message-box").innerHTML = "";
    arcade_jump_audio.volume = 0.7;
    arcade_jump_audio.play();
    pistolero = ["Pis","to","le","ro!"]
    for(let i = 0; i < 4; i++)
    {
        document.getElementById("message-box").innerHTML += pistolero[i];
        arcade_jump_audio.play();
        await new Promise(r => setTimeout(r, 1000)); //Wait 1 second
        arcade_jump_audio.pause();
    }
}