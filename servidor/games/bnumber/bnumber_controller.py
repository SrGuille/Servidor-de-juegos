from servidor import main_views
import random
from typing import List, Tuple, Dict
from servidor import queries as q
import math
import threading

class BNumberGame:

    def __init__(self):

        self.LIST_SIZE = 9
        self.NUMBER_RANGE = 89 # 0 to 89
        self.REWARD_PER_ADVANTAGE = 5

        self.teams_with_names = {'Verde': [], 'Rojo': []}  # Dict with the players of each team
        self.team_names = ['Verde', 'Rojo']
        self.teams_positions = {'Verde': self.get_empty_list(), 'Rojo': self.get_empty_list()} # Dict with the positions of each team
        self.teams_new_number = {'Verde': -1, 'Rojo': -1} # Dict with the new number of each team
        self.players_lock = threading.Lock()

    def get_empty_list(self) -> List[int]:
        return [-1] * self.LIST_SIZE

    def register_position(self, name: str, position: int) -> Tuple[int, bool]:
        """
            Insert the given number in the given position of the team
            If the list is full, the team has won: return -100
            Else: generate a new number for the team 
            - if it is impossible to insert, reset the list: return impossible and new number
            - else: return the new number
        """
        
        new_number = -1 # For the case where the game is not ready
        is_impossible = False

        if not main_views.main_controller_.get_can_players_interact(): # The game is not ready
            return new_number, is_impossible
        
        else: # The game is ready
            self.players_lock.acquire()
            
            player_team, _, _ = self.get_my_team(name)
            number = self.teams_new_number[player_team]
            team_positions = self.teams_positions[player_team]
            team_positions[position] = number
            
            print('Team ' + player_team + ' inserted number at position ' + str(position))
            
            if self.get_number_of_non_empty_positions(player_team) == self.LIST_SIZE: # The team has filled the list
                new_number = -100 # The team has won
            else:
                new_number = self.generate_new_number(player_team)
                self.teams_new_number[player_team] = new_number
                # Is impossible to insert: reset the list and generate a new number
                if self.is_impossible_insert(player_team, new_number):
                    is_impossible = True
                    self.teams_positions[player_team] = self.get_empty_list()

            self.players_lock.release()

        return new_number, is_impossible


    def generate_new_number(self, team: str) -> int:
        """
            Generates a new number for the team (can't be repeated)
        """
        team_positions = self.teams_positions[team]
        new_number = random.randint(0, self.NUMBER_RANGE)
        while new_number in team_positions:
            new_number = random.randint(0, self.NUMBER_RANGE)
        return new_number
    
    def is_impossible_insert(self, team: str, number: int) -> bool:
        """
            Returns true if the new number is impossible to insert in the list
            - If the number is smaller than the first number of the list
            - If the number is bigger than the last number of the list
            - If the number is in the interval of 2 consecutive numbers of the list
        """
        is_impossible = False
        team_positions = self.teams_positions[team]

        for i in range(len(team_positions)):
            if team_positions[i] != -1: # The position is not empty
                if i == 0: 
                    if number < team_positions[i]: # If smaller than the first number
                        is_impossible = True
                        break
                elif i == len(team_positions) - 1: # If bigger than the last number
                    if number > team_positions[i]:
                        is_impossible = True
                        break
                else:
                    if team_positions[i - 1] != -1: # Previous position is not empty
                        # If the number fits in the interval of 2 consecutive numbers
                        if number < team_positions[i] and number > team_positions[i - 1]:
                            is_impossible = True
                            break

        return is_impossible
    
    def get_number_of_non_empty_positions(self, team: str) -> int:
        """
            Returns the number of positions of the team that are not empty
        """
        non_empty_positions = [i for i, number in enumerate(self.teams_positions[team]) if number != -1]
        return len(non_empty_positions)

    def create_teams(self) -> None:
        """
            Assign players to 2 teams randomly (choose a player and add it 
            to a team, then choose another player and add it to the other team)
            In case there is an odd number of players, one team will have 1 more player
            
            The method returns the initial number of players to display in the admin screen
        """
        list_players = q.get_logged_players_names()
        random.shuffle(list_players) # Shuffle the list to avoid deterministic teams
        
        for i in range(0, len(list_players), 2):
            team_number = random.randint(0, 1)
            team_name = self.team_names[team_number]
            # Add first player to the random team
            self.teams_with_names[team_name].append(list_players[i])
            if(len(list_players) > i + 1): # There is a player for the other team
                # Add second player to the other team
                other_team_number = (team_number + 1) % 2
                other_team_name = self.team_names[other_team_number]
                self.teams_with_names[other_team_name].append(list_players[i+1])
        
        print(self.teams_with_names)
        new_number_green = self.generate_new_number('Verde')
        self.teams_new_number['Verde'] = new_number_green
        new_number_red = self.generate_new_number('Rojo')
        self.teams_new_number['Rojo'] = new_number_red
        return new_number_green, new_number_red

    def get_my_team(self, player_name: str) -> Tuple[str, str]:
        """
            Returns the team name of a player 
            and the name of the leader of the team (first position of the team)
        """
        player_team = None
        leader = None
        first_number = -1
        print(player_name)
        for team_name, team_players in self.teams_with_names.items():
            print(team_name, team_players)
            if(player_name in team_players):
                player_team = team_name
                leader = team_players[0]
                first_number = self.teams_new_number[team_name]
                break
        return player_team, leader, first_number
    
    def get_bnumber_data(self) -> Dict[str, List[int]]:
        """
            Returns the positions of each team
        """
        #serialize the positions of each team
        serialized_teams_positions = {
            team: positions 
            for team, positions in self.teams_positions.items()
        }
        serialized_teams_new_number = {
            team: new_number 
            for team, new_number in self.teams_new_number.items()
        }
        return serialized_teams_positions, serialized_teams_new_number

    def finish_bnumber(self) -> str:
        """
            Decides the winner team and gives prizes to the players of the winner team
        """
        # Number of seconds per team
        numbers_team_1 = self.get_number_of_non_empty_positions('Verde')
        numbers_team_2 = self.get_number_of_non_empty_positions('Rojo')

        winner_msj = "¡Ha habido un empate!"

        winner_advantage = abs(numbers_team_1 - numbers_team_2)

        if(winner_advantage > 0): # There is a winner
            if(numbers_team_1 > numbers_team_2):
                winner_team_name = 'Verde'
                loser_team_name = 'Rojo'
            else:
                winner_team_name = 'Rojo'
                loser_team_name = 'Verde'

            winner_msj = f"¡Ha ganado el equipo {winner_team_name} con una ventaja de {str(winner_advantage)} números!"
            winner_team = self.teams_with_names[winner_team_name]
            loser_team = self.teams_with_names[loser_team_name]
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

    