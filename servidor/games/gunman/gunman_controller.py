from servidor import main_views
import random
from servidor import queries as q
from servidor.classes import GunmanPlayer
from copy import deepcopy  # Add this import at the top
import threading

class GunmanGame:
    def __init__(self):
        self.remaining_players = [] # List of players that have not participated in any duel
        self.duel_players = {}
        self.players_lock = threading.Lock()
        self.COINS_TO_STEAL = 10
        self.is_special_duel = False

    def create_initial_duel(self):
        """
        Selects 2 random players from the list of players and returns their names
        """
        self.duel_players = {} # Reset the duel players
        self.remaining_players = q.get_logged_players_names()
        self.is_special_duel = False

        # Select 2 random players 
        self.add_new_player_to_duel()
        self.add_new_player_to_duel()

        serialized_players = {
            name: player.to_dict() 
            for name, player in self.duel_players.items()
        }

        return serialized_players
    
    def create_special_duel(self, player1, player2):
        self.duel_players = {} # Reset the duel players
        self.duel_players[player1] = GunmanPlayer()
        self.duel_players[player2] = GunmanPlayer()
        self.is_special_duel = True

        serialized_players = {
            name: player.to_dict() 
            for name, player in self.duel_players.items()
        }

        return serialized_players

    def add_new_player_to_duel(self):
        """
        Adds a new player for the duel
        """
        new_player = None
        if len(self.remaining_players) > 0:
            new_player = random.choice(self.remaining_players)
            self.duel_players[new_player] = GunmanPlayer()
            self.remaining_players.remove(new_player)
            print(f"New player added: {new_player}")

        return new_player

    def register_player_action(self, name, action):
        allowed = main_views.main_controller_.get_can_players_interact()
        if allowed and name in self.duel_players.keys():
            self.players_lock.acquire()
            self.duel_players[name].action = action
            self.update_bullets(self.duel_players[name])
            self.players_lock.release()
        return allowed

    def update_bullets(self, player):
        """
        Manages the bullets of a player when he takes an action
        """
        if player.action == "shoot":
            player.bullets -= 1
        elif player.action == "shield":
            player.shields -= 1
        elif player.action == "reload":
            player.bullets += 1
            player.shields += 1

    def get_duel_data(self, name):
        """
            Returns to a player if them are in the duel or not and the type of duel
        """
        serialized_player_data = None
        if name in self.duel_players.keys():
            player_data = self.duel_players[name]
            serialized_player_data = player_data.to_dict() 

        return serialized_player_data, self.is_special_duel
    
    def get_remaining_interactions(self):
        """
        Returns the number of remaining interactions in the duel
        """
        have_not_interacted = []
        remaining_interactions = 0
        for player in self.duel_players.keys():
            if self.duel_players[player].action is None:
                remaining_interactions += 1
                have_not_interacted.append(player)
        print(f"Have not interacted: {have_not_interacted}")
        print("All players: ", self.duel_players.keys())
        print(f"Remaining interactions: {remaining_interactions}")
        return remaining_interactions

    def duel_step(self):
        """
        Performs a step of the duel
        """
        # Deep copy of the duel players to send it to the admin
        duel_players_copy = deepcopy(self.duel_players)

        new_players = {}
        winner, loser = self.resolve_duel()

        if len(loser) > 0: 
            if len(loser) == 2: # Kick both players and add 2 new players
                self.duel_players.pop(loser[0]) 
                self.duel_players.pop(loser[1])

                new_player1 = self.add_new_player_to_duel()
                new_player2 = self.add_new_player_to_duel()
                
                # Special case: The last player doesnt' have an opponent, revive one
                if new_player1 is not None and new_player2 is None: 
                    # All players except the new player
                    logged_players = q.get_logged_players_names()
                    logged_players.remove(new_player1)
                    new_player2 = random.choice(logged_players)
                    self.duel_players[new_player2] = GunmanPlayer()

                if new_player1 is not None:
                    new_players[new_player1] = self.duel_players[new_player1]
                if new_player2 is not None:
                    new_players[new_player2] = self.duel_players[new_player2]

            else: # Kick 1 loser, steal coins and add 1 new player
                print(f"Loser: {loser[0]}")
                self.steal_coins(winner, loser[0])
                self.duel_players.pop(loser[0])
                new_player = self.add_new_player_to_duel()
                if new_player is None: # There are no remaining players
                    self.duel_players.pop(winner)
                else:
                    new_players[new_player] = self.duel_players[new_player]
                    self.update_winner_items(winner, duel_players_copy)

        # Reset the actions of the players
        for player in self.duel_players.values(): 
            player.action = None

        current_duel_players = {
            name: player.to_dict() 
            for name, player in duel_players_copy.items()
        }
        print(current_duel_players)

        next_duel_new_players = {
            name: player.to_dict() 
            for name, player in new_players.items()
        }
        print(next_duel_new_players)
        
        return current_duel_players, next_duel_new_players
    
    def update_winner_items(self, winner, duel_players_copy):
        """
        In case of having 0 bullets, the winner will have 1 bullet
        In case of having less than 2 shields, the winner will have 2 shields
        It also updates the duel players copy to send it to the admin
        """
        winner_bullets = self.duel_players[winner].bullets
        if winner_bullets == 0:
            self.duel_players[winner].bullets = 1
            duel_players_copy[winner].bullets = 1

        winner_shields = self.duel_players[winner].shields
        if winner_shields < 2:
            self.duel_players[winner].shields = 2
            duel_players_copy[winner].shields = 2

    def resolve_duel(self) -> tuple[str, list[str]]:
        """
            Determines the winner and loser of the duel if any
            Loser is a list as it can be 1 or 2 players
        """
        winner = None
        loser = []
        player_names = list(self.duel_players.keys())
        actions = (self.duel_players[player_names[0]].action, self.duel_players[player_names[1]].action)

        if actions == ("shoot", "shoot"): #they both die
            loser = [player_names[0], player_names[1]]

        else: 
            if actions == ("shoot", "reload"): # One survives
                winner = player_names[0]
                loser.append(player_names[1])
            elif actions == ("reload", "shoot"): # One survives
                winner = player_names[1]
                loser.append(player_names[0])

        return winner, loser

    def steal_coins(self, winner, loser):
        q.add_coins_to_player(winner, self.COINS_TO_STEAL)
        q.add_coins_to_player(loser, -self.COINS_TO_STEAL)

    def special_duel_step(self):
        """
            Performs a step of the special duel: substracts a life from the loser if any
        """
        _, loser = self.resolve_duel()

        # If both players would have died, pardon them, so we don't substract lives
        if len(loser) < 2: 
            for player in loser:
                self.duel_players[player].lives -= 1

        for player in self.duel_players.values():
            player.action = None

        serialized_players = {
            name: player.to_dict() 
            for name, player in self.duel_players.items()
        }

        return serialized_players



    

