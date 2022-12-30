player_name = sessionStorage.getItem("player_name");

if(player_name == null) //If the player is not logged in, redirect to the login page
{
    window.location.href = "../";
}

function send_guess(guess)
{
    console.log(guess)
    $.ajax({
        url: "../send_player_guess",
        type: "GET",
        data: {guess:guess, player_name:player_name},
        success: function(response) {
            console.log(response);
        }
    });
}