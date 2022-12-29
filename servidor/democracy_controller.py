import threading
from . import models
import json
from . import main_controller
import random

num_moves_per_step = 3
num_steps_per_round = 30
team_names = ['Azul', 'Naranja']
teams = [[], []]
board = []
rows = 10
cols = 10

# Initialize the board with half of the cells for each team
def create_board():
    global board
    board = [[0 for x in range(cols)] for y in range(rows)] # Initialize the board
    random_cells = random.sample(range(0, rows * cols - 1), rows * cols // 2) # Random cells for team orange
    for cell in random_cells:
        board[cell // cols][cell % cols] = 1

# Register the move if the player has not reached the maximum number of moves
def register_player_move(player_name, move):
    listen_client_calls = main_controller.get_listen_client_calls()
    if(listen_client_calls):
        main_controller.get_players_lock().acquire()
        player = main_controller.get_player(player_name)
        if(player != None):
            number_previous_moves = len(player.elements)
            if(number_previous_moves < num_moves_per_step):
                player.elements.append(move)
        main_controller.print_players()
        main_controller.get_players_lock().release()

# Returns the result of the round
def compute_democracy_move():
    main_controller.get_players_lock().acquire()
    players = main_controller.get_players()
    forces = {'up': 0, 'down': 0, 'left': 0, 'right': 0}
    for player in players:
        for move in player.elements:
            forces[move] = forces[move] + 1
        player.elements = []

    vertical_force = forces['up'] - forces['down']
    horizontal_force = forces['left'] - forces['right']

    main_controller.get_players_lock().release()
    return vertical_force, horizontal_force

# Assign players to 2 teams randomly (choose a player and add it to a team, then choose another player and add it to the other team)
# In case there is an odd number of players, one team will have one more player
def make_two_teams(players):
    for i in range(0, len(players), 2):
        team = random.randint(0, 1)
        teams[team].append(players[i])
        if(len(players) > i + 1): # There is a player for the other team
            teams[(team + 1) % 2].append(players[i+1]) 
    return teams

# Returns the team of a player
def get_my_team(player_name):
    team_counter = 0
    for team in teams:
        for player in team:
            if(player.name == player_name):
                return team_names[team_counter]
        team_counter += 1
    return None

def get_teams():
    return teams


    