from typing import List, Any

class Player():
    def __init__(self, name: str):
        self.name: str = name
        self.elements: List[Any] = [] #List of game elements

# For roulette and multibandits
class Bet():
    def __init__(self, type: str, amount: int):
        self.type: str = type
        self.amount: int = amount

# For hangman
class Actor():
    def __init__(self, name: str, attribute: str):
        self.name: str = name
        self.attribute: str = attribute

class HangmanPlayer():
    def __init__(self):
        self.num_wrong_guesses: int = 0
        self.earnings: int = 0

class Guess():
    def __init__(self, num_appereances: int, first_player: str):
        self.num_appereances: int = num_appereances
        self.players: [str] = [first_player] # List of players that guessed this letter (the rest will be added later)
