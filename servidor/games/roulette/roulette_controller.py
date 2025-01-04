from servidor import classes
from servidor import main_views
from servidor import queries as q
import threading

class RouletteGame:
    def __init__(self):
        self.x2_bets = ['R', 'B', 'E', 'O', '1H', '2H']
        self.x3_bets = ['1T', '2T', '3T', '1R', '2R', '3R']
        self.red_numbers = (1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36)
        self.players_bets = {}  # Dictionary to store player bets
        self.players_lock = threading.Lock()

    def register_player_bets(self, name, bets):
        """
            Register the bets of a player if the roulette is not spinning
        """
        if not main_views.main_controller_.get_can_players_interact(): # The roulette has spun
            return False
        else: 
            self.players_lock.acquire()
            player_bets = []
            if len(bets) > 0:
                for player_bet in bets: #Add bets to player
                    bet = classes.Bet(player_bet['type'], player_bet['amount'])
                    player_bets.append(bet) #Add bet to player
                    q.add_coins_to_player(name, -bet.amount) #Substract coins
            else: # If the bet is empty, add a null bet
                bets = classes.Bet('Null', 0)
                player_bets.append(bets)

            self.players_bets[name] = player_bets # Add player bets to memory
            self.players_lock.release()
            return True

    def compute_winner_bets(self, result):
        result = int(result)
        winner_bets = []

        if (result != 0):
            if (result in self.red_numbers):
                winner_bets.append('R')
            else:
                winner_bets.append('B')
                
            if (result % 2 == 0):
                winner_bets.append('E')
            else:
                winner_bets.append('O')
                
            if (result <= 18):
                winner_bets.append('1H')
            else:
                winner_bets.append('2H')
                
            if (result <= 12):
                winner_bets.append('1T')
            elif (result <=24):
                winner_bets.append('2T')
            else:
                winner_bets.append('3T')
                
            if (result % 3 == 1):
                winner_bets.append('3R')
            elif (result % 3 == 2):
                winner_bets.append('2R')
            else:
                winner_bets.append('1R')
                
        return winner_bets

    def assign_prizes(self, result):

        winner_bets = self.compute_winner_bets(result)

        self.players_lock.acquire()
        for player_name in self.players_bets.keys():
            for bet in self.players_bets[player_name]:
                if bet.type == 'Null': # If bet is null, skip it
                    continue

                # If bet is winner, add prize
                if (bet.type in winner_bets):
                    if (bet.type in self.x2_bets):
                        q.add_coins_to_player(player_name, bet.amount * 2)
                    elif (bet.type in self.x3_bets):
                        q.add_coins_to_player(player_name, bet.amount * 3)

                if (bet.type == result): # If bet is winner, add prize
                    q.add_coins_to_player(player_name, bet.amount * 36)
                        
        self.players_bets = {} # Reset the bets (as the init method won't be called again)
        self.players_lock.release()        


    def get_remaining_interactions(self):
        """
            Returns the number of remaining interactions in the roulette
            (logged players who are not in the players_bets dictionary)
        """
        logged_players = q.get_logged_players_names()
        have_not_interacted = []
        remaining_interactions = 0
        for player in logged_players:
            if player not in self.players_bets.keys():
                remaining_interactions += 1
                have_not_interacted.append(player)
        print(f"Have not interacted: {have_not_interacted}")
        print("All players: ", logged_players)
        print(f"Remaining interactions: {remaining_interactions}")
        return remaining_interactions

