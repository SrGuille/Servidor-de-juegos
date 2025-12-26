player_name = sessionStorage.getItem("player_name");

if(player_name == null) //If the player is not logged in, redirect to the login page
{
    window.location.href = "../";
}

number_positions = [];
LIST_SIZE = 8;
current_number = -1;

go_to_wait_screen_after_game();

async function get_my_team()
{
    number_positions = Array(LIST_SIZE).fill(-1);
    player_name = sessionStorage.getItem("player_name");
    await new Promise(r => setTimeout(r, 1000));
    $.ajax({
        url: "../get_my_team_bnumber",
        type: "GET",
        data: {player_name:player_name},
        success: function(response) {
            console.log(response)
            team = response.team;
            leader = response.leader;
            current_number = response.first_number;
            paint_team(team); // Paint the team color
            if(leader == player_name)
            {
                display_buttons();
            }
            else
            {
                document.getElementById("team-message").innerHTML = "Ve junto a " + leader;
            }
        }
    });
}

async function check_game_has_finished()
{
    has_finished = false;
    return new Promise((resolve, reject) => {
        $.ajax({
            url: "../has_finished_bnumber",
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

// Paints the buttons with the team color
function paint_team(team)
{
    let team_color = "team-" + team;
    background = document.getElementById("container");
    background.classList.add(team_color);
}

function display_buttons()
{
    for(let i = 0; i < LIST_SIZE; i++)
    {
        button = document.getElementById(i);
        button.style.display = "block";
    }
}

function unlock_all_buttons()
{
    for(let i = 0; i < LIST_SIZE; i++)
    {
        button = document.getElementById(i);
        button.disabled = false;
    }
}

function lock_impossible_buttons(new_number)
{
    closest_smaller_index = get_closest_smaller_index(new_number);
    console.log("Closest smaller index: " + closest_smaller_index);
    closest_bigger_index = get_closest_bigger_index(new_number);
    console.log("Closest bigger index: " + closest_bigger_index);

    // Unlock every position
    for(let i = 0; i < LIST_SIZE; i++)
    {
        unlock_button(i);
        console.log("Unlocked button " + i);
    }

    if(closest_smaller_index != -1) // If there is a smaller number, lock every smaller position (including it) from the start
    {
        for(let i = 0; i <= closest_smaller_index; i++)
        {
            lock_button(i);
            console.log("Locked button " + i);
        }
    }

    if(closest_bigger_index != -1) // If there is a bigger number, lock every bigger position (including it) up to the end
    {
        for(let i = closest_bigger_index; i < LIST_SIZE; i++)
        {
            lock_button(i);
            console.log("Locked button " + i);
        }
    }
}

function get_closest_smaller_index(number)
{
    // Returns the index of the closest smaller number in the list
    closest_smaller_index = -1;
    for(let i = 0; i < LIST_SIZE; i++)
    {
        if(number_positions[i] == -1)
        {
            continue;
        }   
        if(number_positions[i] < number)
        {
            closest_smaller_index = i;
        }
        else if(number_positions[i] > number)
        {
            break;
        }
    }
    return closest_smaller_index;
}

function get_closest_bigger_index(number)
{
    closest_bigger_index = -1;
    for(let i = 0; i < LIST_SIZE; i++)
    {
        if(number_positions[i] == -1)
        {   
            continue;
        }
        if(number_positions[i] > number)
        {
            closest_bigger_index = i;
            break;
        }
    }
    return closest_bigger_index;
}

function lock_button(position)
{
    button = document.getElementById(position);
    button.disabled = true;
}

function unlock_button(position)
{
    button = document.getElementById(position);
    button.disabled = false;
}

async function go_to_wait_screen_after_game()
{
    await new Promise(r => setTimeout(r, 50000)); //Wait 50 seconds
    for (let i = 0; i < 8; i++)
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

function send_position(position) {
    console.log("Se ha pulsado boton de position: " + position);
    $.ajax({
        url: "../send_position",
        type: "GET",
        data: {player_name: sessionStorage.getItem("player_name"), position: position},
        success: function(response) {
            new_number = response.new_number;
            is_impossible = response.is_impossible;
            console.log(response)
            if (new_number == -100) // The team has won
            {
                sessionStorage.setItem("played", true) //Set the played flag to true
                window.location.href = "../wait_room/";
            }
            else if(new_number != -1) // Accepted number
            {   
                if(is_impossible) // Impossible number
                {
                    // Save the new number as current but not in the list
                    current_number = new_number;
                    reset_number_positions();
                    unlock_all_buttons();
                }
                else
                {
                    // Store the current number in the list
                    number_positions[position] = current_number;
                    // Update the current number
                    current_number = new_number;
                    console.log(number_positions)
                    lock_impossible_buttons(new_number);
                }
            }
        }
    });
}

function reset_number_positions()
{
    for(let i = 0; i < 10; i++)
    {
        number_positions[i] = -1;
    }
}
