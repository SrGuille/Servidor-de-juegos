LETTER_REVEAL_TIMES = [800, 1500, 4000]; // Time to wait to reveal a letter based on progress

async function play_palabrazo()
{
    num_pending_letters = await setup_palabrazo();
    console.log("Palabrazo setup done");
    await new Promise(r => setTimeout(r, 5000)); //Wait 5 seconds
    await countdown();
    await set_can_players_interact(true); // Players can move
    await main_loop(num_pending_letters); 
    await set_can_players_join(false);
    await set_can_players_interact(false); // Players can't move
    await new Promise(r => setTimeout(r, 10000)); //Wait 10 seconds
    await finish_palabrazo();
    await new Promise(r => setTimeout(r, 10000)); //Wait 10 seconds
    window.location.href = "../ranking_and_prizes/";
}

async function countdown()
{
    document.getElementById("enable_sounds").click(); // Trick browser to enable sounds
    arcade_jump_audio.volume = 0.7;
    arcade_jump_audio.play();
    for(i = 3; i > 0; i--)
    {
        arcade_jump_audio.play();
        await new Promise(r => setTimeout(r, 1000)); //Wait 1 seconds
        arcade_jump_audio.pause();
    }}

async function main_loop(initial_num_pending_letters)
{
    all_sentence_revealed = false;
    let num_pending_letters = initial_num_pending_letters;
    while(!all_sentence_revealed) {
        num_pending_letters = await reveal_letter();
        // Calcular el porcentaje de letras restantes
        let reveal_time = get_reveal_time(initial_num_pending_letters, num_pending_letters);
        let pooling_steps = reveal_time / 100;
        for(let i = 0; i < pooling_steps; i++) 
        {
            await new Promise(r => setTimeout(r, 100)); //Wait 0.1 seconds
            // Actualizar num_pending_letters y chequear si se terminó
            num_pending_letters = await get_palabrazo_data();
            if(num_pending_letters === 0) 
            {
                all_sentence_revealed = true;
                break;
            }
        }
    }
}

function get_reveal_time(initial_num_pending_letters, num_pending_letters)
{
    let percent_left = num_pending_letters / initial_num_pending_letters;
    let reveal_time;
    if (percent_left > 1/2) {
        reveal_time = LETTER_REVEAL_TIMES[0]; // Primer 50%
    } 
    else if (percent_left > 1/4) {
        reveal_time = LETTER_REVEAL_TIMES[1]; // Segundo 25% (entre 25% y 50%)
    } else {
        reveal_time = LETTER_REVEAL_TIMES[2]; // Último 25% (menos de 25%)
    }
    return reveal_time;
}

// Get updated data from the server
async function setup_palabrazo() {
    return new Promise((resolve, reject) => {
        $.ajax({
            url: "../setup_palabrazo",
            type: "GET",
            contentType: 'application/json;charset=UTF-8',
            success: function(response) {
                console.log(response.partially_guessed_sentence)
                sentence = response.partially_guessed_sentence;
                jackpot = response.current_jackpot;
                num_pending_letters = response.num_pending_letters;
                display_sentence(sentence);
                display_jackpot(jackpot);

                resolve(num_pending_letters);
            },
            error: function(xhr, status, error) {
                reject(error);
            }
        });
    });
}

// Get updated data from the server
async function get_palabrazo_data() {
    return new Promise((resolve, reject) => {
        $.ajax({
            url: "../get_palabrazo_data",
            type: "GET",
            contentType: 'application/json;charset=UTF-8',
            success: function(response) {
                console.log(response.partially_guessed_sentence)
                sentence = response.partially_guessed_sentence;
                jackpot = response.current_jackpot;
                num_pending_letters = response.num_pending_letters;
                display_sentence(sentence);
                display_jackpot(jackpot);

                resolve(num_pending_letters);
            },
            error: function(xhr, status, error) {
                reject(error);
            }
        });
    });
}

// Get updated data from the server
async function reveal_letter() {
    return new Promise((resolve, reject) => {
        $.ajax({
            url: "../reveal_letter",
            type: "GET",
            contentType: 'application/json;charset=UTF-8',
            success: function(response) {
                console.log(response.partially_guessed_sentence)
                sentence = response.partially_guessed_sentence;
                jackpot = response.current_jackpot;
                num_pending_letters = response.num_pending_letters;
                display_sentence(sentence);
                display_jackpot(jackpot);

                resolve(num_pending_letters);
            },
            error: function(xhr, status, error) {
                reject(error);
            }
        });
    });
}

async function display_sentence(sentence) 
{
    let sentence_display = "<div style='display: flex; flex-direction: row; flex-wrap: wrap; gap: 70px; row-gap: 22px; align-items: flex-start; justify-content: center; margin: 40px 4vw 0 4vw;'>";
    let words = sentence.split(' ');
    for (let w = 0; w < words.length; w++) {
        sentence_display += "<div style='display: flex; flex-direction: row; gap: 10px;'>";
        for (let l = 0; l < words[w].length; l++) {
            let char = words[w][l];
            let isHidden = (char === '_' || char === '*'); // Ajusta según cómo se oculten las letras
            sentence_display += `<div style='
                width: 65px;
                height: 65px;
                border: 2px solid #B9C2CC;
                border-radius: 18px;
                background: linear-gradient(135deg, #fff 70%, #e6f0fa 100%);
                box-shadow: 0 2px 8px rgba(0,0,0,0.10);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 3.2rem;
                font-weight: bold;
                color: #222;
                font-family: var(--font-body, 'Advent Pro', Arial, sans-serif);
                transition: box-shadow 0.2s, border 0.2s;
            '>${isHidden ? '' : char}</div>`;
        }
        sentence_display += "</div>";
    }
    sentence_display += "</div>";
    document.getElementById("palabrazo-sentence").innerHTML = sentence_display;
}


function display_jackpot(jackpot)
{
    document.getElementById('jackpot').innerHTML = 'Bote: ' + jackpot + ' monedas';
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

// Send the colors per second to the server
async function finish_palabrazo()
{
    await $.ajax({
        url: "../finish_palabrazo",
        type: "GET",
        success: function(response) {
            winner_msj = response.winner_msj;
            showVictoryModal(winner_msj);
        }
    });
}

// Show the victory modal with the result message
function showVictoryModal(message) {
    const modalOverlay = document.getElementById("victory-modal-overlay");
    const modalContent = document.getElementById("victory-modal-content");
    modalContent.innerHTML = message;
    modalOverlay.classList.add("show");
}