import threading
from servidor import main_controller
import random

# Constants
MOVES_PER_STEP = 1
TEAM_NAMES = ['Verde', 'Rojo']
REWARD_PER_ADVANTAGE = 5

# Global variables
teams = [[], []] # With player's Objects

# Register the move if the player has not reached the maximum number of moves
def register_player_move(player_name, move):
    if(main_controller.get_can_players_interact()): # If play time has started and not finished
        main_controller.get_players_lock().acquire()
        player = main_controller.get_player(player_name)
        if(player != None):
            number_previous_moves = len(player.elements)
            if(number_previous_moves < MOVES_PER_STEP):
                player.elements.append(move)
                print('Player ' + player_name + ' registered move ' + move)
        #main_controller.print_players()
        main_controller.get_players_lock().release()

# Returns the result of the round (the sum of the forces)
def get_democratic_move():
    main_controller.get_players_lock().acquire()
    players = main_controller.get_players()
    forces = {'up': 0, 'down': 0, 'left': 0, 'right': 0}
    for player in players.values():
        for move in player.elements:
            forces[move] = forces[move] + 1
        player.elements = []

    vertical_force = forces['down'] - forces['up']
    horizontal_force = forces['right'] - forces['left']

    main_controller.get_players_lock().release()
    return vertical_force, horizontal_force

# Assign players to 2 teams randomly (choose a player and add it to a team, then choose another player and add it to the other team)
# In case there is an odd number of players, one team will have one more player
def create_teams():
    main_controller.get_players_lock().acquire()
    players = main_controller.get_players()
    list_players = list(players.values())
    teams_with_names = {0: [], 1: []}
    for i in range(0, len(list_players), 2):
        team = random.randint(0, 1)
        # Add first player to the random team
        teams[team].append(list_players[i])
        teams_with_names[team].append(list_players[i].name)
        if(len(list_players) > i + 1): # There is a player for the other team
            # Add second player to the other team
            teams[(team + 1) % 2].append(list_players[i+1]) 
            teams_with_names[(team + 1) % 2].append(list_players[i+1].name)
    main_controller.get_players_lock().release()
    return teams_with_names

# Returns the team of a player (generallized for n teams)
def get_my_team(player_name):
    team_counter = 0
    for team in teams:
        for player in team:
            if(player.name == player_name):
                return TEAM_NAMES[team_counter]
        team_counter += 1 
    return None

"""
    Recieves an array with the winner team id of each step (doesn't include neutral steps)
    Computes the winner team and gives prizes to the players of the winner team
    If there is a tie, no prizes are given
    Returns a message with the winner team
"""
def decide_winner_and_give_prizes(winner_per_step):
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
            winner_team = 1
        else:
            winner_team = 2

        winner_msj = f"¡Ha ganado el equipo {TEAM_NAMES[winner_team - 1]} con una diferencia de {str(winner_advantage)} casillas!"
        give_prizes(winner_team, winner_advantage)

    return winner_msj
    
# Give prizes to the winner team
def give_prizes(winner_team, winner_advantage):
    main_controller.get_players_lock().acquire()
    for player in teams[winner_team - 1]:
        player.coins += winner_advantage * REWARD_PER_ADVANTAGE
    main_controller.get_players_lock().release()

    