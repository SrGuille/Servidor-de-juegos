
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


def get_player_aid_score(coins, new_earned_coins, threshold):
    """
        -Inversely proportional to their coins
        -Directly proportional to their last round gains (boost)
    """
    if coins == 0: # Don't divide by 0, adjust to 3 to don't clip the distrib
        coins = 3
    if new_earned_coins < 0: # Boost doesn't have effect
        new_earned_coins = 0
    coins = coins / threshold
    new_earned_coins = new_earned_coins
    score = score = mortadelo * (1 / coins) + filemon * new_earned_coins
    return score

mortadelo = 3.5
filemon = 1
threshold = 100
available_aid = 50

# Test cases
tests = [
    # Test 0: Varying earnings with the same coin counts
    {'name': 'Player 0', 'coins': 20, 'new_earned_coins': 0},
    {'name': 'Player A', 'coins': 20, 'new_earned_coins': 10},
    {'name': 'Player B', 'coins': 20, 'new_earned_coins': 20},

    # Test 1: Varying coin counts with the same earnings
    {'name': 'Player C', 'coins': 10, 'new_earned_coins': 10},
    {'name': 'Player D', 'coins': 10, 'new_earned_coins': -20},

    # Test 2: Edge cases with very low coins
    {'name': 'Player E', 'coins': 0, 'new_earned_coins': 0},
    {'name': 'Player F', 'coins': 5, 'new_earned_coins': 3},

    # Test 3: Edge cases with very high coin counts
    {'name': 'Player G', 'coins': 99, 'new_earned_coins': 70},
    {'name': 'Player H', 'coins': 99, 'new_earned_coins': 30},
    {'name': 'Player I', 'coins': 99, 'new_earned_coins': 0},
]

test_results = []
scores = []
for player in tests:
    score = get_player_aid_score(player['coins'], player['new_earned_coins'], threshold)
    scores.append(score)
    test_results.append([player['name'], player['coins'], player['new_earned_coins'], score])

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



