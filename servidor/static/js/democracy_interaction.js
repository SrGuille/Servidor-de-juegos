function send_move(move)
{
    $.ajax({
        url: "/send_player_move",
        type: "GET",
        data: {move:move},
        success: function(response) {
            console.log(response);
        }
    });
}

function get_my_team()
{
    $.ajax({
        url: "/get_my_team",
        type: "GET",
        success: function(response) {
            document.getElementById("team").innerHTML = response.team;
        }
    });
}