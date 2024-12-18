from .models import Player, Prize, Coins_evolution, Prizes_evolution
from . import constants as c
from . import queries as q

# Battles TODO add a field in Players table that says that they have been involved in a battle

# Redistribution without inflation

def redistribution():
    players = q.get_logged_players()
    constant_monetary_base = len(players) * c.INITIAL_COINS # Fix monetary base
    current_monetary_base = get_current_monetary_base(players)
    if current_monetary_base > constant_monetary_base: #Inflation
        total_tax = current_monetary_base - constant_monetary_base
        tax_players(players, total_tax, current_monetary_base)
    elif current_monetary_base < constant_monetary_base: #Deflation
        available_aid = constant_monetary_base - current_monetary_base
        aid_players(players, available_aid, current_monetary_base)

def get_current_monetary_base(players: list[Player]):
    current_monetary_base = 0
    for player in players:
        current_monetary_base += player.coins
    return current_monetary_base

def tax_players(players: list[Player], total_tax: int, current_monetary_base: int):
    pass

def aid_players(players: list[Player], available_aid: int, current_monetary_base: int):
    """
        Determine how much to aid each player:
        Players that have coins below the threshold get a financial aid:
        -Inversely proportional to their coins
        -Directly proportional to their last round gains (boost)
    """
    aid_threshold = current_monetary_base / len(players) # Average coins per player TODO maybe median
    aidable_players = []
    scores = []
    for player in players:
        if player.coins < aid_threshold:
            aidable_players.append(player)
            scores.append(get_player_aid_score(player.coins), player_new_earned_coins(player), aid_threshold)

    total_scores = sum(scores)
    percentage_scores = [score / total_scores for score in scores] # Transform scores in percentages
    aid_per_player = distribute_coins(available_aid, percentage_scores)

    for i, player in enumerate(aidable_players):
        player.coins += aid_per_player[i]

def distribute_coins(total_coins, player_percentages):
    """
        Assign all coins according to the percentages
        It has a second fase to assign the remainders
        TODO si hay empate como repartir la moneda
    """
    # Step 1: Calculate each player's share and initialize distributions
    initial_distributions = []
    remainders = []

    for percentage in player_percentages:
        share = percentage * total_coins  # Directly calculate share
        integer_part = int(share)  # Integer part of the coins to assign initially
        remainder = share - integer_part  # Remaining fractional part
        initial_distributions.append(integer_part)
        remainders.append(remainder)

    # Step 2: Distribute remaining coins based on largest remainders
    remaining_coins = total_coins - sum(initial_distributions)
    for i in sorted(range(len(remainders)), key=lambda i: remainders[i], reverse=True)[:remaining_coins]:
        initial_distributions[i] += 1  # Give one extra coin to players with the highest remainder

    return initial_distributions

    
def player_new_earned_coins(player: Player):
    past_game_number = q.get_current_game_number - 1
    if past_game_number == 0: # If we are in the first round
        past_round_coins = c.INITIAL_COINS
    else:
        past_round_coins = q.get_player_coins_at_game_number(player, past_game_number)

    new_earned_coins = player.coins - past_round_coins
    
    return new_earned_coins

def get_player_aid_score(coins, new_earned_coins, threshold, alpha, beta):
    """
        -Inversely proportional to their coins
        -Directly proportional to their last round gains (boost)
    """
    if coins == 0: # Don't divide by 0, adjust to 3 to don't clip the distrib
        coins = 3
    coins = coins / threshold
    new_earned_coins = new_earned_coins
    score = score = alpha * (1 / coins) + beta * new_earned_coins
    return score

# Prizes cost a percentage of your patrimony: implemented in the prize assignation function register_prize_winner()

# Balance games to avoid inflation

