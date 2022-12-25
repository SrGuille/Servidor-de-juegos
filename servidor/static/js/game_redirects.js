games = ['Ruleta', 'Ahorcado', "Democracia", "Tragaperras"]

redirects = ['../roulette_host/', '../hangman_host/', '../democracy_host/', '../multibandits_host/']

function play_game(game_number)
{
    table = document.getElementById("game_table");
    game_row = table.rows[game_number]
    game = game_row.cells[0].innerHTML;
    rounds = game_row.cells[1].innerHTML;

    //Django view to set game
    $.ajax({
        url: '../set_game/',
        type: 'GET',
        contentType: 'application/json;charset=UTF-8',
        data: {game:game, rounds:rounds},
        success: function(response)
        {
            console.log(response);
            window.location.href = redirects[game_number];
        }
    });
}