let GAME_SECONDS = 90; // Total seconds of the game

let team_screens = {};
let num_teams = 0;

async function play_bnumber()
{
    await create_teams();
    console.log("Teams created")
    await new Promise(r => setTimeout(r, 10000)); //Wait 10 seconds
    await countdown();
    await set_can_players_interact(true); // Players can move
    await main_loop(); 
    await set_can_players_join(false);
    await set_can_players_interact(false); // Players can't move
    await new Promise(r => setTimeout(r, 5000)); //Wait 5 seconds
    await finish_bnumber();
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
        document.getElementById("countdown").innerHTML = i;
        arcade_jump_audio.play();
        await new Promise(r => setTimeout(r, 1000)); //Wait 1 seconds
        arcade_jump_audio.pause();
    }
    document.getElementById("countdown").innerHTML = "";
}

async function main_loop()
{
    seconds = 0;
    seconds_left = document.getElementById("seconds_left");
    team_has_won = false;
    
    console.log(GAME_SECONDS);
    while(seconds < GAME_SECONDS && !team_has_won)
    {
        seconds_left.innerHTML = "Fin en " + (GAME_SECONDS - seconds).toString();
        seconds += 1;
        for(let i = 0; i < 10; i++)
        {
            await new Promise(r => setTimeout(r, 100)); //Wait 0.1 seconds
            team_has_won = await get_bnumber_data();
            if(team_has_won) break;  // Salir del for del segundo

        }
        console.log(seconds);
    }
    seconds_left.innerHTML = "Fin!";
}

// Create the teams and set the new number for each team
async function create_teams()
{
    await $.ajax({
        url: "../create_teams_bnumber",
        type: "GET",
        success: function(response) {
            // random number between 0 and 99
            console.log(response)
            teams_new_number = response.teams_new_number;
            num_teams = Object.keys(teams_new_number).length;
            
            // Mostrar las columnas según el número de equipos
            setup_team_columns(num_teams, Object.keys(teams_new_number));
            
            for (let i = 0; i < num_teams; i++) { // Get team screens and set new numbers
                team_name = Object.keys(teams_new_number)[i];
                team_screen = document.getElementById(`team-${team_name}`);
                team_screens[team_name] = team_screen;
                team_screen.querySelector(".new-number").innerHTML = teams_new_number[team_name];
            }
        }
    });
}

// Configurar y mostrar las columnas de equipos según el número de equipos
function setup_team_columns(num_teams, team_names)
{
    // Ocultar todas las columnas y divisores primero
    document.querySelectorAll('.team-column').forEach(col => col.style.display = 'none');
    document.querySelectorAll('.divider').forEach(div => div.style.display = 'none');
    
    // Mostrar las columnas de los equipos activos
    for (let i = 0; i < num_teams; i++) {
        let team_name = team_names[i];
        let team_column = document.getElementById(`team-${team_name}`);
        if (team_column) {
            team_column.style.display = 'flex';
        }
        
        // Mostrar divisor entre equipos (no después del último)
        if (i < num_teams - 1) {
            let divider = document.getElementById(`divider-${i + 1}`);
            if (divider) {
                divider.style.display = 'block';
            }
        }
    }
}

// Get updated data from the server
async function get_bnumber_data() {
    return new Promise((resolve, reject) => {
        $.ajax({
            url: "../get_bnumber_data",
            type: "GET",
            contentType: 'application/json;charset=UTF-8',
            success: function(response) {
                teams_positions = response.teams_positions;
                teams_new_number = response.teams_new_number;
                team_has_won = false;

                for (let i = 0; i < num_teams; i++) { // Update each team
                    team_name = Object.keys(teams_positions)[i];
                    team_screen = team_screens[team_name];
                    team_positions = teams_positions[team_name];
                    team_new_number = teams_new_number[team_name];
                    display_team(team_screen, team_positions, team_new_number);

                    if (team_new_number == -100) {
                        team_has_won = true;
                        team_screen.querySelector(".new-number").innerHTML = "Ganador";
                    }
                }

                resolve(team_has_won);
            },
            error: function(xhr, status, error) {
                reject(error);
            }
        });
    });
}

// Fill non-empty positions with the team's numbers and displaythe new number
function display_team(team_screen, team_positions, team_new_number)
{
    team_screen.querySelector(".new-number").innerHTML = team_new_number;

    i = 0;
    for(number of team_positions)
    {
        button = team_screen.querySelector(`button[id="${i}"]`);

        if(number != -1)
        { // Display the number
            button.innerHTML = number;
            button.classList.remove("empty-number");
            button.classList.add("filled-number");
        }
        else
        { // Display the empty position
            button.innerHTML = i;
            button.classList.remove("filled-number");
            button.classList.add("empty-number");
        }
        i += 1;
    }
}

// Send the colors per second to the server
async function finish_bnumber()
{
    await $.ajax({
        url: "../finish_bnumber",
        type: "GET",
        success: function(response) {
            document.getElementById("seconds_left").innerHTML = "";
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
