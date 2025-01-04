import matplotlib
matplotlib.use('Agg') # Needed to avoid the error "RuntimeError: main thread is not in main loop"

import threading
from . import queries as q
from . import constants as c
from .roulettes_utils import roulettes_utils
from typing import List

class MainController:
    def __init__(self):
        self.players_lock = threading.Lock() # General lock
        
        # Game state attributes
        self.current_game_id = -1
        self.remaining_rounds = 0
        self.game_number = q.get_stored_game_number() # In case the server is restarted (it will be incremented in transition_to_next_game)
        print(f"Stored game number: {self.game_number}")
        print(f"Remaining games: {q.get_remaining_prizes()}")
        self.transition_to_next_game()

        # Game control flags
        """ 
            Means that the players can join and interact with it.
            Its value is changed from the frontend depending on the state of the game.
            In the games that have more than 1 round it will be toggled between True and False
            between the play - see results phases.
        """ 
        self.can_players_join = False
        self.can_players_interact = False
        
        # Constants
        self.GAME_NAMES = c.GAME_NAMES
        self.INITIAL_COINS = c.INITIAL_COINS

    def set_game(self, game_id, rounds):
        """
            Set the current game and the number of rounds (called by the admin in game_selector.html)
        """
        self.current_game_id = game_id
        self.remaining_rounds = rounds
        self.can_players_join = True

    def transition_to_next_game(self) -> int:
        """
            Called between 2 games:
            - Increments the game number
            - If there are more rounds of the scheculed game it returns the current game id 
            (if there are no more rounds, it returns -1), and one round is substracted
        """
        global current_game_id, remaining_rounds, game_number

        self.game_number += 1 # Increment the game number
        print(f'New game number: {self.game_number}')

        if(self.remaining_rounds > 0):
            self.remaining_rounds -= 1
        
        if(self.remaining_rounds == 0): # If there are no more rounds, return -1
            self.current_game_id = -1
            return -1
        else: # Follow the schedule
            self.can_players_join = True
            return self.current_game_id


    # Returns the current game id if it is ready, otherwise returns -1
    def get_ready_to_join_game(self):
        if(self.can_players_join):
            return self.current_game_id
        else:
            return -1
        
    def get_game_number(self):
        return self.game_number

    def get_can_players_join(self):
        return self.can_players_join

    def set_can_players_join(self, value):
        self.can_players_join = value

    def get_can_players_interact(self):
        return self.can_players_interact

    def set_can_players_interact(self, value):
        self.can_players_interact = value

    def login_player(self, name: str, nick: str) -> None:
        """
            Log in a player with its name and nick
            - If it is the first time, reset the player and add new prizes
            - If it is not the first time, change the player's nick
        """

        is_player_first_time = q.is_player_first_time(name)
        print(f"Is player first time: {is_player_first_time}")

        if(is_player_first_time is not None):
            if(is_player_first_time):
                q.reset_player(name, nick) # Sets the nick and default values
                q.add_new_prizes() # Adds 1 price of each type
            else:
                q.change_player_nick(name, nick) # Changes the nick

        #print_players()
        #print_prizes()

    def get_players_names(self) -> List[str]:
        """
            Gets the names of all players from DB (for the login player selector)
        """
        players_names = q.get_players_names()
        return players_names

    def logout(self, name: str) -> None:
        """
            Sets logged to False so the player is not required to play and deletes its elements
        """
        if(name is not None):
            q.logout_player(name) # Erase the player's nick in DB

    def get_players_scores(self):
        """
            Returns the players and their coins (all players, not only the ones with coins)
        """
        players_scores = []

        logged_players = q.get_logged_players()
        for player in logged_players:
            players_scores.append({'name': player.name, 'nick': player.nick, 'coins': player.coins})
        return players_scores

    def get_available_prizes(self):
        """
            Returns the prizes and their amount (only the ones with amount > 0)
        """
        available_prizes = []
        for prize in q.get_available_prizes():
            available_prizes.append({'type': prize.type, 'prob': prize.prob, 'amount': prize.amount})
        return available_prizes


    def get_players_lock(self):
        return self.players_lock

    def get_player_coins(self, name):
        coins = q.get_player_coins(name)
        return coins

    # Register that the player has paid for the prize and the prize has been given
    def register_prize_winner(self, winner: str, prize_type: str, free: bool):
        prize = q.get_prize(prize_type)

        if(free):
            prize_coins = 0
            print(f'Player {winner} has won a free prize')
        else:
            player_coins = q.get_player_coins(winner)
            prize_coins = round(player_coins * prize.value) # The cost depends on the player's coins
            print(f'Player {winner} has won a prize of {prize_coins} coins')

        q.add_coins_to_player(winner, -prize_coins) # Substract the prize value from the player's coins
        q.decrement_prize_amount(prize)
        q.increment_player_prizes_earned(winner)
        q.insert_prize_evolution(winner, prize_type, self.game_number)
        if(prize.amount == 0):
            q.adjust_prizes_probabilities(prize)
            print(f'There are no more {prize.type} prizes')

        #print_players()
        #print_prizes()

    def insert_coins_evolution_for_game(self):
        logged_players = q.get_logged_players()
        for player in logged_players:
            q.insert_coins_evolution(player, self.game_number)

    def create_players_roulette(self, santa_player: str):
        if(santa_player != ''): # Only one player
            players = [santa_player]
        else: # All players
            players = q.get_logged_players()
        roulettes_utils.create_players_roulette(players)

    def create_prizes_roulette(self):
        available_prizes = q.get_available_prizes()
        roulettes_utils.create_prizes_roulette(available_prizes)

"""
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
"""

"""  
In case of some player has 0 coins, a no cost game is randomly played 
and the players with 0 coins after it get some free coins 
It is stored in a different variable than current_game_id to don't lose the current game id
""" 
#NO_COST_GAMES = c.NO_COST_GAMES

#no_cost_current_game_id = -1
#FREE_COINS_FOR_0_COINS_PLAYERS = c.FREE_COINS_FOR_0_COINS_PLAYERS

"""
def get_player_elements(name):
    players_lock.acquire()
    player_elements = players_elems[name]
    players_lock.release()
    return player_elements
"""

"""
def transition_to_next_game() -> int:
        Called between 2 games:
        - If there are more rounds of the scheculed game it returns the current game id 
          (if there are no more rounds, it returns -1), and one round is substracted
        - When some player/s don't have any coins, next game is some no cost game ignoring the schedule
    
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
"""

"""
def give_coins_to_0_coins_players():
    zero_coins_players = q.get_0_coins_players()
    for player in zero_coins_players:
        q.add_coins_to_player(player.name, FREE_COINS_FOR_0_COINS_PLAYERS)
"""

"""
 # Gets how many players haven't interacted yet
    def get_remaining_interactions(self):
        num_logged_players = len(q.get_logged_players())
        num_interactions = get_number_interactions()

        print(f"Number players: {num_logged_players}")
        print(f"Remaining interactions: {num_logged_players - num_interactions}")
        return num_logged_players - num_interactions

    def get_number_interactions(self):
        num_interactions = 0
        logged_players = q.get_logged_players()
        for player in logged_players:
            if len(players_elems[player.name]) > 0:
                num_interactions += 1
        return num_interactions
"""

