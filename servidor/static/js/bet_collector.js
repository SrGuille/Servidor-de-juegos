player_name = sessionStorage.getItem("player_name");

if(player_name == null) //If the player is not logged in, redirect to the login page
{
    window.location.href = "../";
}

bets = []
coin_bet_number = 1;
total_coins = 0;
available_coins = 0;

function get_coins() 
{
    //TODO Get the coins from the server
    $.ajax({
        url: '../get_player_coins/',
        type: 'GET',
        contentType: 'application/json;charset=UTF-8',
        data: {player_name:player_name},
        success: function(response)
        {
            player_coins = parseInt(response.player_coins);
            document.getElementById("available_coins").innerHTML = player_coins + " monedas disponibles";
            document.getElementById("betted_coins").innerHTML = 0 + " monedas apostadas";
        }
    });
}

function Bet(bet, coins)
{
    this.type = bet;
    this.amount = coins;
}

function find_bet(bet)
{
    for(i = 0; i < bets.length; i++)
    {
        if(bets[i].type == bet)
        {
            return i;
        }
    }
    return -1;
}

// Function to bet or unbet a number
function bet_unbet(button) 
{
    if(coin_bet_number > 0)
    {
        bet(button);
    }
    else
    {
        unbet(button);
    }

    console.log(bets)
}

function bet(button) 
{
    if(available_coins >= coin_bet_number) //If the player has enough coins
    {
        bet_pos = find_bet(button.id);
        
        //If the bet is already in the list, change the number of coins
        if(bet_pos != -1)
        {
            bets[bet_pos].coins += coin_bet_number;
            //new_opacity = bets[bet_pos].coins * 10;
        }
        else //If not, add it to the list
        {
            bets.push(new Bet(button.id, coin_bet_number));
            //new_opacity = coin_bet_number * 10;
        }

        //button.style.opacity = new_opacity.toString() + '%'; 
        button.style.opacity = '70%';

        available_coins -= coin_bet_number;

        document.getElementById("available_coins").innerHTML = available_coins + " monedas disponibles";
        document.getElementById("betted_coins").innerHTML = total_coins - available_coins + " monedas apostadas";
    }
}

// Remove bet from list and update available coins
function unbet(button)
{
    bet_pos = find_bet(button.id);
    if(bet_pos != -1)
    {
        available_coins += bets[bet_pos].amount;
        bets.splice(bet_pos, 1);
        button.style.opacity = '0%'; 

        document.getElementById("available_coins").innerHTML = available_coins + " monedas disponibles";
        document.getElementById("betted_coins").innerHTML = total_coins - available_coins + " monedas apostadas";
    }
}

function send_bets() 
{
    //Send the bets to the server using AJAX
    bets_json = JSON.stringify(bets);

    player_bets = new Object();
    player_bets.bets = bets_json;
    player_bets.player_name = player_name;

    player_bets = JSON.stringify(player_bets);
    console.log(player_bets)
    
    //Send using set_bets django view
    $.ajax({
        url: '../send_bets/',
        type: 'GET',
        data: {bets:player_bets},
        contentType: 'application/json;charset=UTF-8',
        success: function(response) {
            console.log(response);
        }
    });
}

// Function to change the number of coins to bet
function change_bet_coins() {
    coin_bet_number = (coin_bet_number + 1) % 4;
    document.getElementById("group_coins_bet").innerHTML = "Apostar: " + coin_bet_number + " moneda(s)";
    console.log(document.getElementById("group_coins_bet").innerHTML)

    if(coin_bet_number == 0)
    {
        document.getElementById("group_coins_bet").innerHTML = "Retirar apuesta";
    }

}