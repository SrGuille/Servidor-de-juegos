function get_player_data_and_play()
{
    $.ajax({
        url: "../get_duel_data",
        type: "GET",
        data: {name: sessionStorage.getItem("player_name")},
        success: function(response) {
            if (response.player_data != null) // Player is in the duel
            {
                console.log(response);
                player_data = response.player_data;
                bullets = player_data.bullets;
                shields = player_data.shields;
                lives = player_data.lives;
                is_special_duel = response.is_special_duel;
                display_stats(bullets, shields, lives, is_special_duel); 
                update_buttons(bullets, shields); // Disable the shoot and shield buttons if there are no bullets and vice versa
            }
            else // Player is not in the duel
            {
                window.location.href = "../wait_room/";
                sessionStorage.setItem("played", true);
            }
        }
    });
}

async function send_player_action(action)
{
    return new Promise(function(resolve, reject) {
        $.ajax({
            url: "../send_player_action",
            type: "GET",
            data: {
            name: sessionStorage.getItem("player_name"),
            action: action
            },
            success: function(response) { // Send to wait room
                resolve(response);
            }   
        });
    });
}


async function send_player_action_notify(guess)
{
    response = await send_player_action(guess);
    if (response.allowed == true)
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

function update_buttons(bullets, shields)
{
    shoot_button = document.getElementById("shoot");
    shield_button = document.getElementById("shield");
    if (bullets == 0)
    {
        shoot_button.disabled = true;
    }
    else
    {
        shoot_button.disabled = false;
    }
    if (shields == 0)
    {
        shield_button.disabled = true;
    }
    else
    {
        shield_button.disabled = false;
    }
}

function display_stats(bullets, shields, lives, is_special_duel)
{
    document.getElementById("bullet-count").innerHTML = bullets;
    document.getElementById("shield-count").innerHTML = shields;
    if (is_special_duel)
    {
        lives = document.getElementById("lives").style.display = "block";
        document.getElementById("lives-count").innerHTML = lives;
    }
}


