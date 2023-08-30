player_name = sessionStorage.getItem("player_name");

if(player_name == null) //If the player is not logged in, redirect to the login page
{
    window.location.href = "../";
}

go_to_wait_screen_after_game();

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

function get_my_team()
{
    $.ajax({
        url: "../get_my_team",
        type: "GET",
        data: {player_name:player_name},
        success: function(response) {
            document.getElementById("team").innerHTML = response.team;
            console.log(response)
        }
    });
}


async function go_to_wait_screen_after_game()
{
    await new Promise(r => setTimeout(r, 42000));
    sessionStorage.setItem("played", true) //Set the played flag to true
    window.location.href = "../wait/";
}