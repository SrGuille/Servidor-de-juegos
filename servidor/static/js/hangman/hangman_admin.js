images = ["{% static 'img/ahorcado/ahorcado10.png' %}", "{% static 'img/ahorcado/ahorcado08.png' %}", "{% static 'img/ahorcado/ahorcado06.png' %}", "{% static 'img/ahorcado/ahorcado04.png' %}", "{% static 'img/ahorcado/ahorcado02.png' %}", "{% static 'img/ahorcado/ahorcado00.png' %}"]

function display_sentence(sentence) 
{
    sentence_display = "";
    for(let i = 0; i < sentence.length; i++)
    {
        if(sentence[i] == ' ')
        {
            sentence_display += "&nbsp;&nbsp;";
        }
        else
        {
            sentence_display += sentence[i] + "&nbsp;";
        }
    }

    document.getElementById("hueco-palabra").innerHTML = sentence_display;
}

function get_sentence()
{
    $.ajax({
        url: '../create_sentence/',
        type: 'GET',
        contentType: 'application/json;charset=UTF-8',
        success: function(response)
        {
            console.log(response.partially_guessed_sentence)
            sentence = response.partially_guessed_sentence;
            display_sentence(sentence);
        }
    });

}

function change_image(step)
{
    document.getElementById("ahorcado").src = images[step];
}

// Wait for all players to bet before performing the step
async function wait_for_all_players_and_run()
{
    get_sentence();
    set_is_current_game_ready(true);
    all_guesses_sent = false;
    while (!all_guesses_sent)
    {
        await new Promise(r => setTimeout(r, 5000)); //Wait 5 seconds
        response = await $.ajax({
            url: '../get_remaining_interactions/',
            type: 'GET',
            contentType: 'application/json;charset=UTF-8'
        });

        if(response.remaining_interactions == "0")
        {
            all_guesses_sent = true;
        }
        
    }

}

async function play_game()
{
    step = 1;
    rounds = 5;
    while (step <= rounds)
    {
        await wait_for_all_players_and_run();
        round_winner_players = perform_step();
        if(round_winner_players.length > 0)
        {
            if(round_winner_players[0] == "Loss")
            {
                alert("You lost!");
                change_image(step);
            }
            else
            {
                set_winners(round_winner_players);
                change_image(0);
            }
            break;
        }
        else
        {
            change_image(step);
        }

        step += 1;
    }

    await new Promise(r => setTimeout(r, 10000)); //Wait 10 seconds

    window.location.href = "../ranking_and_prizes/";
    
}

// Perform a step of the game
async function perform_step()
{
    set_is_current_game_ready(false);
    response = await $.ajax({
        url: '../perform_step/',
        type: 'GET',
        contentType: 'application/json;charset=UTF-8'
    });

    set_hanged_candidates(response.hanged_candidades);
    set_partially_guessed_sentence(response.partially_guessed_sentence);
    round_winner_players = response.round_winner_players;

    return round_winner_players;

}

function set_hanged_candidates(hanged_candidades)
{
    hanged_candidades_string = "";
    for(let i = 0; i < hanged_candidades.length; i++)
    {
        candidate = hanged_candidades[i];
        hanged_candidades_string = hanged_candidades_string + candidate + "<br>";
    }

    document.getElementById('ahorcados').innerHTML = hanged_candidades_string;
}

function set_partially_guessed_sentence(partially_guessed_sentence)
{
    document.getElementById('sentence').innerHTML = partially_guessed_sentence;
}

function set_winners(winners)
{
    winners_string = "";
    for(let i = 0; i < winners.length; i++)
    {
        winner = winners[i];
        winners_string = winners_string + winner + "<br>";
    }

    document.getElementById('winners').innerHTML = winners_string;
}