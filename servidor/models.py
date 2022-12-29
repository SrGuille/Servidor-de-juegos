from django.db import models

# Create your models here.

class Player():
    def __init__(self, name):
        self.name = name
        self.logged = True
        self.coins = 100 #Initial coins
        self.elements = [] #List of game elements

# For roulette and multibandits
class Bet():
    def __init__(self, type, amount):
        self.type = type
        self.amount = amount

class Prize():
    def __init__(self, type, prob, value):
        self.type = type
        self.prob = prob
        self.value = value
        self.amount = 0 #Will be incremented when players are registered

# For hangman
class Guess():
    def __init__(self, letter, apperances):
        self.letter = letter
        self.apperances = 0
