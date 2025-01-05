
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


def get_player_aid_score(coins, new_earned_coins, prizes):
    """
        -Inversely proportional to their coins
        -Directly proportional to their last round gains (boost)
        -Inversely proportional to the prizes
    """
    if coins < aid_clip_coins: # Don't divide by 0, adjust to 3 to don't clip the distrib
        coins = aid_clip_coins
    if prizes == 0: # Don't divide by 0, adjust to 3 to don't clip the distrib
        prizes = 0.5
    if new_earned_coins < 0: # Boost doesn't have effect
        new_earned_coins = 0
    normalized_coins = coins / aid_alpha
    normalized_prizes = prizes / aid_gamma
    score = (1 / normalized_coins)**2 + aid_beta * new_earned_coins + (1 / normalized_prizes)
    return score


aid_alpha = 100
aid_beta = 1
aid_gamma = 30

aid_clip_coins = 5

available_aid = 50


# Test cases
tests = [
    # Test 0: Varying earnings with the same coin counts
    {'name': 'Player 0', 'coins': 20, 'new_earned_coins': 0, 'prizes': 0},
    {'name': 'Player A', 'coins': 20, 'new_earned_coins': 10, 'prizes': 0},
    {'name': 'Player B', 'coins': 20, 'new_earned_coins': 20, 'prizes': 0},

    # Test 0.5: Varying prizes with the same coin counts
    {'name': 'Player C', 'coins': 20, 'new_earned_coins': 0, 'prizes': 1},
    {'name': 'Player D', 'coins': 20, 'new_earned_coins': 10, 'prizes': 1},
    {'name': 'Player E', 'coins': 20, 'new_earned_coins': 20, 'prizes': 1},

    # Test 2: Edge cases with very low coins
    {'name': 'Player H', 'coins': 0, 'new_earned_coins': 0, 'prizes': 0},
    {'name': 'Player H', 'coins': 0, 'new_earned_coins': 0, 'prizes': 2},

    # Test 3: Edge cases with very high coin counts
    {'name': 'Player J', 'coins': 99, 'new_earned_coins': 70, 'prizes': 0},
    {'name': 'Player K', 'coins': 99, 'new_earned_coins': 30, 'prizes': 0},
    {'name': 'Player L', 'coins': 99, 'new_earned_coins': 0, 'prizes': 0},
    {'name': 'Player M', 'coins': 99, 'new_earned_coins': 70, 'prizes': 1},
    {'name': 'Player N', 'coins': 99, 'new_earned_coins': 30, 'prizes': 1},
    {'name': 'Player O', 'coins': 99, 'new_earned_coins': 0, 'prizes': 1},
]

test_results = []
scores = []
for player in tests:
    score = get_player_aid_score(player['coins'], player['new_earned_coins'], player['prizes'])
    scores.append(score)
    test_results.append([player['name'], player['coins'], player['new_earned_coins'], player['prizes'], score])

total_scores = sum(scores)

percentage_scores = [score / total_scores for score in scores] # Transform scores in percentages
aid_per_player = distribute_coins(available_aid, percentage_scores)

for i, player in enumerate(test_results):
    player.append(percentage_scores[i])
    player.append(aid_per_player[i])

coins = 0
# Display the results of additional tests
for x in test_results:
    print(x)
    coins += x[-1]
print(coins)



