import math

def steal_coins_per_player(winner_team_len: int, loser_team_len: int, coins_per_player: int) -> None:
    """
        Steal coins from the loser team knowing the coins to steal per player:
        - If the number of players of each team is the same, the coins are stolen from each loser to each winner
        - Else: it may happen that coins are decimal, in that case, some inflation is generated
            (always print coins instead of stealing them and generate deflation coins)

    """

    if winner_team_len == loser_team_len: # Easy case, the coins flow from each loser to each winner
        coins_to_steal_to_each_loser = coins_per_player
        total_coins_to_steal = loser_team_len * coins_to_steal_to_each_loser
        coins_to_give_to_each_winner = coins_to_steal_to_each_loser
        total_coins_to_give = winner_team_len * coins_to_give_to_each_winner
        extra_coins = total_coins_to_give - total_coins_to_steal # Always 0

    elif winner_team_len > loser_team_len: # There are more players in the winner team
        # The coins are distributed evenly between the winner team (rounded up)
        coins_to_steal_to_each_loser = coins_per_player
        total_coins_to_steal = loser_team_len * coins_to_steal_to_each_loser
        coins_to_give_to_each_winner = math.ceil(total_coins_to_steal / winner_team_len)
        total_coins_to_give = coins_to_give_to_each_winner * winner_team_len
        extra_coins = total_coins_to_give - total_coins_to_steal # Positive if coins_to_steal_to_each_loser is not multiple of len(winner_team)
    else: # There are more players in the loser team
        coins_to_give_to_each_winner = coins_per_player
        total_coins_to_give = winner_team_len * coins_to_give_to_each_winner
        coins_to_steal_to_each_loser = math.floor(total_coins_to_give / loser_team_len)
        total_coins_to_steal = loser_team_len * coins_to_steal_to_each_loser
        extra_coins = total_coins_to_give - total_coins_to_steal # Positive if coins_to_steal_to_each_loser is not multiple of len(winner_team)

    print(f'Coins to steal to each loser: {coins_to_steal_to_each_loser}')
    print(f'Total coins to steal: {total_coins_to_steal}')
    print(f'Coins to give to each winner: {coins_to_give_to_each_winner}')
    print(f'Total coins to give: {total_coins_to_give}')
    print(f'Inflation coins: {extra_coins}')

    return coins_to_give_to_each_winner, coins_to_steal_to_each_loser


def steal_coins_total(winner_team_len: int, loser_team_len: int, total_coins: int) -> None:
    """
        Steal coins from the loser team, knowing the total coins to steal:
        - If the number of players of each team is the same, the coins are stolen from each loser to each winner
        - Else: it may happen that coins are decimal, in that case, some inflation is generated
            (always print coins instead of stealing them and generate deflation coins)

    """

    if winner_team_len == loser_team_len: # Easy case, the coins flow from each loser to each winner
        coins_to_steal_to_each_loser = math.floor(total_coins / winner_team_len) # Take into account the number of players of the winner/loser team
        total_coins_to_steal = loser_team_len * coins_to_steal_to_each_loser
        coins_to_give_to_each_winner = math.ceil(total_coins / winner_team_len) # Take into account the number of players of the winner/loser team
        total_coins_to_give = winner_team_len * coins_to_give_to_each_winner
        extra_coins = total_coins_to_give - total_coins_to_steal # Always 0

    elif winner_team_len > loser_team_len: # There are more players in the winner team
        # The coins are distributed evenly between the winner team (rounded up)
        coins_to_steal_to_each_loser = math.floor(total_coins / loser_team_len) # Take into account the number of players of the loser team
        total_coins_to_steal = loser_team_len * coins_to_steal_to_each_loser
        coins_to_give_to_each_winner = math.ceil(total_coins / winner_team_len)
        total_coins_to_give = coins_to_give_to_each_winner * winner_team_len
        extra_coins = total_coins_to_give - total_coins_to_steal # Positive if coins_to_steal_to_each_loser is not multiple of len(winner_team)
    else: # There are more players in the loser team
        coins_to_give_to_each_winner = math.ceil(total_coins / winner_team_len) # Take into account the number of players of the winner team
        total_coins_to_give = winner_team_len * coins_to_give_to_each_winner
        coins_to_steal_to_each_loser = math.floor(total_coins / loser_team_len)
        total_coins_to_steal = loser_team_len * coins_to_steal_to_each_loser
        extra_coins = total_coins_to_give - total_coins_to_steal # Positive if coins_to_steal_to_each_loser is not multiple of len(winner_team)

    print(f'Coins to steal to each loser: {coins_to_steal_to_each_loser}')
    print(f'Total coins to steal: {total_coins_to_steal}')
    print(f'Coins to give to each winner: {coins_to_give_to_each_winner}')
    print(f'Total coins to give: {total_coins_to_give}')
    print(f'Inflation coins: {extra_coins}')

    return coins_to_give_to_each_winner, coins_to_steal_to_each_loser