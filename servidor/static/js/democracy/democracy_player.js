player_name = sessionStorage.getItem("player_name");

if(player_name == null) //If the player is not logged in, redirect to the login page
{
    window.location.href = "../";
}

go_to_wait_screen_after_game();


/*
function send_move(move)
{
    console.log(move)
    $.ajax({
        url: "../send_player_move",
        type: "GET",
        data: {move:move, player_name:player_name},
        success: function(response) {
            console.log(response);
        }
    });
}
*/

async function get_my_team()
{
    await new Promise(r => setTimeout(r, 2000));
    $.ajax({
        url: "../get_my_team",
        type: "GET",
        data: {player_name:player_name},
        success: function(response) {
            paint_team(response.team)
        }
    });
}

// Paints the team label with the correct color
function paint_team(team)
{
    const teamElement = document.getElementById("team");

    // Actualiza el texto del equipo
    teamElement.innerHTML = team;

    // Cambia la clase según el equipo
    if (team.toLowerCase() === "verde") {
        teamElement.classList.add("team-green");
    } else if (team.toLowerCase() === "rojo") {
        teamElement.classList.add("team-red");
    }

    forceRedraw(teamElement);
}

function forceRedraw(element) {
    element.style.display = "none"; // Oculta temporalmente el elemento
    element.offsetHeight; // Forzar reflujo
    element.style.display = ""; // Restablece el estilo
}


async function go_to_wait_screen_after_game()
{
    await new Promise(r => setTimeout(r, 55000));
    sessionStorage.setItem("played", true) //Set the played flag to true
    window.location.href = "../wait_room/";
}

/*
This function sends the move to the server synched with the server clock
If the player sends a new move before the second is over, it will be sent when the second is over
If the player sends more moves after that, only the last one will be sent at the end of the second 
*/
function try_send_move(move) {
    const now = Date.now();
    const time_elapsed = now - last_move_try_time;  // How much time has passed since last move

    // If there's no previous move, try to send now (it will be accepted if the game is ready)
    if (time_until_next_second == -1) {
        send_move(move);
        return;
    }

    // We've waited longer than time_until_next_second, we're in a new second
    if (time_elapsed >= time_until_next_second) {
        send_move(move);
        return;
    }

    // We have already sent a move in this second, we have to wait until the next second
    if (timeout_id !== null) { // Clear any previous scheduled send during this second
        clearTimeout(timeout_id);
        timeout_id = null;  // Reset the timeout ID
        console.log("Timeout cleared");
    }
    
    // How much time is left until the next second
    const remaining_time = time_until_next_second - time_elapsed;
    
    timeout_id = setTimeout(() => { // Schedule the move for the start of the next second
        if (move) {
            send_move(move);
        }
    }, remaining_time);
}

let time_until_next_second = -1;  // Time until next second from server
let last_move_try_time = 0;   // When tried to send the move
let timeout_id = null;   // Timeout for scheduled move

function send_move(move) {
    clearTimeout(timeout_id); // Clear any previous scheduled send during this second
    last_move_try_time = Date.now();  // Track when tried to send the move
    $.ajax({
        url: "../send_player_move",
        type: "GET",
        data: {move: move, player_name: player_name},
        success: function(response) {
            time_until_next_second = response.time_until_next_second;
        }
    });
}