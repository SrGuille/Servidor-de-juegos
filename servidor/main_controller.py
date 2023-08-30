import matplotlib
matplotlib.use('Agg') # Needed to avoid the error "RuntimeError: main thread is not in main loop"
import matplotlib.pyplot as plt

import numpy as np
import os
import threading
from . import models

players_lock = threading.Lock() # Lock for the players list

players = []

games = ['Ruleta', 'Ahorcado', "Democracia", "Tragaperras"]

# Controls the active game and the number of rounds
active_game_id = -1
remaining_rounds = 0

""" 
Means that the players can join and interact with it.
Its value is changed from the frontend depending on the state of the game.
In the games that have more than 1 round it will be toggled between True and False
between the play - see results phases.
""" 
ready_to_play_game = False

"""  
In case of some player has 0 coins, a no cost game is randomly played 
and the players with 0 coins after it get some free coins 
""" 
no_cost_games = ['Ahorcado', 'Democracia'] # Games that don't cost coins to play

no_cost_active_game_id = -1
FREE_COINS_FOR_0_COINS_PLAYERS = 15

prizes = [
    models.Prize("Dulce", 0.25, 5), 
    models.Prize("Regalo pequeño", 0.25, 20), 
    models.Prize("Regalo mediano", 0.25, 30), 
    models.Prize("Regalo grande", 0.25, 40)
]


# TODO Maybe init everything here
def game_setup():
    pass

# Sets the active game and the number of rounds
def set_game(game_id, rounds):
    global active_game_id, remaining_rounds
    active_game_id = game_id
    remaining_rounds = rounds

""" 
If there are more rounds of the scheculed game it returns the active game id 
(if there are no more rounds, it returns -1), and one round is substracted
When some player/s don't have any coins, next game is some no cost game ignoring the schedule
"""
def transition_to_next_game():
    global active_game_id, remaining_rounds, no_cost_active_game_id

    #TODO, maybe don't give coins to players who got to 0 coins in the previous game
    
    # Compensate the players with 0 coins who didn't won anything in the previous no cost game
    if(no_cost_active_game_id != -1): # If there was a no cost game
        give_coins_to_0_coins_players()
        no_cost_active_game_id = -1 # Reset no cost active game id
    
    if(some_player_has_0_coins()): # If some player has 0 coins, redirect to a no cost game
        no_cost_active_game_id = np.random.randint(0, len(no_cost_games))
        return no_cost_active_game_id
    else:
        if(remaining_rounds > 0):
            remaining_rounds -= 1
        
        if(remaining_rounds == 0): # If there are no more rounds, return -1
            active_game_id = -1
            return -1
        else:
            return active_game_id

# Returns the active game id if it is ready to start, otherwise returns -1
def get_ready_to_play_game():
    if(ready_to_play_game):
        if(no_cost_active_game_id != -1):
            return no_cost_active_game_id
        else:
            return active_game_id
    else:
        return -1
    
def is_game_ready_to_play():
    return ready_to_play_game

def give_coins_to_0_coins_players():
    players_lock.acquire()
    for player in players:
        if(player.coins == 0):
            player.coins += FREE_COINS_FOR_0_COINS_PLAYERS
    players_lock.release()

# If it does not exist, it registers the player and adds a prize of each type
def register_player(name):
    players_lock.acquire()
    if(get_player(name) == None): # If player doesn't exist
        id = len(players) + 1
        players.append(models.Player(name, id))
        add_prizes() # Player brings 1 prize of each type
    players_lock.release()
    print_players()
    print_prizes()

# Returns the player information if it exists (required to have the lock previously)
def get_player(name):
    searched_player = None
    for player in players:
        if(player.name == name):
            searched_player = player
            break

    return searched_player

def get_player_elements(name):
    players_lock.acquire()
    player = get_player(name)
    player_elements =  player.elements
    players_lock.release()
    return player_elements

def get_prize(type):
    searched_prize = None
    for prize in prizes:
        if(prize.type == type):
            searched_prize = prize
            break

    return searched_prize

# Adds a prize of each type to the prizes list
def add_prizes():
    for prize in prizes:
        if(prize.type == "Dulce"): # If it is a candy, a lot of them
            prize.amount += 10
        else:
            prize.amount += 1

