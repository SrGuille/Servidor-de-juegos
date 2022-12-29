import threading
from . import models
import json
from . import main_controller
import random

num_moves_per_step = 3
team_names = ['Azul', 'Naranja']
teams = [[], []]
coins_per_second = 5

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
def get_democratic_move():
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
def create_teams(players):
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

def send_colors_per_second(colors_per_second):
    number_blue = 0
    number_orange = 0

    for color in colors_per_second:
        if(color == 0):
            number_blue += 1

        else:
            number_orange += 1

    if(number_blue != number_orange): # There is a winner
        if(number_blue > number_orange):
            winner_team = 0
        else:
            winner_team = 1

        winner_advantage = abs(number_blue - number_orange)
        give_prizes(winner_team, winner_advantage)
    
# Give prizes to the winner team
def give_prizes(winner_team, winner_advantage):
    for team in teams[winner_team]:
        for player in team:
            player.coins += winner_advantage * coins_per_second

    