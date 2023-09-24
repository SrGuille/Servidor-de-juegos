import threading
from servidor import models
import json
from servidor import main_controller

players_lock = threading.Lock()

# Register player bets only if the roulette is not spinning
def register_player_bets(bets):
    if(main_controller.get_can_players_interact()): # If roulette has not spinned yet
        main_controller.get_players_lock().acquire()
        player = main_controller.get_player(bets['player_name'])
        if(player != None):
            list_bets = bets['bets']
            list_bets = json.loads(list_bets) #Convert string to list
            for player_bet in list_bets: #Add bets to player
                bet = models.Bet(player_bet['type'], player_bet['amount'])
                player.elements.append(bet) #Add bet to player
                player.coins -= bet.amount #Substract coins
        main_controller.print_players()
        main_controller.get_players_lock().release()
        return True
    else:
        return False

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
            winner_bets.append('1H')
        else:
            winner_bets.append('2H')
            
        if (result <= 12):
            winner_bets.append('1T')
        elif (result <=24):
            winner_bets.append('2T')
        else:
            winner_bets.append('3T')
            
        if (result % 3 == 1):
            winner_bets.append('3R')
        elif (result % 3 == 2):
            winner_bets.append('2R')
        else:
            winner_bets.append('1R')
            
    return winner_bets

def assign_prizes(result):
    x2_bets = ['R', 'B', 'E', 'O', '1H', '2H']
    x3_bets = ['1T', '2T', '3T', '1R', '2R', '3R']

    winner_bets = compute_winner_bets(result)

    players = main_controller.get_players()
    for player in players.values():
        for bet in player.elements:

            # If bet is winner, add prize
            if (bet.type in winner_bets):
                if (bet.type in x2_bets):
                    player.coins += bet.amount * 2
                elif (bet.type in x3_bets):
                    player.coins += bet.amount * 3

            if (bet.type == result): # If bet is winner, add prize
                player.coins += bet.amount * 36
                    

    main_controller.print_players()
                