# Gets how many players haven't interacted yet
def get_remaining_interactions():
    players_lock.acquire()
    number_players = len(players)
    number_interactions = 0

    for player in players:
        if(len(player.elements) > 0): #If player has elements
            number_interactions += 1

    players_lock.release()
    return number_players - number_interactions

# Returns the players and their coins (all players, not only the ones with coins)
def get_players_scores():
    players_scores = []
    players_lock.acquire()
    for player in players: # First, create a list of dicts
        players_scores.append({'player_name': player.name, 'coins': player.coins})
    players_lock.release()
    return players_scores

# Returns the prizes and their amount (only the ones with amount > 0)
def get_available_prizes():
    available_prizes = []
    for prize in prizes:
        if(prize.amount > 0):
            available_prizes.append({'type': prize.type, 'prob': prize.prob, 'amount': prize.amount})

    return available_prizes

# Creates the players roulette image with players with coins
def create_players_roulette():
    labels = []
    sizes = []

    for player in players:
        if(player.coins > 0): # If player has coins
            labels.append(player.name)
            sizes.append(player.coins)

    sizes = np.array(sizes)

    print(labels)
    print(sizes)

    create_roulette_image(labels, sizes, 90, False, 0.5, 'players_roulette')

# Creates the prizes roulette image with available prizes
def create_prizes_roulette():
    labels = []
    sizes = []

    for prize in prizes:
        if(prize.amount > 0): # If there are prizes of this type
            label = prize.type.replace("Regalo", "R.")
            labels.append(label)
            sizes.append(prize.prob)

    sizes = np.array(sizes)

    create_roulette_image(labels, sizes, 90, False, 0.5, 'prizes_roulette')

# Creates the roulette image (first delete it if it exists)
def create_roulette_image(labels, sizes, startangle, counterclock, labeldistance, filename):
    plt.pie(sizes, labels=labels, startangle=startangle, counterclock = counterclock, labeldistance=labeldistance)
    if(os.path.exists(f'servidor/static/img/{filename}.png')):
        os.remove(f'servidor/static/img/{filename}.png')
    plt.savefig(f'servidor/static/img/{filename}.png', transparent=True, dpi=150, bbox_inches='tight')
    plt.close()

def get_players():
    return players

def get_players_lock():
    return players_lock

def set_ready_to_play_game(value):
    global ready_to_play_game
    ready_to_play_game = value

# Returns the coins of a player
def get_player_coins(name):
    players_lock.acquire()
    player = get_player(name)
    coins = 0
    if(player != None):
        coins = player.coins
    players_lock.release()
    return coins

def some_player_has_0_coins():
    players_lock.acquire()
    for player in players:
        if(player.coins == 0):
            players_lock.release()
            return True
    players_lock.release()
    return False

# Empty the bets list of all players
def reset_elements():
    global ready_to_play_game
    for player in players:
        player.elements = []
    print_players()


# Give to the other available prizes the proportional probability of the out of stock prize
def adjust_prizes_probabilities(out_of_stock_prize):
    out_of_stock_prob = out_of_stock_prize.prob
    available_prizes = []
    sum_available_prizes_prob = 0
    num_available_prizes = 0
    for prize in prizes:
        if(prize.amount > 0):
            sum_available_prizes_prob += prize.prob
            available_prizes.append(prize)
            num_available_prizes += 1
    
    for prize in available_prizes:
        prize.prob += (out_of_stock_prob * prize.prob) / sum_available_prizes_prob

# Register that the player has paid for the prize and the prize has been given
def register_prize_winner(winner, prize_type):
    players_lock.acquire()
    player = get_player(winner)
    prize = get_prize(prize_type)
    if(player != None):
        player.coins -= prize.value
        prize.amount -= 1

    if(prize.amount == 0): # If there are no more prizes of this type
        adjust_prizes_probabilities(prize)
    players_lock.release()
    print_players()
    print_prizes()

def print_players():
    for player in players:
        print(f"Name: {player.name}")
        print(f"Coins: {player.coins}")
        print(f"Elements: {player.elements}")

def print_prizes():
    for prize in prizes:
        print(f"Type: {prize.type}")
        print(f"Prob: {prize.prob}")
        print(f"Amount: {prize.amount}")