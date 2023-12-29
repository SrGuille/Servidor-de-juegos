import matplotlib
matplotlib.use('Agg') # Needed to avoid the error "RuntimeError: main thread is not in main loop"

import numpy as np
import threading
from . import models
from . import queries as q
from . import classes
from . import constants as c
from .roulettes_utils import roulettes_utils

from typing import List

players_lock = threading.Lock() # Lock for the players list

players_elems = {} # Dict with the elements of each player	

GAME_NAMES = c.GAME_NAMES

INITIAL_COINS = c.INITIAL_COINS

# Controls the current game and the number of rounds
current_game_id = -1
remaining_rounds = 0

""" 
Means that the players can join and interact with it.
Its value is changed from the frontend depending on the state of the game.
In the games that have more than 1 round it will be toggled between True and False
between the play - see results phases.
""" 
can_players_join = False
can_players_interact = False

"""  
In case of some player has 0 coins, a no cost game is randomly played 
and the players with 0 coins after it get some free coins 
It is stored in a different variable than current_game_id to don't lose the current game id
""" 
NO_COST_GAMES = c.NO_COST_GAMES

no_cost_current_game_id = -1
FREE_COINS_FOR_0_COINS_PLAYERS = c.FREE_COINS_FOR_0_COINS_PLAYERS

# TODO Maybe init everything here
def game_setup():
    pass

# Admin sets the current game and the number of rounds
def set_game(game_id, rounds):
    global current_game_id, remaining_rounds, can_players_join
    current_game_id = game_id
    remaining_rounds = rounds
    can_players_join = True


def transition_to_next_game() -> int:
    """ 
        Called between 2 games:
        - If there are more rounds of the scheculed game it returns the current game id 
          (if there are no more rounds, it returns -1), and one round is substracted
        - When some player/s don't have any coins, next game is some no cost game ignoring the schedule
    """
    global current_game_id, remaining_rounds, no_cost_current_game_id

    reset_elements() # Reset the elements of all players

    # Compensate the players with 0 coins who didn't won anything in the previous no cost game
    #TODO, maybe don't give coins to players who reached 0 coins in the previous game when DB exists
    if(no_cost_current_game_id != -1): # If there was a no cost game
        give_coins_to_0_coins_players()
        no_cost_current_game_id = -1 # Reset no cost current game id
    
    # If some player has 0 coins, redirect to a no cost game
    if(some_player_has_0_coins()): 
        no_cost_game = np.random.choice(NO_COST_GAMES)
        no_cost_current_game_id = GAME_NAMES.index(no_cost_game)
        set_can_players_join(True)
        return no_cost_current_game_id
    else:
        if(remaining_rounds > 0):
            remaining_rounds -= 1
        
        if(remaining_rounds == 0): # If there are no more rounds, return -1
            current_game_id = -1
            return -1
        else: # Follow the schedule
            set_can_players_join(True)
            return current_game_id

# Returns the current game id if it is ready, otherwise returns -1
def get_ready_to_join_game():
    if(can_players_join):
        if(no_cost_current_game_id != -1): # If there is a no cost game
            return no_cost_current_game_id
        else:
            return current_game_id
    else:
        return -1
    
def get_can_players_join():
    return can_players_join

def set_can_players_join(value):
    global can_players_join
    can_players_join = value

def get_can_players_interact():
    return can_players_interact

def set_can_players_interact(value):
    global can_players_interact
    can_players_interact = value

def give_coins_to_0_coins_players():
    zero_coins_players = q.get_0_coins_players()
    for player in zero_coins_players:
        q.add_coins_to_player(player.name, FREE_COINS_FOR_0_COINS_PLAYERS)

def login_player(name: str, nick: str) -> None:
    """
        Log in a player with its name and nick
    """
    players_lock.acquire()
    players_elems[name] = []
    players_lock.release()

    is_player_first_time = q.is_player_first_time(name)
    print(f"Is player first time: {is_player_first_time}")

    if(is_player_first_time is not None):
        if(is_player_first_time):
            q.reset_player(name, nick)
            q.add_new_prizes()
        else:
            q.change_player_nick(name, nick)

    print_players()
    print_prizes()

def get_players_names() -> List[str]:
    """
        Gets the names of all players from DB
    """
    players_names = q.get_players_names()
    return players_names

def logout(name: str) -> None:
    """
        Sets logged to False so the player is not required to play and deletes its elements
    """
    q.logout_player(name) # Erase the player's nick in DB
    players_lock.acquire()
    del players_elems[name]
    players_lock.release()
    print_players()

def get_player_elements(name):
    players_lock.acquire()
    player_elements = players_elems[name]
    players_lock.release()
    return player_elements

# Gets how many players haven't interacted yet
def get_remaining_interactions():
    logged_players = q.get_logged_players()
    num_logged_players = len(logged_players)
    num_interactions = 0

    players_lock.acquire()
    for player in logged_players:
        if len(players_elems[player.name]) > 0:
            num_interactions += 1
    players_lock.release()

    print(f"Number players: {num_logged_players}")
    print(f"Remaining interactions: {num_logged_players - num_interactions}")
    return num_logged_players - num_interactions

# Returns the players and their coins (all players, not only the ones with coins)
def get_players_scores():
    players_scores = []
    """
    players_lock.acquire()
    for player in players.values(): # Create a list of dicts
        players_scores.append({'name': player.name, 'nick': player.nick, 'coins': player.coins})
    players_lock.release()"""

    logged_players = q.get_logged_players()
    for player in logged_players:
        players_scores.append({'name': player.name, 'nick': player.nick, 'coins': player.coins})
    return players_scores

# Returns the prizes and their amount (only the ones with amount > 0)
def get_available_prizes():
    available_prizes = []
    for prize in q.get_available_prizes():
        available_prizes.append({'type': prize.type, 'prob': prize.prob, 'amount': prize.amount})
    return available_prizes

def get_players_elems():
    # Returns the whole dict
    return players_elems

def get_players_lock():
    return players_lock

def get_player_elems(name):
    player_elems = None
    if name in players_elems:
        player_elems = players_elems[name]
    return player_elems

# Returns the coins of a player
def get_player_coins(name):
    coins = q.get_player_coins(name)
    return coins

def some_player_has_0_coins():
    if(len(q.get_0_coins_players()) > 0):
        return True
    else:
        return False

def reset_elements() -> None:
    """
        Resets the elements of all players
    """
    for player in players_elems:
        players_elems[player] = []
    print_players()     

# Register that the player has paid for the prize and the prize has been given
def register_prize_winner(winner, prize_type):
    prize = q.get_prize(prize_type)
    q.add_coins_to_player(winner, -prize.value) # Substract the prize value from the player's coins
    q.decrement_prize_amount(prize)
    if(prize.amount == 0):
        q.adjust_prizes_probabilities(prize)

    print_players()
    print_prizes()

def create_players_roulette():
    logged_players = q.get_logged_players()
    roulettes_utils.create_players_roulette(logged_players)

def create_prizes_roulette():
    available_prizes = q.get_available_prizes()
    roulettes_utils.create_prizes_roulette(available_prizes)

def print_players():
    for player in q.get_logged_players():
        if player.name in players_elems: # If key exists
            print(f"Name: {player.name}")
            print(f"Nick: {player.nick}")
            print(f"Coins: {player.coins}")
            print(f"Elements: {players_elems[player.name]}")

def print_prizes():
    for prize in q.get_available_prizes():
        print(f"Type: {prize.type}")
        print(f"Prob: {prize.prob}")
        print(f"Amount: {prize.amount}")