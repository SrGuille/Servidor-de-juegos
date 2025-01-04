from servidor import main_views
import random
from typing import List, Tuple, Dict
from servidor import queries as q
import math
import time
import threading
class DemocracyGame:

    def __init__(self):
        self.clock_time = 0
        self.teams_with_names = {0: [], 1: []}  # Dict with the players of each team
        self.players_moves = {}  # Store player moves internally
        self.players_lock = threading.Lock()
        
        # Constants
        self.MOVES_PER_STEP = 1
        self.TEAM_NAMES = ['Verde', 'Rojo']
        self.REWARD_PER_ADVANTAGE = 5
        self.FORCE_DIVISOR = 2 # To avoid too much movement

    def init_clock(self) -> None:
        """Initialize the game clock, synched with the admin client"""
        self.clock_time = time.time()

    def get_time_until_next_second(self) -> float:
        """
            Returns the time until the next second starts
        """
        time_since_clock = time.time() - self.clock_time
        return 1000 - (time_since_clock * 1000)

    def register_player_move(self, name: str, move: str) -> Tuple[bool, int, float]:
        """
            Register the move if the player has not reached 
            the maximum number of moves in an step (1)
        """
        time_until_next_second = -1 # For the case where the game is not ready

        if not main_views.main_controller_.get_can_players_interact(): # The game is not ready
            return time_until_next_second
        
        else: # The game is ready
            self.players_lock.acquire() # Lock to don't race with get_democratic_move()
            
            time_until_next_second = self.get_time_until_next_second()
            if name not in self.players_moves: # Init the list the first time
                self.players_moves[name] = []
            
            if len(self.players_moves[name]) < self.MOVES_PER_STEP:
                self.players_moves[name].append(move)
                print('Player ' + name + ' registered move ' + move)
            
            self.players_lock.release()

        return time_until_next_second

    def get_and_reset_players_moves(self) -> Dict[str, int]:
        """
            Returns the count of all types of moves of all players in a dictionary and resets the moves of all players
        """
        total_moves = {'up': 0, 'down': 0, 'left': 0, 'right': 0}
        for player_name, player_moves in self.players_moves.items():
            for move in player_moves:
                total_moves[move] += 1
            self.players_moves[player_name] = []  # Reset the moves of the player

        return total_moves


    def get_democratic_move(self) -> Tuple[int, int]:
        """ 
            Returns the result of the step (the sum of the forces in both directions)
            divided by 2 (to avoid too much movement)
        """
        self.players_lock.acquire()

        global clock_time
        clock_time = time.time()  # Reset the clock time

        forces = self.get_and_reset_players_moves()

        vertical_sign = 0
        horizontal_sign = 0

        if forces['up'] > forces['down']:
            vertical_sign = -1
        elif forces['up'] < forces['down']:
            vertical_sign = 1

        if forces['left'] > forces['right']:
            horizontal_sign = -1
        elif forces['left'] < forces['right']:
            horizontal_sign = 1

        vertical_force = abs(forces['up'] - forces['down'])
        horizontal_force = abs(forces['right'] - forces['left'])
        
        vertical_force = math.ceil(vertical_force / self.FORCE_DIVISOR) * vertical_sign
        horizontal_force = math.ceil(horizontal_force / self.FORCE_DIVISOR) * horizontal_sign

        """
        vertical_force = forces['down'] - forces['up']
        horizontal_force = forces['right'] - forces['left']
        """

        self.players_lock.release()

        return vertical_force, horizontal_force


    def create_teams(self) -> Dict[int, List[str]]:
        """
            Assign players to 2 teams randomly (choose a player and add it 
            to a team, then choose another player and add it to the other team)
            In case there is an odd number of players, one team will have 1 more player
            It fills 2 data structures:
            - Returns a dictionary with the team of each player (with player's names)
            - Fills the global variable teams with the players of each team (with player's Objects)
        """
        self.teams_with_names = {0: [], 1: []} # Dict with the players of each team (with player's names)
        list_players = q.get_logged_players_names()
        random.shuffle(list_players) # Shuffle the list to avoid deterministic teams
        
        for i in range(0, len(list_players), 2):
            team = random.randint(0, 1)
            # Add first player to the random team
            self.teams_with_names[team].append(list_players[i])
            if(len(list_players) > i + 1): # There is a player for the other team
                # Add second player to the other team
                other_team = (team + 1) % 2
                self.teams_with_names[other_team].append(list_players[i+1])
        
        print(self.teams_with_names)
        return self.teams_with_names

    def get_my_team(self, player_name: str) -> str:
        """
            Returns the team name of a player
        """
        for team in self.teams_with_names:
            if(player_name in self.teams_with_names[team]):
                return self.TEAM_NAMES[team]
        return None


    def decide_winner_and_give_prizes(self, winner_per_step: List[int]) -> str:
        """
        Recieves an array with the winner team id of each step (without neutral steps)
        Computes the winner team and gives prizes to the players of the winner team
        If there is a tie, no prizes are given
        Returns a text message with the winner team to display in the admin page
        """
        print(winner_per_step)
        # Number of seconds per team
        steps_team_1 = 0
        steps_team_2 = 0 

        winner_msj = "¡Ha habido un empate!"

        for color in winner_per_step:
            if(color == 1):
                steps_team_1 += 1
            else:
                steps_team_2 += 1

        winner_advantage = abs(steps_team_1 - steps_team_2)

        if(winner_advantage > 0): # There is a winner
            if(steps_team_1 > steps_team_2):
                winner_team_num = 1
                loser_team_num = 2
            else:
                winner_team_num = 2
                loser_team_num = 1

            winner_msj = f"¡Ha ganado el equipo {self.TEAM_NAMES[winner_team_num - 1]} con una diferencia de {str(winner_advantage)} casillas!"
            winner_team = self.teams_with_names[winner_team_num - 1] # Get the list of players of the winner team
            loser_team = self.teams_with_names[loser_team_num - 1] # Get the list of players of the loser team
            self.give_prizes(winner_team, loser_team, winner_advantage)

        return winner_msj
        
    def give_prizes(self, winner_team: List[str], loser_team: List[str], winner_advantage: int) -> None:
        """
            Steal coins from the loser team:
            - If the number of players of each team is the same, the coins are stolen from each loser to each winner
            - Else: it may happen that coins are decimal, in that case, some inflation is generated
              (always print coins instead of stealing them and generate deflation coins)

        """
        self.players_lock.acquire()
        if len(winner_team) == len(loser_team): # Easy case, the coins flow from each loser to each winner
            coins_to_steal_to_each_loser = winner_advantage * self.REWARD_PER_ADVANTAGE
            total_coins_to_steal = len(loser_team) * coins_to_steal_to_each_loser
            coins_to_give_to_each_winner = coins_to_steal_to_each_loser
            total_coins_to_give = len(winner_team) * coins_to_give_to_each_winner
            extra_coins = total_coins_to_give - total_coins_to_steal # Always 0

        elif len(winner_team) > len(loser_team): # There is an extra player in the winner team
            # The coins are distributed evenly between the winner team (rounded up)
            coins_to_steal_to_each_loser = winner_advantage * self.REWARD_PER_ADVANTAGE
            total_coins_to_steal = len(loser_team) * coins_to_steal_to_each_loser
            coins_to_give_to_each_winner = math.ceil(total_coins_to_steal / len(winner_team))
            total_coins_to_give = coins_to_give_to_each_winner * len(winner_team)
            extra_coins = total_coins_to_give - total_coins_to_steal # Positive if coins_to_steal_to_each_loser is not multiple of len(winner_team)
        else: # There is an extra player in the loser team
            coins_to_give_to_each_winner = winner_advantage * self.REWARD_PER_ADVANTAGE
            total_coins_to_give = len(winner_team) * coins_to_give_to_each_winner
            coins_to_steal_to_each_loser = math.floor(total_coins_to_give / len(loser_team))
            total_coins_to_steal = len(loser_team) * coins_to_steal_to_each_loser
            extra_coins = total_coins_to_give - total_coins_to_steal # Positive if coins_to_steal_to_each_loser is not multiple of len(winner_team)

        print(f'Coins to steal for each loser: {coins_to_steal_to_each_loser}')
        print(f'Total coins to steal: {total_coins_to_steal}')
        print(f'Coins to give for each winner: {coins_to_give_to_each_winner}')
        print(f'Total coins to give: {total_coins_to_give}')
        print(f'Inflation coins: {extra_coins}')

        for player_name in winner_team:
            q.add_coins_to_player(player_name, coins_to_give_to_each_winner)

        for player_name in loser_team:
            q.add_coins_to_player(player_name, -coins_to_steal_to_each_loser)

        self.players_lock.release()

"""
coins_to_steal_to_each_loser = winner_advantage * self.REWARD_PER_ADVANTAGE
print(f'Coins to steal for each loser: {coins_to_steal_to_each_loser}')
total_coins_to_steal = len(loser_team) * coins_to_steal_to_each_loser
print(f'Total coins to steal: {total_coins_to_steal}')

# Ceiling division to avoid fractional coins (some extra non-existent coins can be added)
coins_to_give_to_each_winner = math.ceil(total_coins_to_steal / len(winner_team)) 
print(f'Coins to give to each winner: {coins_to_give_to_each_winner}')
extra_coins = (coins_to_give_to_each_winner * len(winner_team)) - total_coins_to_steal
print(f'Inflation coins: {extra_coins}')
"""
    