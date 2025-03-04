/*
    This file contains the functions to handle the redirects to the games
    The basic idea is that when previous game ends, we want to know what game to play next.
    To do so, the admin will check if there is a game to play or if there is not manually select one in the menu.
    Once the next game is known, the admin will display it and will send a message to all the clients to join it.
*/

admin_redirects = ['../roulette_admin/', '../hangman_admin/', '../democracy_admin/', '../gunman_admin/', '../bnumber_admin/']
player_redirects = ['../roulette_player/', '../hangman_player/', '../democracy_player/', '../gunman_player/', '../bnumber_player/']

// Set the game to play with rounds and redirect to it
function set_next_game(game_id)
{
    rounds = document.getElementById('rounds' + game_id.toString()).value
    console.log(rounds);
    //Django view to set game
    $.ajax({
        url: '../set_game/',
        type: 'GET',
        contentType: 'application/json;charset=UTF-8',
        data: {game:game_id, rounds:rounds},
        success: function(response)
        {
            console.log(response);
            notify_clients_game_ready(game_id);
            window.location.href = admin_redirects[game_id];
        }
    });
}

// Called by the admin to transition to the next game
async function transition_to_next_game()
{
    return new Promise(function(resolve, reject) {
        $.ajax({
            url: '../transition_to_next_game/',
            type: 'GET',
            contentType: 'application/json;charset=UTF-8',
            success: function(response) 
            {
                game_id = parseInt(response.game_id)
                resolve(game_id);
            }
        });
    });
}

/*
It is called by the players and gets the next game to join from the server if there is one
(if there is no game to play it returns -1)
*/
async function get_ready_to_join_game() {
    return new Promise(function(resolve, reject) {
        $.ajax({
            url: '../get_ready_to_join_game/',
            type: 'GET',
            contentType: 'application/json;charset=UTF-8',
            success: function(response) {
                var game_id = parseInt(response.game_id);
                console.log(game_id);
                resolve(game_id); 
            }
        });
    });
}

/* 
Called by a player when he wants to play the next game:
- If it is called by the player just after having played a game it will redirect to the wait room.
- (Login + random situation): it gets the next game from the server and redirects to it if there is one
  If there is no game to play it goes to the wait room to wait for the admin to select a game
*/
async function play_next_game()
{
    var played = (sessionStorage.getItem("played") === 'true');
    // If the player has already played its turn, redirect to the wait room
    if(played) 
    {
        console.log("Ya has jugado tu turno, espera a que el resto de jugadores acaben");
        listen_in_wait_room();
    }
    else 
    {
        var game_id = await get_ready_to_join_game();
        if(game_id != -1) // There is a game to play
        {
            play_game(game_id);
        }
        else // No game to play
        {
            console.log("No hay juego listo, redirigiendo a la sala de espera...");
            listen_in_wait_room();
        }
    } 
}

/*
Called by the admin to get the next game to play
If there is a game to play it redirects to it
If there is no game to play it redirects to the game selector
*/
async function admin_next_game()
{
    game_id = await transition_to_next_game();
    if(game_id != -1) // We have an scheduled game to play
    {
        admin_game(game_id);
    }
    else
    {
        window.location.href = '../game_selector/';
    }
}

/*
Old function to wait until the game is ready

async function wait_until_ready_to_play_game()
{
    player_name = sessionStorage.getItem("player_name");
    if(player_name == null) //If the player is not logged in, redirect to the login page
    {
        window.location.href = "../";
    }

    await new Promise(r => setTimeout(r, 5000));

    $.ajax({
        url: '../redirect_to_ready_to_play_game/',
        type: 'GET',
        contentType: 'application/json;charset=UTF-8',
        data: {player_name:player_name},
        success: function(response) 
        {
            window.location.href = response.redirect;
        }
    });
}*/

// Join the wait room and return the socket
async function join_wait_room(client_name)
{
    let wait_room_url = `ws://${window.location.host}/ws/wait_room/`;
    if (client_name != null) {
        // Add client_name as a query parameter
        wait_room_url += `?client_name=${encodeURIComponent(client_name)}`;
    }
    let wait_room_socket = new WebSocket(wait_room_url);
    await new Promise(resolve => wait_room_socket.addEventListener("open", resolve));
    return wait_room_socket;
}

// admin calls this to notify all clients in the wait room that the game is ready
async function notify_clients_game_ready(game_id)
{
    wait_room_socket = await join_wait_room();
    wait_room_socket.send(JSON.stringify({
        'game_id': game_id.toString(),
    }));
    wait_room_socket.close();
}

// admin calls this to notify specific clients by name in the wait room that the game is ready
async function notify_specific_clients_game_ready(game_id, clients) {
    // Join the wait room as the admin with a known name (optional)
    let wait_room_socket = await join_wait_room("admin");
    wait_room_socket.send(JSON.stringify({
        'game_id': game_id.toString(),
        'clients': clients // array of client names, e.g. ['Alice', 'Bob']
    }));
    wait_room_socket.close();
}

// Player listens in the wait room socket and goes to the game when the admin sends the message
async function listen_in_wait_room(client_name)
{   
    // Join by sending the client name
    wait_room_socket = await join_wait_room(client_name);
    wait_room_socket.onmessage = function(e) {
        var data = JSON.parse(e.data);
        game_id = data['game_id'];
        wait_room_socket.close();
        play_game(game_id);
    };
}

// Notify players and admin that the game is ready and redirect to it
function admin_game(game_id)
{
    notify_clients_game_ready(game_id)
    window.location.href = admin_redirects[game_id];
}

// Played flag is set to false and redirect to the game
function play_game(game_id)
{
    sessionStorage.setItem("played", false) //Set the played flag to false
    window.location.href = player_redirects[game_id];
}

/* 
Stablish that the current game can/can't be joined
*/
function set_can_players_join(can_join)
{
    return new Promise(function(resolve, reject) {
        $.ajax({
            url: '../set_can_players_join/',
            type: 'GET',
            contentType: 'application/json;charset=UTF-8',
            data: {can_join:can_join.toString()},
            success: function(response) 
            {
                resolve();
            }
        });
    });
}

/*
Stablish that the current game can/can't be interacted with
*/
function set_can_players_interact(can_interact)
{
    return new Promise(function(resolve, reject) {
        $.ajax({
            url: '../set_can_players_interact/',
            type: 'GET',
            contentType: 'application/json;charset=UTF-8',
            data: {can_interact:can_interact.toString()},
            success: function(response) 
            {
                resolve();
                console.log("Can players interact: " + can_interact);
            }
        });
    });
}