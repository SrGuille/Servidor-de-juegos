from typing import List
import math

def give_prizes(winner_team: List[str], loser_team: List[str], winner_advantage: int) -> None:
    """
        Steal coins from the loser team:
        - If the number of players of each team is the same, the coins are stolen from each loser to each winner
        - Else: it may happen that coins are decimal, in that case, some inflation is generated
            (always print coins instead of stealing them and generate deflation coins)

    """

    if len(winner_team) == len(loser_team): # Easy case, the coins flow from each loser to each winner
        coins_to_steal_to_each_loser = winner_advantage * REWARD_PER_ADVANTAGE
        total_coins_to_steal = len(loser_team) * coins_to_steal_to_each_loser
        coins_to_give_to_each_winner = coins_to_steal_to_each_loser
        total_coins_to_give = len(winner_team) * coins_to_give_to_each_winner
        extra_coins = total_coins_to_give - total_coins_to_steal # Always 0

    elif len(winner_team) > len(loser_team): # There is an extra player in the winner team
        # The coins are distributed evenly between the winner team (rounded up)
        coins_to_steal_to_each_loser = winner_advantage * REWARD_PER_ADVANTAGE
        total_coins_to_steal = len(loser_team) * coins_to_steal_to_each_loser
        coins_to_give_to_each_winner = math.ceil(total_coins_to_steal / len(winner_team))
        total_coins_to_give = coins_to_give_to_each_winner * len(winner_team)
        extra_coins = total_coins_to_give - total_coins_to_steal # Positive if coins_to_steal_to_each_loser is not multiple of len(winner_team)
    else: # There is an extra player in the loser team
        coins_to_give_to_each_winner = winner_advantage * REWARD_PER_ADVANTAGE
        total_coins_to_give = len(winner_team) * coins_to_give_to_each_winner
        coins_to_steal_to_each_loser = math.floor(total_coins_to_give / len(loser_team))
        total_coins_to_steal = len(loser_team) * coins_to_steal_to_each_loser
        extra_coins = total_coins_to_give - total_coins_to_steal # Positive if coins_to_steal_to_each_loser is not multiple of len(winner_team)

    print(f'Coins to steal from each loser: {coins_to_steal_to_each_loser}')
    print(f'Total coins to steal: {total_coins_to_steal}')
    print(f'Coins to give to each winner: {coins_to_give_to_each_winner}')
    print(f'Total coins to give: {total_coins_to_give}')
    print(f'Inflation coins: {extra_coins}')

REWARD_PER_ADVANTAGE = 10
# Generate test cases

winner_team = ['player1', 'player2']
loser_team = ['player4', 'player5']
winner_advantage = 2
give_prizes(winner_team, loser_team, winner_advantage)
print('\n') # 100

winner_team = ['player1', 'player2', 'player3']
loser_team = ['player4', 'player5']
winner_advantage = 2
give_prizes(winner_team, loser_team, winner_advantage)
print('\n')

winner_team = ['player1', 'player2']
loser_team = ['player4', 'player5', 'player6']
winner_advantage = 2
give_prizes(winner_team, loser_team, winner_advantage)
print('\n') # 100

winner_team = ['player1', 'player2']
loser_team = ['player4', 'player5']
winner_advantage = 1
give_prizes(winner_team, loser_team, winner_advantage)
print('\n') # 100

winner_team = ['player1', 'player2', 'player3']
loser_team = ['player4', 'player5']
winner_advantage = 1
give_prizes(winner_team, loser_team, winner_advantage)
print('\n')

winner_team = ['player1', 'player2']
loser_team = ['player4', 'player5', 'player6']
winner_advantage = 1
give_prizes(winner_team, loser_team, winner_advantage)
print('\n') # 100

