from servidor import main_views
import random
from typing import List, Tuple, Dict
from servidor import queries as q
import threading
import servidor.coin_stealing as cs
import math
from servidor.classes import Sock, SockPlayerBet

class SocksGame:
    def __init__(self):
        self.NUM_SOCKS = 8
        self.SOCKS_INTERVALS = ((0.3, 0.8), (1.5, 2))
        self.socks: List[Sock] = []
        self.players_previous_coins: Dict[str, int] = {}
        self.players_lock = threading.Lock()

    def initialize_socks(self):
        """Initializes the socks with min between 0.3-0.8 and max between 1.5-2"""
        self.players_previous_coins = {}
        self.socks = []
        for i in range(self.NUM_SOCKS):
            min_val = round(random.uniform(0.3, 0.8), 2)
            max_val = round(random.uniform(1.5, 2.0), 2)
            sock = Sock(min_val, max_val)
            self.socks.append(sock)
            print(f"Initialized sock {i} with min: {min_val}, max: {max_val}")
        return self.NUM_SOCKS

    def get_num_socks(self) -> int:
        """ Returns the number of socks available for the first round (player call)"""
        return self.NUM_SOCKS
    
    def run_socks_round(self):
        """
        Run multiplicator for each sock and process bets.
        For every sock, return:
            - List of top 3 players that have historically bet on it (name x times + if they are currently betting)
            - Total historical bets on that sock
        """
        self.players_lock.acquire()

        for sock in self.socks:
            multiplicator = sock.generate_multiplicator()
            print(f"Sock {sock} generated multiplicator: {multiplicator:.2f}")
            for bet in sock.bets:
                won_coins = round(bet.bet_amount * multiplicator)
                q.add_coins_to_player(bet.player_name, won_coins)

        socks_data_msj = self.get_socks_historical_data()

        # Clear bets for the next round
        for sock in self.socks:
            sock.clear_bets()

        self.players_lock.release()

        return socks_data_msj
    
    def get_socks_historical_data(self) -> List[Dict]:
        """
        Returns historical data for each sock:
            - List of top 3 players that have historically bet on it (name x times + if they are currently betting)
            - Total historical bets on that sock
        """
        socks_data_msjs = []
        for sock in self.socks:
            socks_data_msj = ""
            # Count historical bets
            bet_counts = sock.historical_bets
            # Sort players by number of bets
            sorted_bets = sorted(bet_counts.items(), key=lambda x: x[1], reverse=True)
            top_players = sorted_bets[:3]
            for player, count in top_players:
                socks_data_msj += f"{player} x{count}"
                is_currently_betting = any(bet.player_name == player for bet in sock.bets)
                if is_currently_betting:
                    socks_data_msj += " (sigue aquí) <br>"
                else:
                    socks_data_msj += " (se ha ido) <br>"

            total_historical_bets = sum(bet_counts.values())
            socks_data_msj += f"Total apuestas históricas: {total_historical_bets}"  

            socks_data_msjs.append(socks_data_msj)
        return socks_data_msjs

    def get_socks_average_performance(self):
        socks_average_performance = []
        for sock in self.socks:
            if len(sock.historical_performances) > 0:
                average_performance = sum(sock.historical_performances) / len(sock.historical_performances)
            else:
                average_performance = 0
            socks_average_performance.append(round(average_performance, 2))
        return socks_average_performance
    
    def register_sock_bet(self, player_name: str, sock_id: int, coins: int) -> bool:
        """
        Registers a bet for a player on a specific sock.
        Returns True if the bet was successfully registered, False otherwise.
        """
        valid = False

        if not main_views.main_controller_.get_can_players_interact(): # The game is not ready
            return valid
        
        else: # The game is ready
            self.players_lock.acquire()

            valid = True

            sock = self.socks[sock_id]
            bet = SockPlayerBet(player_name, coins)
            sock.add_bet(bet)

            self.players_previous_coins[player_name] = q.get_player_coins(player_name)

            # Substract player coins
            q.add_coins_to_player(player_name, -coins)

            print(f"Player {player_name} bet {coins} on sock {sock_id}")

            self.players_lock.release()

        return valid
    
    def get_player_available_and_previous_coins(self, player_name: str) -> Tuple[int, int]:
        """
        Returns the number of available coins for the player
        """
        available_coins = q.get_player_coins(player_name)
        previous_coins = -1
        if player_name in self.players_previous_coins:
            previous_coins = self.players_previous_coins[player_name]

        print(f"Getting available coins for player: {player_name}")
        print(f"Available coins: {available_coins}")
        print(f"Previous coins: {previous_coins}")
        return available_coins, previous_coins
    
    def get_remaining_interactions(self):
        """
            Returns the number of remaining interactions in the roulette
            (logged players who are not in the bets of a sock yet)
        """
        logged_players = q.get_logged_players_names()
        have_interacted = []
        interactions = 0
        for player in logged_players:
            for sock in self.socks:
                has_bet = any(bet.player_name == player for bet in sock.bets)
                if has_bet:
                    interactions += 1
                    have_interacted.append(player)
                    break

        have_not_interacted = [p for p in logged_players if p not in have_interacted]
        remaining_interactions = len(have_not_interacted)
                    
        print(f"Have not interacted: {have_not_interacted}")
        print("All players: ", logged_players)
        print(f"Remaining interactions: {remaining_interactions}")
        return remaining_interactions