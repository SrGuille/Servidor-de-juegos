from . import queries as q
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import random
import os


def get_coins_evolution():
    """
        Get the coins of all players during each game
    """
    coins_evolution = {} # {player: [list of coins]}
    players = q.get_players_names()
    for player in players:
        coins_evolution[player] = []
        for game_number in range(4, q.get_stored_game_number() + 1): # All the games in the DB
            coins = q.get_player_coins_at_game_number(player, game_number)
            coins_evolution[player].append(coins)

    coins_evolution = correct_coins_evolution(coins_evolution)
    
    return coins_evolution


def correct_coins_evolution(coins_evolution):
    """
        If the data of a whole game is 0 (all the players have 0 coins), we make the average of the previous and next game
    """
    players = list(coins_evolution.keys())
    num_games = len(next(iter(coins_evolution.values())))

    for game_idx in range(1, num_games - 1):
        all_zero = all(coins_evolution[player][game_idx] == 0 for player in players)
        
        if all_zero:
            for player in players:
                prev_game = coins_evolution[player][game_idx - 1]
                if prev_game != 0:
                    next_game = coins_evolution[player][game_idx + 1]
                else: # If the player left in the prev, conserve it at 0
                    prev_game = 0
                    next_game = 0
                coins_evolution[player][game_idx] = (prev_game + next_game) / 2

    return coins_evolution

def split_coins_evolution(coins_evolution, group_size=5):
    """
        Split the coins evolution into groups of players
        Compute the average number of coins for each player and group 
        (the best x players and so on)
    """
    # Calculate the average number of coins for each player
    player_averages = {player: sum(coins) / len(coins) for player, coins in coins_evolution.items()}
    # Sort players by their average number of coins in descending order
    sorted_players = sorted(player_averages, key=player_averages.get, reverse=True)

    # Split players into groups
    groups = [sorted_players[i:i + group_size] for i in range(0, len(sorted_players), group_size)]

    # Create a list of dictionaries where each dictionary represents a group of players and their coin evolution
    group_dicts = []
    for group in groups:
        group_dict = {player: coins_evolution[player] for player in group}
        group_dicts.append(group_dict)

    return group_dicts

def plot_coins_evolution(evolution, prize_winners, width=10, height=5, year=2024, id=0):
    """
        Plot the coin evolution of all players
    """
    plt.style.use('dark_background')  # Use a dark background style
    plt.rcParams['font.family'] = 'serif'
    plt.figure(figsize=(width, height))  # Set the figure size (width, height)

    # Generate a colormap with enough unique colors
    num_players = len(evolution)
    colors = plt.cm.get_cmap('tab20', num_players)  # 'tab20' colormap has 20 distinct colors

    all_game_numbers = set()
    for idx, (player, coins) in enumerate(evolution.items()):
        if coins:  # Check if the list is not empty
            # Filter out zero values
            filtered_coins = [coin if coin != 0 else None for coin in coins]
            game_numbers = list(range(1, len(coins) + 1))
            plt.plot(game_numbers, filtered_coins, label=player, marker='o', markersize=3, color=colors(idx))
            all_game_numbers.update(game_numbers)

            # Plot special points for prize-winning rounds
            for game_number, coin in zip(game_numbers, coins):
                if game_number in prize_winners and prize_winners[game_number] == player:
                    plt.plot(game_number, coin, marker='*', markersize=10, color=colors(idx))

    plt.xlabel('Juegos', color='white')
    plt.ylabel('Monedas', color='white')

    if isinstance(id, int): # If id is a number
        group = 'grupo ' + str(id)
    else:
        group = id
        
    plt.title(f'Evolución de las monedas ({group})', color='white')

    plt.legend()

    # Set the x-axis ticks to show exact game numbers
    ax = plt.gca()
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.xticks(sorted(all_game_numbers), color='white')  # Ensure all game numbers appear as ticks
    plt.yticks(color='white')
    
    # Save the plot as an image file
    filename = 'evolucion_monedas_' + str(year) + '_' + str(id)
    full_path = f'servidor/static/img/stats/{str(year)}/{filename}.png'
    if(os.path.exists(full_path)):
        os.remove(full_path)
    plt.savefig(full_path, dpi=150, bbox_inches='tight')

def get_prizes_evolution():
    """
        Get the prizes of all players during each game
    """
    prizes_evolution = {} # {player: [list of prizes]}
    prize_winners = {}  # {game_number: player}

    smallest_game_number = -1 # If there are garbage game numbers: start from number 1
    for game_number in range(1, q.get_stored_game_number() + 1): # All the games in the DB
        winner = q.get_prize_winner(game_number)
        if winner is not None:
            if smallest_game_number == -1:
                smallest_game_number = game_number
            if winner not in prizes_evolution:
                prizes_evolution[winner] = [game_number - smallest_game_number + 1]
            else:
                prizes_evolution[winner].append(game_number - smallest_game_number + 1)
            
            prize_winners[game_number - smallest_game_number + 1] = winner

    return prizes_evolution, prize_winners

def plot_prizes_evolution(prizes_evolution, width=15, height=5, year=2024):
    """
        Plot the prizes evolution of all players
    """
    plt.style.use('dark_background')  # Use a dark background style
    plt.rcParams['font.family'] = 'serif'  # Set the font family
    plt.figure(figsize=(width, height))  # Set the figure size (width, height)

    # Generate a colormap with enough unique colors
    num_players = len(prizes_evolution)
    colors = plt.cm.get_cmap('tab20', num_players)  # 'tab20' colormap has 20 distinct colors

    all_game_numbers = set()
    for idx, (player, games) in enumerate(prizes_evolution.items()):
        if games:  # Check if the list is not empty
            # Put the number of prizes as the y-axis values
            cumulative_prizes = [i + 1 for i in range(len(games))]
            plt.plot(games, cumulative_prizes, marker='*', markersize=10, label=player, color=colors(idx))
            all_game_numbers.update(games)

    plt.xlabel('Juegos', color='white')
    plt.ylabel('Número de premios', color='white')

    plt.title(f'Evolución de los premios', color='white')
    plt.legend()

    # Set the x-axis ticks to show exact game numbers
    ax = plt.gca()
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.xticks(sorted(all_game_numbers), color='white')  # Ensure all game numbers appear as ticks
    plt.yticks(color='white')

    # Save the plot as an image file
    filename = 'evolucion_regalos_' + str(year)
    full_path = f'servidor/static/img/stats/{str(year)}/{filename}.png'
    if(os.path.exists(full_path)):
        os.remove(full_path)
    plt.savefig(full_path, dpi=150, bbox_inches='tight')

def generate_test(num_players, game_numbers):
    """
        Generate a test with a list of players and their coins evolution
    """
    test = {}
    for i in range(num_players):
        test[i] = []
        for j in range(game_numbers):
            test[i].append(random.randint(0, 100))

    return test

#test = generate_test(15, 50)
#plot_evolution(test, 'Monedas', 20, 10)







