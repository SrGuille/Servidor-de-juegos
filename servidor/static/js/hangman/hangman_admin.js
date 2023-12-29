images = ["/static/img/ahorcado/ahorcado10.png", 
        "/static/img/ahorcado/ahorcado08.png", 
        "/static/img/ahorcado/ahorcado06.png", 
        "/static/img/ahorcado/ahorcado04.png", 
        "/static/img/ahorcado/ahorcado02.png", 
        "/static/img/ahorcado/ahorcado00.png"]

victory_sounds = ["celebration.mp3",
                "congratulations.mp3"]

loss_sounds = ["horn.mp3",
            "mario_fail.mp3",
            'sad_trombone.mp3',
            'spongebob_fail.mp3',
            'wrong_buzzer.mp3']

game_id = 1 // Hangman

var partially_guessed_sentence = "";
var game_winners = []
var hang_step = 0
var pot = 75

async function display_sentence(sentence) 
{
    space_count = 0;
    sentence_display = "";
    for(let i = 0; i < sentence.length; i++)
    {
        if(sentence[i] == ' ')
        {
            space_count++;
            sentence_display += "&nbsp;&nbsp;";
            if (space_count == 6)
            {
                sentence_display += "<br>";
                space_count = 0;
            }
        }
        else
        {
            sentence_display += sentence[i] + "&nbsp;";
        }
    }

    document.getElementById("hueco-palabra").innerHTML = sentence_display;
}

// Get the initial censured sentence
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
            pot = response.pot_per_sentence_guess
            display_sentence(sentence);
            display_pot(pot);
        }
    });

}

function display_image(hang_step)
{
    document.getElementById("ahorcado").src = images[hang_step];
}

/* Wait for all players to bet before performing the step
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

}*/

async function play_hangman()
{
    game_end = false;
    await get_sentence();
    while (!game_end)
    {
        await set_can_players_join(true);
        await notify_clients_game_ready(game_id) // Tell them to rejoin the game
        await set_can_players_interact(true);
        await listen_in_game_room(); // Wait for all players to guess
        await set_can_players_join(false);
        await set_can_players_interact(false); 

        await perform_step();

        if(game_winners.length > 0) // It can have winners or the word 'Loss'
        {
            if(game_winners[0] == "Loss")
            {
                display_image(hang_step);
                display_loss();
                play_loss_sound();
            }
            else
            {
                display_winners(game_winners);
                play_victory_sound();
            }
            game_end = true;
        }
        else
        {
            console.log(partially_guessed_sentence, game_winners, hang_step, pot)

            display_sentence(partially_guessed_sentence);
            display_image(hang_step); // Change image if necessary
            display_pot(pot);
            await new Promise(r => setTimeout(r, 3000)); //Wait 5 seconds
        }
    }

    await new Promise(r => setTimeout(r, 10000)); //Wait 10 seconds

    window.location.href = "../ranking_and_prizes/";
    
}

// Perform a step of the game
async function perform_step()
{
    response = await $.ajax({
        url: '../perform_step/',
        type: 'GET',
        contentType: 'application/json;charset=UTF-8'
    });
    
    partially_guessed_sentence = response.partially_guessed_sentence;
    game_winners = response.game_winners;
    hang_step = response.hang_step;
    pot = response.pot_per_sentence_guess;

    console.log(partially_guessed_sentence, game_winners, hang_step, pot)
}

/*
function set_hanged_candidates(hanged_candidades)
{
    hanged_candidades_string = "";
    for(let i = 0; i < hanged_candidades.length; i++)
    {
        candidate = hanged_candidades[i];
        hanged_candidades_string = hanged_candidades_string + candidate + "<br>";
    }

    document.getElementById('ahorcados').innerHTML = hanged_candidades_string;
}*/

function display_pot(pot)
{
    document.getElementById('ahorcados').innerHTML = 'Bote: ' + pot + ' monedas';
}

function display_partially_guessed_sentence(partially_guessed_sentence)
{
    document.getElementById('sentence').innerHTML = partially_guessed_sentence;
}

function display_winners(winners)
{
    winners_string = "Ganadores: <br>";
    for(let i = 0; i < winners.length; i++)
    {
        winner = winners[i];
        winners_string = winners_string + winner + "<br>";
    }

    document.getElementById('ahorcados').innerHTML = winners_string;
}

function display_loss()
{
    document.getElementById('ahorcados').innerHTML = "¡Ahorcados!";
}

function play_victory_sound()
{
    document.getElementById("enable_sounds").click(); // Trick browser to enable sounds
    victory_sound = victory_sounds[Math.floor(Math.random() * victory_sounds.length)];
    victory_audio = new Audio("/static/sounds/victory/" + victory_sound);
    victory_audio.play();
}

function play_loss_sound()
{
    document.getElementById("enable_sounds").click(); // Trick browser to enable sounds
    loss_sound = loss_sounds[Math.floor(Math.random() * loss_sounds.length)];
    loss_audio = new Audio("/static/sounds/loss/" + loss_sound);
    loss_audio.play();
}