meme_sounds = ['android_meme.mp3', 'bababooey.mp3', 'doot_doot.mp3',
                'echo_fart.mp3', 'foghorn.mp3', 'metal_pipe.mp3',
                'moah.mp3', 'taco_bell.mp3', 'what_the_hell.mp3',
                'windows_xp.mp3']

player_name = sessionStorage.getItem("player_name");

if(player_name == null) //If the player is not logged in, redirect to the login page
{
    window.location.href = "../";
}

async function send_guess(guess)
{
    response = await validate_guess(guess);
    valid = response.valid;
    eliminated = response.eliminated;
    winner = response.winner;
    if(valid)
    {
        if(eliminated)
        {
            alert("Has fallado la frase :(");
        }

        await notify_player_has_interacted();
        sessionStorage.setItem("played", true) //Set the played flag to true
        window.location.href = "../wait_room/";
    }
    else
    {
        play_meme_sound();
    }
}

async function validate_guess(guess)
{
    console.log(guess)
    return new Promise(function(resolve, reject) {
        $.ajax({
            url: "../send_player_guess",
            type: "GET",
            data: {guess:guess, player_name:player_name},
            success: function(response) {
                resolve(response);
            }
        });
    });
}

function play_meme_sound()
{
    document.getElementById("enable_sounds").click(); // Trick browser to enable sounds
    meme_sound = meme_sounds[Math.floor(Math.random() * meme_sounds.length)];
    meme_audio = new Audio("/static/sounds/meme/" + meme_sound);
    meme_audio.play();
}