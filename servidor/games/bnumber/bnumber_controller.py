from servidor import main_views
import random
from typing import List, Tuple, Dict
from servidor import queries as q
import threading
import servidor.coin_stealing as cs
import math

class BNumberGame:

    def __init__(self):

        self.LIST_SIZE = 8
        self.NUMBER_RANGE = (10 * self.LIST_SIZE) - 1
        self.REWARD_PER_ADVANTAGE = 5
        self.TEAM_NAMES = ('Verde', 'Rojo', 'Azul', 'Amarillo')  # Possible team names
        self.num_teams = 4  # Number of teams in the game

        # Dicts with: the players of each team, the positions of each team and the new number of each team
        self.teams_with_names = {}  
        self.teams_positions = {}
        self.teams_new_number = {}
        self.players_lock = threading.Lock()

    def get_empty_list(self) -> List[int]:
        return [-1] * self.LIST_SIZE
    
    def generate_new_number(self, team: str) -> int:
        """
            Generates a new number for the team (can't be repeated)
        """
        team_positions = self.teams_positions[team]
        new_number = random.randint(0, self.NUMBER_RANGE)
        while new_number in team_positions:
            new_number = random.randint(0, self.NUMBER_RANGE)
        return new_number
    
    def create_teams(self) -> dict:
        """
            Assign players to teams randomly.
            The method returns the initial number of each team to display in the admin screen
        """
        list_players = q.get_logged_players_names()
        random.shuffle(list_players) # Shuffle the list to avoid deterministic teams

        self.num_teams = min(self.num_teams, len(list_players)) # Adjust the number of teams if there are few players
        
        # Initialize the dicts
        self.teams_with_names = {team_name: [] for team_name in self.TEAM_NAMES[:self.num_teams]}
        self.teams_positions = {team_name: self.get_empty_list() for team_name in self.TEAM_NAMES[:self.num_teams]}

        # Assign players to teams in round-robin way (groups of num_teams)
        for i in range(0, len(list_players), self.num_teams):
            for team_number in range(self.num_teams):
                player_index = i + team_number
                if player_index < len(list_players): # There is a player for this team
                    team_name = self.TEAM_NAMES[team_number]
                    self.teams_with_names[team_name].append(list_players[player_index])
                    print(f'Player {list_players[player_index]} assigned to team {team_name}')
        
        print(self.teams_with_names)
        # Generate the initial number for each team
        for team_name in self.TEAM_NAMES[:self.num_teams]:
            self.teams_new_number[team_name] = random.randint(0, self.NUMBER_RANGE)
        
        return self.teams_new_number

    def get_my_team(self, player_name: str) -> Tuple[str, str, int]:
        """
            Returns the team name of a player 
            and the name of the leader of the team (first position of the team)
            and the first number of the team
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
    
    def has_finished(self) -> bool:
        """
            Returns true if the game is not ready (call it only after several seconds of starting the game)
        """
        has_finished = False
        if not main_views.main_controller_.get_can_players_interact(): # The game is not ready
            has_finished = True
        return has_finished

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
                self.teams_new_number[player_team] = new_number
            else:
                new_number = self.generate_new_number(player_team)
                self.teams_new_number[player_team] = new_number
                # Is impossible to insert: reset the list and generate a new number
                if self.is_impossible_insert(player_team, new_number):
                    is_impossible = True
                    self.teams_positions[player_team] = self.get_empty_list()

            self.players_lock.release()

        return new_number, is_impossible
    
    def is_impossible_insert(self, team: str, number: int) -> bool:
        """
            Returns true if the new number is impossible to insert in the list
            - If the number is smaller than the first number of the list
            - If the number is bigger than the last number of the list
            - If the number is in the interval of 2 consecutive numbers of the list
        """
        is_impossible = False
        team_positions = self.teams_positions[team]

        if team_positions[0] != -1 and number < team_positions[0]: # If smaller than the first pos (which is not empty)
            return True
        elif team_positions[-1] != -1 and number > team_positions[-1]: # If bigger than the last pos (which is not empty)
            return True

        for i in range(1, len(team_positions)):
            if team_positions[i] != -1 and team_positions[i - 1] != -1: # The current and the prev position are not empty
                if number < team_positions[i] and number > team_positions[i - 1]: # If in the interval of 2 consecutive numbers
                    is_impossible = True
                    break

        return is_impossible
    
    def get_number_of_non_empty_positions(self, team: str) -> int:
        """
            Returns the number of positions of the team that are not empty
        """
        non_empty_positions = [i for i, number in enumerate(self.teams_positions[team]) if number != -1]
        return len(non_empty_positions)
    
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
            Decides the winner team and gives prizes to the players of the winner team/s
            If there there is a team (can be many if they are simoultaneous) that has compleated the list, each player of that team wins REWARD_PER_FULL_LIST coins from the rest of teams
            Else, the team/s with more numbers filled wins, and each player of the winner team/s wins REWARD_PER_ADVANTAGE coins per advantage number from the rest of teams
        """
        # Numbers filled per team
        numbers_filled_per_team = {}
        for team_name in self.TEAM_NAMES[:self.num_teams]:
            numbers_filled_per_team[team_name] = self.get_number_of_non_empty_positions(team_name)

        # The number of filled positions of the best team/s
        max_filled = max(numbers_filled_per_team.values())
        is_full_filled = max_filled == self.LIST_SIZE  # There is at least one team that has completed the list
        
        # Determine the winner team/s
        winner_teams = [team for team, num_filled in numbers_filled_per_team.items() if num_filled == max_filled]
        print(f"Winner teams: {winner_teams}, with {max_filled} numbers filled.")
        loser_teams = [team for team in self.TEAM_NAMES[:self.num_teams] if team not in winner_teams]
        print(f"Loser teams: {loser_teams}, with respective filled numbers: {[numbers_filled_per_team[team] for team in loser_teams]}.")

        if loser_teams == []: # There is a tie
            winner_msj = "¡Ha habido un empate entre todos!"
            return winner_msj

        winner_advantages = {} # Dict with the advantage of the winner teams over each loser team
        coins_to_steal = {} # Dict with the coins to steal from the winner teams to each loser team

        for loser_team in loser_teams: # Loser teams own the coins to the winner players
            advantage = max_filled - numbers_filled_per_team[loser_team]
            winner_advantages[loser_team] = advantage
            coins_to_steal[loser_team] = math.ceil((advantage * self.REWARD_PER_ADVANTAGE) / len(winner_teams)) # Take into account the number of winner teams

        if is_full_filled: # There is at least one team that has completed the list
            win_type_str = "haber completado la lista"
        else:
            win_type_str = "haber llenado más números"
        
        winner_msj = ""
        if len(winner_teams) > 1:
            winner_teams_str = ", ".join(winner_teams[:-1]) + " y " + winner_teams[-1] 
            winner_msj += f"¡Han ganado los equipos {winner_teams_str}"
        else:
            winner_msj += f"¡Ha ganado el equipo {winner_teams[0]}"
        
        winner_msj += f" por {win_type_str}!<br>"

        for loser_team in loser_teams:
            winner_msj += f"<br>Ventaja sobre el equipo {loser_team}: {winner_advantages[loser_team]} números."

        # Give prizes to the winner team/s
        self.give_prizes(winner_teams, loser_teams, coins_to_steal)

        return winner_msj
        
    def give_prizes(self, winner_teams: List[str], loser_teams: List[str], coins_to_steal: Dict[str, int]) -> None:
        """
            Steal coins from the loser team:
            - If the number of players of each team is the same, the coins are stolen from each loser to each winner
            - Else: it may happen that coins are decimal, in that case, some inflation is generated
              (always print coins instead of stealing them and generate deflation coins)

        """
        self.players_lock.acquire()

        for winner_team in winner_teams: # Each winner team revieves coins from each loser team
            for loser_team in loser_teams:
                coins_to_give_to_each_winner, coins_to_steal_to_each_loser = cs.steal_coins_total(len(self.teams_with_names[winner_team]), len(self.teams_with_names[loser_team]), coins_to_steal[loser_team])

                for player_name in self.teams_with_names[winner_team]:
                    q.add_coins_to_player(player_name, coins_to_give_to_each_winner)

                for player_name in self.teams_with_names[loser_team]:
                    q.add_coins_to_player(player_name, -coins_to_steal_to_each_loser)

        self.players_lock.release()

