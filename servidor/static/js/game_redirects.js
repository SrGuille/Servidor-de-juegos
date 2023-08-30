/*
    This file contains the functions to handle the redirects to the games
    The basic idea is that when previous game ends, we want to know what game to play next.
    To do so, the admin will check if there is a game to play or if there is not manually select one in the menu.
    Once the next game is known, the admin will display it and will send a message to all the clients to join it.
*/

admin_redirects = ['../roulette_admin/', '../hangman_admin/', '../democracy_admin/', '../multibandits_admin/']
client_redirects = ['../roulette_client/', '../hangman_client/', '../democracy_client/', '../multibandits_client/']

// Set the game to play with rounds and redirect to it
function set_next_game(game_id)
{
    //table = document.getElementById("game_table");
    rounds = document.getElementById('rounds' + game_id.toString()).value
    //game_row = table.rows[game_id + 1] // +1 because of the header
    //rounds = game_row.cells[1].children[0].value; // Value of the input
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

async function get_ready_to_play_game() {
    return new Promise(function(resolve, reject) {
        $.ajax({
            url: '../get_ready_to_play_game/',
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

It it is called by the player just after having played a game it will redirect to the wait room
In any other case it gets the next game from the server and redirects to it if there is one
If there is no game to play it goes to the wait room to wait for the admin to select a game
*/
async function play_next_game()
{
    var played = (sessionStorage.getItem("played") === 'true');
    // If the player has already played its turn, redirect to the wait room
    if(played) 
    {
        listen_in_wait_room();
    }
    else
    {
        var game_id = await get_ready_to_play_game();
        if(game_id != -1) // There is a game to play
        {
            play_game(game_id);
        }
        else // No game to play
        {
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
    if(game_id != -1) // We have a game to play
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
async function join_wait_room()
{
    let wait_room_url = `ws://${window.location.host}/ws/wait_room/`;
    let wait_room_socket = new WebSocket(wait_room_url);
    await new Promise(resolve => wait_room_socket.addEventListener("open", resolve));
    return wait_room_socket;
}

// admin calls this to notify clients in the wait room that the game is ready
async function notify_clients_game_ready(game_id)
{
    wait_room_socket = await join_wait_room();
    wait_room_socket.send(JSON.stringify({
        'game_id': game_id.toString(),
    }));
    wait_room_socket.close();
}

// Listen to the wait room socket and redirect to the game when the admin sends the message
async function listen_in_wait_room()
{
    wait_room_socket = await join_wait_room();
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
    window.location.href = client_redirects[game_id];
}

/* 
Stablish that the current game can't be played, 
so no one can join it or interact with it 
*/
function not_ready_to_play_game()
{
    $.ajax({
        url: '../not_ready_to_play_game/',
        type: 'GET',
        contentType: 'application/json;charset=UTF-8'
    });
}

/*
Stablish that the current game is ready to be played,
so anyone can join it and interact with it
*/
function ready_to_play_game()
{
    // Listen to client calls
    $.ajax({
        url: '../ready_to_play_game/',
        type: 'GET',
        contentType: 'application/json;charset=UTF-8'
    });
}