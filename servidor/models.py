from django.db import models
from typing import List

# Create your models here.

class Player():
    def __init__(self, name: str, nick: str, id: int):
        self.name: str = name
        self.nick:str = nick
        self.id: int = id
        self.logged: bool = True
        self.coins: int = 200 #Initial coins
        self.elements: List[any] = [] #List of game elements

# For roulette and multibandits
class Bet():
    def __init__(self, type: str, amount: int):
        self.type: str = type
        self.amount: int = amount

class Prize():
    def __init__(self, type: str, prob: float, value: int):
        self.type: str = type
        self.prob: float = prob
        self.value: int = value
        self.amount: int = 0 #Will be incremented when players are registered

# For hangman
class Guess():
    def __init__(self, letter):
        self.letter = letter
