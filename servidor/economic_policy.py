from .models import Player, Prize, Coins_evolution, Prizes_evolution
from . import constants as c
from . import queries as q
from . import main_views
import random

class RegulatedPlayer:
    def __init__(self, nick: str, coins: int):
        self.nick = nick
        self.coin_change = coins

    def serialize(self):
        return {
            'nick': self.nick,
            'coin_change': self.coin_change
        }

class EconomicPolicy:
    def __init__(self):
        # Duels constants
        self.ELEGIBLE_ROUNDS_FOR_SPECIAL_DUEL_RICH = 10
        self.ELEGIBLE_ROUNDS_FOR_SPECIAL_DUEL_POOR = 5
        self.RICH_PERCENTILE = 70 
        self.POOR_PERCENTILE = 30

        # Aid constants
        self.aid_alpha = 80
        self.aid_beta = 1
        self.aid_gamma = 5
        self.aid_clip_coins = 5

        # Tax constants
        self.tax_alpha = 1
        self.tax_beta = 100 

        self.players_sorted_by_richness = self.get_players_sorted_by_richness()

    def get_players_sorted_by_richness(self):
        """
            Get the players sorted by the richness score
        """
        players = list(q.get_logged_players())
        players.sort(key=lambda x: self.get_player_richness_score(x.coins, x.prizes_earned), reverse=True)
        
        print(f'Players sorted by richness:')
        for player in players:
            print(f'Player {player.name} coins: {player.coins} prizes: {player.prizes_earned}, score: {self.get_player_richness_score(player.coins, player.prizes_earned)}')
        
        return players
    
    def get_players_above_percentile(self, percentile: int):
        """
            Get the players that are above the given percentile
            Percentiles are upside down (30 is 30% richest players)
            The +0.000001 is to avoid banker's rounding
        """
        percentile = 100 - percentile # Convert 70 to 30
        players = self.players_sorted_by_richness
        
        print(f'Players above percentile {percentile}:')
        for player in players[:round(len(players) * percentile / 100 + 0.000001)]:
            print(f'Player {player.name} coins: {player.coins} prizes: {player.prizes_earned}, score: {self.get_player_richness_score(player.coins, player.prizes_earned)}')
        
        return players[:round(len(players) * percentile / 100 + 0.000001)]
    
    def get_players_below_percentile(self, percentile: int):
        """
            Get the players that are below the given percentile
            Percentiles are normal (30 is 30% poorest players)
            The +0.000001 is to avoid banker's rounding
        """
        players = self.players_sorted_by_richness
        
        print(f'Players below percentile {percentile}:')
        for player in players[-round(len(players) * percentile / 100 + 0.000001):]:
            print(f'Player {player.name} coins: {player.coins} prizes: {player.prizes_earned}, score: {self.get_player_richness_score(player.coins, player.prizes_earned)}')
        
        return players[-round(len(players) * percentile / 100 + 0.000001):]
    
    def is_player_rich(self, player: Player):
        """
        Determines if a player is in the top 30% richest players
        """
        # Update the sorted players list to get current state
        players_above_percentile = self.get_players_above_percentile(self.RICH_PERCENTILE)
        
        # Compare by unique player name
        return any(p.name == player.name for p in players_above_percentile)
    
    def get_games_since_last_aid(self, player: Player, game_number: int):
        """
            Get the number of games since the player has been in a aid
        """
        if player.last_aid_game_number == -1:
            return game_number
        else:
            return game_number - player.last_aid_game_number
    
    def get_apt_poorest_player(self, game_number: int):
        """
            Get the poorest player that is apt for duel or santa
        """
        for player in self.players_sorted_by_richness:
            games_since_last_aid = self.get_games_since_last_aid(player, game_number)
            if games_since_last_aid >= self.ELEGIBLE_ROUNDS_FOR_SPECIAL_DUEL_POOR:
                return player
        return None

    def decide_call_special_duel(self, prize_winner_name: str, game_number: int):
        """
            If the game number is greater than 10

            If the prize winner:
            - is in the top 3 richest players 
            - has not being in a duel for more than 10 rounds
            It has a 50% chance to enter a duel

            In that case, it is paired with the poorest player
            - that has not been in a duel for more than 5 rounds
        """
        prize_winner = next(player for player in self.players_sorted_by_richness if player.name == prize_winner_name)
        is_rich = self.is_player_rich(prize_winner)
        print(f'Player {prize_winner_name} is rich: {is_rich}')

        if prize_winner.last_rich_duel_game_number == -1: # If the player has not been in a duel yet
            rounds_since_last_rich_duel = game_number
        else:
            rounds_since_last_rich_duel = game_number - prize_winner.last_rich_duel_game_number

        print(f'Player {prize_winner_name} rounds since last rich duel: {rounds_since_last_rich_duel}')  
        random_number = random.randint(0, 100)
        print(f'Random number: {random_number}')

        # A duel is going to be called
        if is_rich and rounds_since_last_rich_duel >= self.ELEGIBLE_ROUNDS_FOR_SPECIAL_DUEL_RICH and random_number < 50: 
            print(f'A duel is going to be called')
            # Get the poorest player that has not been in a duel yet
            chosen_player = self.get_apt_poorest_player(game_number)

            if chosen_player is not None: # Almost impossible to be None
                print(f'Chosen player: {chosen_player.name}')
                q.set_player_last_rich_duel_game_number(prize_winner, game_number)
                q.set_player_last_aid_game_number(chosen_player, game_number)
                print(f'Player {prize_winner_name} last rich duel game number: {game_number}')
                print(f'Player {chosen_player.name} last aid game number: {game_number}')

            return chosen_player

        else: # No duel is going to be called
            return None

    def decide_call_santa(self, game_number: int):
        """
            If the game number is greater than 20
            - Get the poorest player
            - If the poorest player has no prizes
                - 80% chance to call santa
            - If the poorest player has 1 prize
                - 50% chance to call santa
        """
        call_santa = False
        chosen_player = self.get_apt_poorest_player(game_number)
        if chosen_player is not None: # Almost impossible to be None
            print(f'Chosen player: {chosen_player.name}')
            random_number = random.randint(0, 100)
            print(f'Random number: {random_number}')
            if chosen_player.prizes_earned == 0:
                print(f'Chosen player has 0 prizes')
                if random_number < 80:
                    call_santa = True
                    print(f'Santa is called')
            elif chosen_player.prizes_earned == 1:
                print(f'Chosen player has 1 prize')
                if random_number < 50:
                    call_santa = True
                    print(f'Santa is called')
        if call_santa:
            return chosen_player
        else:
            return None

    def decide_call_special_duel_or_santa(self, prize_winner_name: str,game_number: int):
        """
            Santa can be called if we are in the 60% or more of the game
            If santa is not called, a special duel can be called
            A special duel can be called if we are in the 40% or more of the game
        """
        print(f'Players sorted by richness:')
        # Update it
        self.players_sorted_by_richness = self.get_players_sorted_by_richness()
        for player in self.players_sorted_by_richness:
            print(f'Player {player.name} coins: {player.coins} prizes: {player.prizes_earned}, score: {self.get_player_richness_score(player.coins, player.prizes_earned)}')
        remaining_games = q.get_remaining_prizes()
        percent_of_total_games = game_number / (remaining_games + game_number)
        print(f'Percent of total games: {percent_of_total_games}')
        chosen_player = None
        call_santa = False
        call_special_duel = False

        if percent_of_total_games > 0.6:
            print(f'Deciding if santa is called')
            chosen_player = self.decide_call_santa(game_number)
            if chosen_player is not None:
                call_santa = True 
                print(f'Santa is called')
        if percent_of_total_games > 0.4 and chosen_player is None:
            print(f'Deciding if special duel is called')
            chosen_player = self.decide_call_special_duel(prize_winner_name, game_number)
            if chosen_player is not None:
                call_special_duel = True
                print(f'Special duel is called')

        return chosen_player, call_santa, call_special_duel

    def balance_inflation_deflation(self, game_number: int):
        """
            Balance inflation and deflation to have a stable monetary base
            If the monetary base is greater than the initial one, tax the players
            If the monetary base is less than the initial one, aid the players
        """
        # Update it
        self.players_sorted_by_richness = self.get_players_sorted_by_richness()
        players = q.get_logged_players()
        constant_monetary_base = len(players) * c.INITIAL_COINS # Fix monetary base
        print(f'Constant monetary base: {constant_monetary_base}')
        self.free_coins_to_very_poor_players(players) # Free 5 coins to the poorest players

        current_monetary_base = self.get_current_monetary_base(players)
        print(f'Current monetary base: {current_monetary_base}')
        regulated_players = []
        if current_monetary_base > constant_monetary_base: #Inflation
            total_tax = current_monetary_base - constant_monetary_base
            print(f'Inflation: {total_tax}')
            regulated_players = self.tax_players(total_tax)
        elif current_monetary_base < constant_monetary_base: #Deflation
            available_aid = constant_monetary_base - current_monetary_base
            print(f'Deflation: {available_aid}')
            regulated_players = self.aid_players(available_aid, game_number)
        else:
            print(f'No inflation or deflation')

        # Now we have the definitive coins for each player after this game
        main_views.main_controller_.insert_coins_evolution_for_game()

        return regulated_players

    def free_coins_to_very_poor_players(self, players: list[Player]):
        """
            Free coins to the poorest players
        """
        for player in players:
            if player.coins < self.aid_clip_coins:
                q.add_coins_to_player(player.name, self.aid_clip_coins - player.coins)
                print(f'Player {player.name} has been aided with {self.aid_clip_coins - player.coins} coins')

    def get_current_monetary_base(self, players: list[Player]):
        current_monetary_base = 0
        for player in players:
            current_monetary_base += player.coins
        return current_monetary_base

    def tax_players(self, total_tax: int):
        taxed_players = []
        taxable_players = self.get_players_above_percentile(self.RICH_PERCENTILE) # Tax the top 30% 
        scores = []
        for player in taxable_players:
            scores.append(self.get_player_richness_score(player.coins, player.prizes_earned))

        total_scores = sum(scores)
        percentage_scores = [score / total_scores for score in scores] # Transform scores in percentages
        tax_per_player = self.distribute_coins(total_tax, percentage_scores)

        for i, player in enumerate(taxable_players):
            print(f'Player {player.name} has been taxed with {-tax_per_player[i]} coins')
            q.add_coins_to_player(player.name, -tax_per_player[i])
            taxed_players.append(RegulatedPlayer(player.nick, -tax_per_player[i]).serialize())

        return taxed_players

    def aid_players(self, available_aid: int, game_number: int):
        aided_players = []
        aidable_players = self.get_players_below_percentile(self.POOR_PERCENTILE) # Aid the poorest 30% by coins
        scores = []
        for player in aidable_players:
            scores.append(self.get_player_aid_score(player.coins, self.player_new_earned_coins(player, game_number), player.prizes_earned))
            print(f'Player {player.name} with coins: {player.coins}, new earned coins: {self.player_new_earned_coins(player, game_number)}, prizes: {player.prizes_earned} has an aid score of: {scores[-1]}')

        total_scores = sum(scores)
        percentage_scores = [score / total_scores for score in scores] # Transform scores in percentages
        aid_per_player = self.distribute_coins(available_aid, percentage_scores)

        for i, player in enumerate(aidable_players):
            print(f'Player {player.name} has been aided with {aid_per_player[i]} coins')
            q.add_coins_to_player(player.name, aid_per_player[i])
            aided_players.append(RegulatedPlayer(player.nick, aid_per_player[i]).serialize())

        return aided_players


    def distribute_coins(self, total_coins, player_percentages):
        """
            Assign all coins according to the percentages
            It has a second fase to assign the remainders
            TODO: If there is a tie, how to distribute the coin? (now it is given to the first one)
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

        
    def player_new_earned_coins(self, player: Player, game_number: int):
        if game_number - 1 == 0: # If we are in the first round
            past_game_coins = c.INITIAL_COINS
        else:
            past_game_coins = q.get_player_coins_at_game_number(player, game_number - 1)

        new_earned_coins = player.coins - past_game_coins
        
        return new_earned_coins

    def get_player_aid_score(self, coins, new_earned_coins, prizes):
        """
            -Quadratic inversely proportional to their coins
            -Directly proportional to their last round gains (boost)
            -Inversely proportional to the prizes
        """
        if coins < self.aid_clip_coins: # Don't divide by 0, adjust to 5 to don't clip the distrib
            coins = self.aid_clip_coins
        if prizes == 0: # Don't divide by 0, adjust to 0.5 to don't clip the distrib
            prizes = 0.5
        if new_earned_coins < 0: # Boost doesn't have effect
            new_earned_coins = 0

        normalized_coins = coins / self.aid_alpha
        normalized_prizes = prizes / self.aid_gamma
        score = (1 / normalized_coins)**2 + self.aid_beta * new_earned_coins + (1 / normalized_prizes)
        return score
    
    def get_player_richness_score(self, coins, prizes):
        """
            -Quadratic proportional to coins
            -Quadratic proportional to prizes
        """
        score = (self.tax_alpha * coins)**2 + (self.tax_beta * prizes)**2
        return score

