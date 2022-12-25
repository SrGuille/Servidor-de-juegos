import matplotlib.pyplot as plt
import numpy as np
import os
import threading
from . import models

players_lock = threading.Lock()

players = []

games = ['Ruleta', 'Ahorcado', "Democracia", "Tragaperras"]

active_game_id = 0
remaining_rounds = 1

# Sets the active game and the number of rounds
def set_game(game, rounds):
    global active_game_id, remaining_rounds
    active_game_id = game
    remaining_rounds = rounds

def get_active_game():
    return active_game_id

def register_player(name):
    players_lock.acquire()
    for player in players: #If player already exists, do nothing
        if(player.name == name):
            players_lock.release()
            print_players()
            return
    # If player does not exist, create it
    players.append(models.Player(name))
    players_lock.release()
    print_players()

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
    if(os.path.exists('servidor/static/img/pie_chart.png')):
        os.remove('servidor/static/img/pie_chart.png')
    plt.savefig('servidor/static/img/pie_chart.png')

def get_players():
    return players

def get_players_lock():
    return players_lock

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

def print_players():
    for player in players:
        print(f"Name: {player.name}")
        print(f"Coins: {player.coins}")
        for bet in player.bets:
            print(f"Bet: {bet.type}")
            print(f"Amount: {bet.amount}")