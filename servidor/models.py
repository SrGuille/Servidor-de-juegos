from django.db import models
from servidor import constants as c
# Create your models here.

class Player(models.Model):
    name = models.CharField(max_length=20)
    nick = models.CharField(max_length=25, blank=True, null=True) #Optional
    coins = models.IntegerField(default=c.INITIAL_COINS)
    attributes = models.CharField(max_length=100)

class Prize(models.Model):
    type = models.CharField(max_length=20)
    prob = models.FloatField()
    value = models.FloatField()
    amount = models.IntegerField()

class Coins_evolution(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    coins = models.IntegerField()
    date = models.DateField(auto_now_add=True)
    game_number = models.IntegerField()
    
    class Meta: # Define primary key
        unique_together = ('player', 'date', 'game_number')

class Prizes_evolution(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    prize = models.ForeignKey(Prize, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    game_number = models.IntegerField()

    class Meta: # Define primary key
        unique_together = ('player', 'prize', 'date', 'game_number')
        
