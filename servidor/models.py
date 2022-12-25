from django.db import models

# Create your models here.

class Player():
    def __init__(self, name):
        self.name = name
        self.logged = True
        self.coins = 10
        self.bets = []


class Bet():
    def __init__(self, type, amount):
        self.type = type
        self.amount = amount
