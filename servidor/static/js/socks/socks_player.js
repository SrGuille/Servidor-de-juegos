let num_socks = 8;
let available_coins = 0;
let coins_to_bet = 5;
const bet_steps = [5, 10, 20, 40];
let bet_step_index = 0;
let selected_sock = null;

function update_sock_visibility() {
    for (let i = 0; i < 8; i++) {
        const sockItem = document.getElementById('sock-item-' + i);
        if (sockItem) {
            if (i < num_socks) {
                sockItem.style.display = '';
            } else {
                sockItem.style.display = 'none';
            }
        }
    }
}

function update_available_coins_label(msj) {
    document.getElementById('available_coins').innerText = msj;
}

function display_coins_to_bet(coins_to_bet) {
    document.getElementById('group_coins_bet').innerHTML = 'Apostar: <span id="coins-to-bet">' + coins_to_bet + '</span> moneda(s)';
}

function change_bet_coins() {
    let next_index = (bet_step_index + 1) % bet_steps.length;

    if (available_coins < bet_steps[next_index]) {
        bet_step_index = 0;
    }
    else {
        bet_step_index = next_index;
    }

    coins_to_bet = bet_steps[bet_step_index];
    
    display_coins_to_bet(coins_to_bet);
}

async function init_socks_player() {
    // Oculta todos los calcetines inicialmente
    for (let i = 0; i < 8; i++) {
        const sockItem = document.getElementById('sock-item-' + i);
        if (sockItem) sockItem.style.display = 'none';
    }
    // Llama a get_num_socks
    await $.ajax({
        url: '../get_num_socks',
        type: 'GET',
        success: function(response) {
            num_socks = response.num_socks || 8;
            update_sock_visibility();
        }
    });
    // Llama a get_player_available_coins
    let player_name = sessionStorage.getItem('player_name');
    await $.ajax({
        url: '../get_player_available_and_previous_coins',
        type: 'GET',
        data: {player_name: player_name},
        success: function(response) {
            console.log("Response from server:", response);
            available_coins = response.available_coins;
            let previous_coins = response.previous_coins;
            let msj = "Tienes " + available_coins + " monedas";
            
            if (previous_coins !== -1) { // Apuesta previa existe
                coin_diff = available_coins - parseInt(previous_coins);
                if (coin_diff > 0) {
                    msj += " (ganaste " + coin_diff + " en la última ronda)";
                } else if (coin_diff < 0) {
                    msj += " (perdiste " + Math.abs(coin_diff) + " en la última ronda)";
                } else {
                    msj += " (ni ganaste ni perdiste en la última ronda)";
                }
            }

            update_available_coins_label(msj);

            coins_to_bet = 5;
            bet_step_index = 0;
            display_coins_to_bet(coins_to_bet);
        }
    });
}

function select_sock(i) {
    // Solo se puede seleccionar uno
    for (let j = 0; j < num_socks; j++) {
        let btn = document.getElementById('bet-btn-' + j);
        if (btn) btn.classList.remove('selected');
    }
    document.getElementById('bet-btn-' + i).classList.add('selected');
    selected_sock = i;
}

async function send_sock_bet() {
    if (selected_sock === null) {
        alert('Selecciona un calcetín para apostar.');
        return;
    }
    return new Promise(function(resolve, reject) {
        $.ajax({
            url: '../send_sock_bet',
            type: 'GET',
            data: { player_name: sessionStorage.getItem('player_name'), sock_id: selected_sock, coins: coins_to_bet },
            success: function(response) {
                console.log("Response from server:", response);
                resolve(response);
            }
        });
    });
}

async function send_sock_bet_notify()
{
    response = await send_sock_bet();
    if (response.valid == true)
    {
        await notify_player_has_interacted();
        sessionStorage.setItem("played", true) //Set the played flag to true
        window.location.href = "../wait_room/";
    }
    else
    {
        alert("No puedes interactuar en este momento");
    }
}

document.addEventListener('DOMContentLoaded', function() {
    init_socks_player();
});



