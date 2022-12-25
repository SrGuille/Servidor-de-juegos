import threading
from . import models
import json
import matplotlib.pyplot as plt
import numpy as np
import os

players_lock = threading.Lock()
number_players = 0
number_bets = 0

players = []

def register_player(name):
    global players, number_players
    players_lock.acquire()
    for player in players: #If player already exists, do nothing
        if(player.name == name):
            players_lock.release()
            print_players()
            return
    # If player does not exist, create it
    number_players += 1
    players.append(models.Player(name))
    players_lock.release()
    print_players()

def register_player_bets(json_str):
    global players, number_bets
    bets = json.loads(json_str) #Convert json to dict
    players_lock.acquire()
    for player in players: #Find player
        if(player.name == bets['player_name']):
            list_bets = bets['bets']
            list_bets = json.loads(list_bets) #Convert string to list
            for player_bet in list_bets: #Add bets to player
                bet = models.Bet(player_bet['type'], player_bet['amount'])
                player.bets.append(bet)
    number_bets += 1
    players_lock.release()
    print_players()

def get_player_coins(name):
    global players
    players_lock.acquire()
    for player in players:
        if(player.name == name):
            coins = player.coins
            players_lock.release()
            return coins
    players_lock.release()
    return 0
    
def reset_bets():
    global players, number_bets
    players_lock.acquire()
    for player in players:
        player.bets = []
    number_bets = 0
    players_lock.release()
    print_players()

def get_remaining_bets():
    global number_players, number_bets
    return number_players - number_bets

def print_players():
    for player in players:
        print(f"Name: {player.name}")
        print(f"Coins: {player.coins}")
        for bet in player.bets:
            print(f"Bet: {bet.type}")
            print(f"Amount: {bet.amount}")

def get_winner_bets(result):
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
    x2_bets = ['R','B', 'E', 'O', 'H1', 'H2']
    x3_bets = ['T1', 'T2', 'T3', 'R1', 'R2', 'R3']

    winner_bets = get_winner_bets(result)
    for player in players:
        for bet in player.bets:
            player.coins -= bet.amount # Substract bet amount

            # If bet is winner, add prize
            if (bet.type in winner_bets):
                if (bet.type in x2_bets):
                    player.coins += bet.amount * 2
                elif (bet.type in x3_bets):
                    player.coins += bet.amount * 3
                else:
                    player.coins += bet.amount * 36
                

def get_ranking():
    ranking = []
    for player in players: # First, create a list of dicts
        ranking.append({'player_name': player.name, 'coins': player.coins})
    # Then, sort the list of dicts by coins
    ranking = sorted(ranking, key=lambda k: k['coins'], reverse=True)
    return ranking


def get_pie_chart():
    lables = []
    sizes = []

    for player in players:
        lables.append(player.name)
        sizes.append(player.coins)

    sizes = np.array(sizes)

    plt.pie(sizes, labels=lables, startangle=90, counterclock = False)
    os.remove('servidor/static/img/pie_chart.png')
    plt.savefig('servidor/static/img/pie_chart.png')