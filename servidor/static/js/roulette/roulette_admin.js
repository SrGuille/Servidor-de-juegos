/* Wait for all players to bet before spinning the roulette
OLD version before using websockets
async function wait_for_all_players_and_run()
{
    ready_to_play_game();
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

        console.log(response.remaining_interactions)
        if(response.remaining_interactions == "0")
        {
            result = spin_roulette();
            all_bets_sent = true;
        }
        
    }

}*/

// Spin the roulette and send the result to the server
async function run_and_send_result()
{
    result = await spin_roulette(); 
    console.log(result);
    send_roulette_result(result);
}

//Wait for all players to bet before spinning the roulette
async function wait_for_all_players_and_run()
{
    await listen_in_game_room(); // Wait for all players to bet
    await set_can_players_join(false);
    run_and_send_result(); // Spin the roulette and send the result to the server
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
    // quien lea esto es masón (29/12/23) - Juanda
    
    crutial_degrees = Math.floor(Math.random() * 360);
    roulette.style.setProperty('--rotation_degrees', extra_degrees + crutial_degrees + 'deg');
    chosen_number = roulette_numbers[Math.floor(crutial_degrees / numbers_width)];
    roulette.classList.add("roulette_spin_animation");
    
    document.getElementById("enable_sounds").click(); // Trick browser to enable sounds
    spinning_roulette_audio.volume = 0.2; // TODO Check if it works after play()
    spinning_roulette_audio.play();

    await new Promise(r => setTimeout(r, 9000));
    document.getElementById("result-spin").innerHTML = chosen_number;

    await new Promise(r => setTimeout(r, 5000));
    return chosen_number
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
            window.location.href = "../ranking_and_prizes/";
        }
    });
}

/*animation-duration animation-timing-function animation-delay animation-iteration-count direction  fill-mode animation-play-state animation-name*/

