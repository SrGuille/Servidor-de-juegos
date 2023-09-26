import matplotlib
matplotlib.use('Agg') # Needed to avoid the error "RuntimeError: main thread is not in main loop"

import numpy as np
import threading
from . import models
from .roulettes_utils import roulettes_utils

players_lock = threading.Lock() # Lock for the players list

players = {}

GAME_NAMES = ['Ruleta', 'Ahorcado', "Democracia", "Tragaperras"]

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
NO_COST_GAMES = ['Ahorcado', 'Democracia'] # Games that don't cost coins to play

no_cost_current_game_id = -1
FREE_COINS_FOR_0_COINS_PLAYERS = 15

prizes = {
    "Dulce": models.Prize("Dulce", 0.25, 5), 
    "Regalo pequeño": models.Prize("Regalo pequeño", 0.25, 20), 
    "Regalo mediano": models.Prize("Regalo mediano", 0.25, 30), 
    "Regalo grande": models.Prize("Regalo grande", 0.25, 40)
}


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

    # Compensate the players with 0 coins who didn't won anything in the previous no cost game
    #TODO, maybe don't give coins to players who reached 0 coins in the previous game when DB exists
    if(no_cost_current_game_id != -1): # If there was a no cost game
        give_coins_to_0_coins_players()
        no_cost_current_game_id = -1 # Reset no cost current game id
    
    # If some player has 0 coins, redirect to a no cost game
    if(some_player_has_0_coins()): 
        no_cost_current_game_id = np.random.randint(0, len(NO_COST_GAMES))
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
    players_lock.acquire()
    for player in players.values():
        if(player.coins == 0):
            player.coins += FREE_COINS_FOR_0_COINS_PLAYERS
    players_lock.release()

def register_player(name: str, nick: str) -> None:
    """
        If it does not exist, it registers the player and adds a prize of each type
    """
    players_lock.acquire()
    if(players.get(name) == None): # If player doesn't exist
        id = len(players) + 1
        players[name] = models.Player(name, nick, id)
        add_prizes() # Player brings 1 prize of each type
    else: 
        players[name].logged = True
        players[name].nick = nick
    players_lock.release()
    print_players()
    print_prizes()

def logout(name: str) -> None:
    """
        Sets logged to False so the player is not required to play
    """
    players_lock.acquire()
    players[name].logged = False
    players_lock.release()
    print_players()

def get_number_logged_players() -> int:
    """
        Returns the number of players who are logged
        TODO when database just maintain in memory logged players
    """
    number_players = 0
    for player in players.values():
        if(player.logged):
            number_players += 1
    return number_players

def get_player_elements(name):
    players_lock.acquire()
    player = players[name]
    player_elements =  player.elements
    players_lock.release()
    return player_elements

# Adds a prize of each type to the prizes list
def add_prizes():
    for prize in prizes.values():
        if(prize.type == "Dulce"): # If it is a candy, a lot of them
            prize.amount += 10
        else:
            prize.amount += 1

# Gets how many players haven't interacted yet
def get_remaining_interactions():
    players_lock.acquire()
    number_players = get_number_logged_players()
    number_interactions = 0

    for player in players.values():
        if(len(player.elements) > 0 and player.logged): #If player has elements (bets, etc.)
            number_interactions += 1

    players_lock.release()
    print(f"Number players: {number_players}")
    print(f"Remaining interactions: {number_players - number_interactions}")
    return number_players - number_interactions

# Returns the players and their coins (all players, not only the ones with coins)
def get_players_scores():
    players_scores = []
    players_lock.acquire()
    for player in players.values(): # Create a list of dicts
        players_scores.append({'name': player.name, 'nick': player.nick, 'coins': player.coins})
    players_lock.release()
    return players_scores

# Returns the prizes and their amount (only the ones with amount > 0)
def get_available_prizes():
    available_prizes = []
    for prize in prizes.values():
        if(prize.amount > 0):
            available_prizes.append({'type': prize.type, 'prob': prize.prob, 'amount': prize.amount})

    return available_prizes

def get_players():
    return players

def get_players_lock():
    return players_lock

def get_player(name):
    return players[name]

# Returns the coins of a player
def get_player_coins(name):
    players_lock.acquire()
    player = players[name]
    coins = 0
    if(player != None):
        coins = player.coins
    players_lock.release()
    return coins

def some_player_has_0_coins():
    players_lock.acquire()
    for player in players.values():
        if(player.coins == 0):
            players_lock.release()
            return True
    players_lock.release()
    return False

def reset_elements() -> None:
    """
        Resets the elements of all players
    """
    for player in players.values():
        player.elements = []
    print_players()



def adjust_prizes_probabilities(out_of_stock_prize):
    """ 
        The probability of the out of stock prize is distributed 
        among the other available prizes depending on 
        their actual probability to cover the empty space
    """
    out_of_stock_prob = out_of_stock_prize.prob
    for prize in prizes.values():
        if(prize.amount > 0):
            prize.prob += (out_of_stock_prob * prize.prob) / (1 - out_of_stock_prob)
        

# Register that the player has paid for the prize and the prize has been given
def register_prize_winner(winner, prize_type):
    players_lock.acquire()
    player = players[winner]
    prize = prizes[prize_type]
    if(player != None):
        player.coins -= prize.value
        prize.amount -= 1

    if(prize.amount == 0): # If there are no more prizes of this type
        adjust_prizes_probabilities(prize)
    players_lock.release()
    print_players()
    print_prizes()

def create_players_roulette():
    roulettes_utils.create_players_roulette(players)

def create_prizes_roulette():
    roulettes_utils.create_prizes_roulette(prizes)

def print_players():
    for player in players.values():
        print(f"Name: {player.name}")
        print(f"Nick: {player.nick}")
        print(f"Coins: {player.coins}")
        print(f"Elements: {player.elements}")

def print_prizes():
    for prize in prizes.values():
        print(f"Type: {prize.type}")
        print(f"Prob: {prize.prob}")
        print(f"Amount: {prize.amount}")