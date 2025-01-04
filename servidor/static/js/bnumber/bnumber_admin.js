let classes = ['team-green', 'team-red']

let GAME_SECONDS = 90; // Total seconds of the game

let NUMBER_RANGE = 99; // 0 to 99

let team_green_screen;
let team_red_screen;

async function play_bnumber()
{
    team_green_screen = document.getElementById("team-green");
    team_red_screen = document.getElementById("team-red");
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
    await new Promise(r => setTimeout(r, 5000)); //Wait 5 seconds
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
            new_number_green = response.new_number_green;
            team_green_screen.querySelector(".new-number").innerHTML = new_number_green;
            new_number_red = response.new_number_red;
            team_red_screen.querySelector(".new-number").innerHTML = new_number_red;
        }
    });
}

// Get democratic move, move the character and log the color
async function get_bnumber_data() {
    let team_has_won = false;
    return new Promise((resolve, reject) => {
        $.ajax({
            url: "../get_bnumber_data",
            type: "GET",
            contentType: 'application/json;charset=UTF-8',
            success: function(response) {
                teams_positions = response.teams_positions;
                teams_new_number = response.teams_new_number;
                team_green_positions = teams_positions['Verde'];
                team_red_positions = teams_positions['Rojo'];
                team_green_new_number = teams_new_number['Verde'];
                team_red_new_number = teams_new_number['Rojo'];

                if(team_green_new_number == -100 || team_red_new_number == -100) 
                {
                    team_has_won = true;
                } 
                else
                {
                    display_team(team_green_screen, team_green_positions, team_green_new_number);
                    display_team(team_red_screen, team_red_positions, team_red_new_number);
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
            document.getElementById("bnumber-result").innerHTML = response.winner_msj;
        }
    });
}
