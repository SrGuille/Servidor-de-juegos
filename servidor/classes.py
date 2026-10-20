from typing import List, Any
import random

class Player():
    def __init__(self, name: str):
        self.name: str = name
        self.elements: List[Any] = [] #List of game elements

# For roulette and multibandits
class Bet():
    def __init__(self, type: str, amount: int):
        self.type: str = type
        self.amount: int = amount

# For palabrazo
class PalabrazoActor():
    def __init__(self, name: str, attributes: list):
        self.name: str = name
        self.attributes: list = attributes

class GunmanPlayer():
    def __init__(self):
        self.bullets: int = 1
        self.shields: int = 2
        self.action: str = None
        self.lives: int = 2 # For the special duel
        self.streak_length: int = 0 # streak length

    def to_dict(self): 
        return {
            'action': self.action,
            'bullets': self.bullets,
            'shields': self.shields,
            'lives': self.lives,
            'streak_length': self.streak_length
        }
    
    def to_string(self):
        return f"Action: {self.action}, Bullets: {self.bullets}, Shields: {self.shields}, Lives: {self.lives}"

class Sock:
    def __init__(self, min, max):
        self.min = min
        self.max = max
        self.bets = [] # List of SockPlayerBet
        self.historical_bets = {} # Player: number of bets
        self.historical_performances = [] # List of multiplicator performances

    def generate_multiplicator(self):
        multiplicator = random.uniform(self.min, self.max)
        self.historical_performances.append(multiplicator)

        return multiplicator

    def add_bet(self, bet):
        self.bets.append(bet)
        if bet.player_name in self.historical_bets:
            self.historical_bets[bet.player_name] += 1
        else:
            self.historical_bets[bet.player_name] = 1

    def add_performance(self, performance: float):
        self.performances.append(performance)

    def clear_bets(self):
        self.bets = []

    def __str__(self):
        return f"prizes x[min: {self.min:.2f}, max: {self.max:.2f}]"
    
class SockPlayerBet:
    def __init__(self, player_name, bet_amount):
        self.player_name = player_name
        self.bet_amount = bet_amount