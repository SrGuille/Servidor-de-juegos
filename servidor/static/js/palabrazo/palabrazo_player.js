meme_sounds = ['android_meme.mp3', 'bababooey.mp3', 'doot_doot.mp3',
                'echo_fart.mp3', 'foghorn.mp3', 'metal_pipe.mp3',
                'moah.mp3', 'taco_bell.mp3', 'what_the_hell.mp3',
                'windows_xp.mp3']

victory_sounds = ['celebration1.mp3', 'congratulations.mp3']

player_name = sessionStorage.getItem("player_name");

if(player_name == null) //If the player is not logged in, redirect to the login page
{
    window.location.href = "../";
}

go_to_wait_screen_after_game();

async function send_guess(guess)
{
    valid = await validate_guess(guess);

    if(!valid)
    {
        play_meme_sound();
    }
    else
    {
        //play_victory_sound();
    }

    await new Promise(r => setTimeout(r, 500)); // Wait 0.5 seconds
    document.getElementById("respuesta").value = "";
}

async function validate_guess(guessed_word)
{
    console.log(guessed_word)
    return new Promise(function(resolve, reject) {
        $.ajax({
            url: "../send_player_guess",
            type: "GET",
            data: {player_name:player_name, guessed_word:guessed_word},
            success: function(response) {
                resolve(response.valid);
            }
        });
    });
}

async function check_game_has_finished()
{
    has_finished = false;
    return new Promise((resolve, reject) => {
        $.ajax({
            url: "../has_finished_palabrazo",
            type: "GET",
            success: function(response) {
                console.log(response)
                has_finished = response.has_finished;
                resolve(has_finished);
            },
            error: function(xhr, status, error) {
                reject(error);
            }
        });
    });
}

async function go_to_wait_screen_after_game()
{
    await new Promise(r => setTimeout(r, 50000)); //Wait 50 seconds
    for (let i = 0; i < 20; i++)
    {
        has_finished = await check_game_has_finished();
        if (has_finished)
        {
            console.log("Game has finished, going to wait screen...");
            break;
        }
        console.log("Game not finished yet, checking again in 10 seconds...");
        await new Promise(r => setTimeout(r, 10000)); //Wait 10 seconds
    }
    sessionStorage.setItem("played", true) //Set the played flag to true
    window.location.href = "../wait_room/";
}

function play_meme_sound()
{
    document.getElementById("enable_sounds").click(); // Trick browser to enable sounds
    meme_sound = meme_sounds[Math.floor(Math.random() * meme_sounds.length)];
    meme_audio = new Audio("/static/sounds/meme/" + meme_sound);
    meme_audio.play();
}

function play_victory_sound()
{
    document.getElementById("enable_sounds").click(); // Trick browser to enable sounds
    victory_sound = victory_sounds[Math.floor(Math.random() * victory_sounds.length)];
    victory_audio = new Audio("/static/sounds/victory/" + victory_sound);
    victory_audio.play();
}