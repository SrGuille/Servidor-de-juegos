import threading
from servidor import main_controller
import random
from typing import List, Tuple, Dict
from servidor import queries as q
import math

# Constants
MOVES_PER_STEP = 1
TEAM_NAMES = ['Verde', 'Rojo']
REWARD_PER_ADVANTAGE = 5

# Global variables
teams_with_names = {0: [], 1: []} # Dict with the players of each team (with player's names)


def register_player_move(name: str, move: str) -> None:
    """
        Register the move if the player has not reached 
        the maximum number of moves in an step
    """

    if(main_controller.get_can_players_interact()): # If play time has started and not finished
        main_controller.get_players_lock().acquire()
        player_moves = main_controller.get_player_elems(name)
        if(player_moves != None): # If player exists in memory
            number_previous_moves = len(player_moves)
            if(number_previous_moves < MOVES_PER_STEP):
                player_moves.append(move)
                print('Player ' + name + ' registered move ' + move)
        main_controller.get_players_lock().release()


def get_players_moves() -> Dict[str, int]:
    """
        Returns the count of all types of moves of all players in a dictionary
    """
    main_controller.get_players_lock().acquire()

    players_moves = main_controller.get_players_elems()
    total_moves = {'up': 0, 'down': 0, 'left': 0, 'right': 0}
    for player_name, player_moves in players_moves.items():
        for move in player_moves:
            total_moves[move] += 1
        players_moves[player_name] = []  # Reemplazar con una nueva lista vacía

    main_controller.get_players_lock().release()

    return total_moves

def get_democratic_move()-> Tuple[int, int]:
    """ 
        Returns the result of the step (the sum of the forces in both directions)
        divided by 2 (to avoid too much movement)
    """
    forces = get_players_moves()

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
    
    vertical_force = math.ceil(vertical_force / 2) * vertical_sign
    horizontal_force = math.ceil(horizontal_force / 2) * horizontal_sign

    """
    vertical_force = forces['down'] - forces['up']
    horizontal_force = forces['right'] - forces['left']
    """

    return vertical_force, horizontal_force


def create_teams() -> Dict[int, List[str]]:
    global teams_with_names
    """
        Assign players to 2 teams randomly (choose a player and add it 
        to a team, then choose another player and add it to the other team)
        In case there is an odd number of players, one team will have 1 more player
        It fills 2 data structures:
        - Returns a dictionary with the team of each player (with player's names)
        - Fills the global variable teams with the players of each team (with player's Objects)
    """
    teams_with_names = {0: [], 1: []} # Dict with the players of each team (with player's names)
    list_players = q.get_logged_players_names()
    random.shuffle(list_players) # Shuffle the list to avoid deterministic teams
    
    for i in range(0, len(list_players), 2):
        team = random.randint(0, 1)
        # Add first player to the random team
        teams_with_names[team].append(list_players[i])
        if(len(list_players) > i + 1): # There is a player for the other team
            # Add second player to the other team
            other_team = (team + 1) % 2
            teams_with_names[other_team].append(list_players[i+1])
    
    print(teams_with_names)
    return teams_with_names

def get_my_team(player_name: str) -> str:
    """
        Returns the team name of a player
    """
    for team in teams_with_names:
        if(player_name in teams_with_names[team]):
            return TEAM_NAMES[team]
    return None


def decide_winner_and_give_prizes(winner_per_step: List[int]) -> str:
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
        else:
            winner_team_num = 2

        winner_msj = f"¡Ha ganado el equipo {TEAM_NAMES[winner_team_num - 1]} con una diferencia de {str(winner_advantage)} casillas!"
        winner_team = teams_with_names[winner_team_num - 1] # Get the list of players of the winner team
        give_prizes(winner_team, winner_advantage)

    return winner_msj
    
def give_prizes(winner_team: List[str], winner_advantage: int) -> None:
    """
        Give coins to the winner team players
    """
    main_controller.get_players_lock().acquire()
    for player_name in winner_team:
        q.add_coins_to_player(player_name, winner_advantage * REWARD_PER_ADVANTAGE)
    main_controller.get_players_lock().release()

    