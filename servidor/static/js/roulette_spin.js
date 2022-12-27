// Wait for all players to bet before spinning the roulette
async function wait_for_all_players_and_run()
{
    all_bets_sent = false;
    while (!all_bets_sent)
    {
        await new Promise(r => setTimeout(r, 5000)); //Wait 5 seconds
        //Send using set_bets django view
        response = await $.ajax({
            url: '../get_remaining_interactions/',
            type: 'GET',
            contentType: 'application/json;charset=UTF-8'
        });

        if(response.remaining_interactions == "0")
        {
            result = spin_roulette();
            all_bets_sent = true;
        }
        
    }

}

// Spin the roulette certain random degrees
async function spin_roulette()
{
    roulette_numbers = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26];
    roulette_numbers.reverse();
    numbers_width = 360 / roulette_numbers.length;
    extra_spins = 13;
    extra_degrees = extra_spins * 360;

    roulette = document.getElementById("roulette");

    crutial_degrees = Math.floor(Math.random() * 360);
    roulette.style.setProperty('--rotation_degrees', extra_degrees + crutial_degrees + 'deg');
    chosen_number = roulette_numbers[Math.floor(crutial_degrees / numbers_width)];
    roulette.classList.add("roulette_spin_animation");

    tell_server_to_stop_listening_calls();

    await new Promise(r => setTimeout(r, 9000));
    document.getElementById("result").innerHTML = chosen_number;

    await new Promise(r => setTimeout(r, 5000));
    send_roulette_result(chosen_number);
}

// Tell server that roulette is spinning so that new bets are not accepted
function tell_server_to_stop_listening_calls()
{
    $.ajax({
        url: '../dont_listen_client_calls/',
        type: 'GET',
        contentType: 'application/json;charset=UTF-8',
        success: function(response)
        {
            console.log(response);
        }
    });
}

function send_roulette_result(result)
{
    $.ajax({
        url: '../send_roulette_result/',
        type: 'GET',
        contentType: 'application/json;charset=UTF-8',
        data: {result:result},
        success: function(redirect) 
        {
            window.location.href = "../ranking/";
        }
    });
}

/*animation-duration animation-timing-function animation-delay animation-iteration-count direction  fill-mode animation-play-state animation-name*/

