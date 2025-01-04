
def distribute_coins(total_coins, player_percentages):
    """
        Assign all coins according to the percentages
        It has a second fase to assign the remainders
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


def get_player_richness_score(coins, prizes):
    """
        -Directly proportional to coins (quadratic)
        -Directly proportional to prizes (quadratic)
    """
    score = (tax_alpha * coins)**2 + (tax_beta * prizes)**2
    return score


available_aid = 50
tax_alpha = 1
tax_beta = 50

# Test cases
tests = [
    {'name': 'Player 0', 'coins': 0, 'prizes': 0},
    {'name': 'Player B', 'coins': 0, 'prizes': 2},
    {'name': 'Player D', 'coins': 0, 'prizes': 4},

    {'name': 'Player 0', 'coins': 50, 'prizes': 0},
    {'name': 'Player B', 'coins': 50, 'prizes': 2},
    {'name': 'Player D', 'coins': 50, 'prizes': 4},

    {'name': 'Player 0', 'coins': 100, 'prizes': 0},
    {'name': 'Player B', 'coins': 100, 'prizes': 2},
    {'name': 'Player D', 'coins': 100, 'prizes': 4},

    {'name': 'Player C', 'coins': 200, 'prizes': 0},
    {'name': 'Player E', 'coins': 200, 'prizes': 2},
    {'name': 'Player G', 'coins': 200, 'prizes': 4},

    {'name': 'Player F', 'coins': 300, 'prizes': 0},
    {'name': 'Player H', 'coins': 300, 'prizes': 2},
    {'name': 'Player J', 'coins': 300, 'prizes': 4},
]

test_results = []
scores = []
for player in tests:
    score = get_player_richness_score(player['coins'], player['prizes'])
    scores.append(score)
    test_results.append([player['name'], player['coins'], player['prizes'], score])

total_scores = sum(scores)

percentage_scores = [score / total_scores for score in scores] # Transform scores in percentages
tax_per_player = distribute_coins(available_aid, percentage_scores)

for i, player in enumerate(test_results):
    player.append(percentage_scores[i])
    player.append(tax_per_player[i])

coins = 0
# Display the results of additional tests
for x in test_results:
    print(x)
    coins += x[-1]
print(coins)

# Sort the players by richness score
sorted_players = sorted(tests, key=lambda x: get_player_richness_score(x['coins'], x['prizes']), reverse=True)
print(sorted_players)
print(len(sorted_players))
print('\n')
percentile = 30
rich = sorted_players[:round(len(sorted_players) * percentile / 100 + 0.000001)]
print(rich)
print(len(rich))

print('\n')
percentile = 30
poor = sorted_players[-round(len(sorted_players) * percentile / 100 + 0.000001):]
print(poor)
print(len(poor))







