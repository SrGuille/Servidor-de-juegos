import threading
from . import models
import json
from . import main_controller

players_lock = threading.Lock()

# Register player bets only if the roulette is not spinning
def register_player_bets(json_str):
    listen_client_calls = main_controller.get_listen_client_calls()
    if(listen_client_calls):
        bets = json.loads(json_str) #Convert json to dict
        main_controller.get_players_lock().acquire()
        players = main_controller.get_players()
        for player in players: #Find player
            if(player.name == bets['player_name']):
                list_bets = bets['bets']
                list_bets = json.loads(list_bets) #Convert string to list
                for player_bet in list_bets: #Add bets to player
                    bet = models.Bet(player_bet['type'], player_bet['amount'])
                    player.elements.append(bet) #Add bet to player
                    player.coins -= bet.amount #Substract coins
        print_players(players)
        main_controller.get_players_lock().release()

def print_players(players):
    for player in players:
        print(f"Name: {player.name}")
        print(f"Coins: {player.coins}")
        for bet in player.elements:
            print(f"Bet: {bet.type}")
            print(f"Amount: {bet.amount}")

def compute_winner_bets(result):
    result = int(result)
    red=(1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36)
    winner_bets = []

    if (result != 0):
        if (result in red):
            winner_bets.append('R')
        else:
            winner_bets.append('B')
            
        if (result % 2 == 0):
            winner_bets.append('E')
        else:
            winner_bets.append('O')
            
        if (result <= 18):
            winner_bets.append('H1')
        else:
            winner_bets.append('H2')
            
        if (result <= 12):
            winner_bets.append('T1')
        elif (result <=24):
            winner_bets.append('T2')
        else:
            winner_bets.append('T3')
            
        if (result % 3 == 1):
            winner_bets.append('R1')
        elif (result % 3 == 2):
            winner_bets.append('R2')
        else:
            winner_bets.append('R3')
            
    winner_bets.append(result)
    return winner_bets

def assign_prizes(result):
    x2_bets = ['R', 'B', 'E', 'O', 'H1', 'H2']
    x3_bets = ['T1', 'T2', 'T3', 'R1', 'R2', 'R3']

    winner_bets = compute_winner_bets(result)

    main_controller.get_players_lock().acquire()
    players = main_controller.get_players()
    for player in players:
        for bet in player.elements:

            # If bet is winner, add prize
            if (bet.type in winner_bets):
                if (bet.type in x2_bets):
                    player.coins += bet.amount * 2
                elif (bet.type in x3_bets):
                    player.coins += bet.amount * 3
                else:
                    player.coins += bet.amount * 36

    print_players(players)
    main_controller.get_players_lock().release()
                