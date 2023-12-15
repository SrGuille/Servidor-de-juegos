from .models import Player, Prize, Coins_evolution, Prizes_evolution
from . import constants as c

def is_player_first_time(name):
    """
        It is the first time that the player logs in if the field 'nick' is empty
    """
    first_time = False
    try:
        jugador = Player.objects.get(name=name)

        print(f"Player nick: {jugador.nick}")

        # Comprueba si el campo 'nick' está vacío
        if jugador.nick == None or jugador.nick == '':
            first_time = True
        else:
            first_time =  False

    except Player.DoesNotExist:
        first_time = None

    return first_time

def reset_player(name, nick):
    """
        Reset the player's nick and coins
    """

    try:
        jugador = Player.objects.get(name=name)
        jugador.nick = nick
        jugador.coins = c.INITIAL_COINS
        jugador.save()

    except Player.DoesNotExist:
        print('No existe el jugador ' + name + ' que se quiere resetear')


def add_new_prizes():
    """
        Add the player's prizes of a reseted player. 
        It adds 1 prize of each type and 10 candies
    """
    # Add 1 prize of each type
    prizes = Prize.objects.all()
    for prize in prizes: # Change each prize amount
        if prize.type == c.CANDY:
            prize.amount += 10
        else:
            prize.amount += 1
        
        prize.save()

def get_players_names():
    """
        Gets the names of all players from DB
    """
    players_names = []
    players = Player.objects.all()
    for player in players:
        players_names.append(player.name)

    return players_names
        

