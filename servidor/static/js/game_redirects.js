redirects = ['../roulette_host/', '../hangman_host/', '../democracy_host/', '../multibandits_host/']

// Set the game to play with rounds and redirect to it
function set_play_game(game_number)
{
    //table = document.getElementById("game_table");
    rounds = document.getElementById('rounds' + game_number.toString()).value
    //game_row = table.rows[game_number + 1] // +1 because of the header
    //rounds = game_row.cells[1].children[0].value; // Value of the input
    console.log(rounds);
    //Django view to set game
    $.ajax({
        url: '../set_game/',
        type: 'GET',
        contentType: 'application/json;charset=UTF-8',
        data: {game:game_number, rounds:rounds},
        success: function(response)
        {
            console.log(response);
            window.location.href = redirects[game_number];
        }
    });
}

// Get the next game (by configured rounds) and redirect to it
function play_next_game()
{
    $.ajax({
        url: '../get_next_game/',
        type: 'GET',
        contentType: 'application/json;charset=UTF-8',
        success: function(response) 
        {
            game_number = parseInt(response.game)
            if(game_number != -1) // We have a game to play (configured rounds)
            {
                window.location.href = redirects[game_number];
            }
            else // No game to play, go to game selector
            {
                window.location.href = '../game_selector/';
            }
        }
    });
}