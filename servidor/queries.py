from .models import Player, Prize, Coins_evolution, Prizes_evolution
from . import constants as c

def is_player_first_time(name):
    """
        It is the first time that the player logs in if the field 'nick' is empty 
        and the coins are the initial ones
    """
    first_time = False
    try:
        jugador = Player.objects.get(name=name)

        print(f"Player nick in DB: {jugador.nick}")

        # Comprueba si el campo 'nick' está vacío
        if (jugador.nick == None or jugador.nick == '') and jugador.coins == c.INITIAL_COINS:
            first_time = True
        else:
            first_time =  False

    except Player.DoesNotExist:
        first_time = None

    return first_time

def logout_player(name):
    """
        Empty the player's nick to indicate that it is not logged
    """

    try:
        jugador = Player.objects.get(name=name)
        jugador.nick = ''
        jugador.save()

    except Player.DoesNotExist:
        print('No existe el jugador ' + name + 'que se quiere desloguear')

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
        print('No existe el jugador ' + name + 'que se quiere resetear')

def change_player_nick(name, nick):
    """
        Change the player's nick
    """

    try:
        jugador = Player.objects.get(name=name)
        jugador.nick = nick
        jugador.save()

    except Player.DoesNotExist:
        print('No existe el jugador ' + name + 'al que se le quiere cambiar el nick')

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
        
def get_logged_players():
    """
        Gets all logged players from DB (with nick not empty)
    """
    players = Player.objects.filter(nick__isnull=False).exclude(nick__exact='')
    return players

def get_logged_players_names():
    """
        Gets the names of all logged players from DB
    """
    players_names = []
    players = get_logged_players()
    for player in players:
        players_names.append(player.name)

    return players_names

def get_player_attributes(name):
    """
        Gets the attributes of a player
    """
    try:
        jugador = Player.objects.get(name=name)
        return jugador.attributes

    except Player.DoesNotExist:
        print('No existe el jugador ' + name + 'del que se quieren obtener los atributos')

def get_0_coins_players():
    """
        Gets the players with 0 coins
    """
    players = Player.objects.filter(coins=0)
    return players

def add_coins_to_player(name, coins):
    """
        Give coins to a player, it can be negative. If the quantitity is going to be negative, we put it to 0
    """
    try:
        player = Player.objects.get(name=name)
        if player.coins + coins < 0:
            player.coins = 0
        else:
            player.coins += coins
        player.save()

    except Player.DoesNotExist:
        print('No existe el jugador ' + name + 'al que se le quieren dar monedas')

def get_player_coins(name):
    """
        Gets the coins of a player
    """
    try:
        jugador = Player.objects.get(name=name)
        return jugador.coins

    except Player.DoesNotExist:
        print('No existe el jugador ' + name + 'del que se quieren obtener las monedas')

def get_available_prizes():
    """
        Gets all prizes with amount > 0
    """
    prizes = Prize.objects.filter(amount__gt=0) # it can't be negative, only exclude 0
    return prizes

def adjust_prizes_probabilities(out_of_stock_prize):
    """ 
        The probability of the out of stock prize is distributed 
        among the other available prizes depending on 
        their actual probability to cover the empty space
    """
    out_of_stock_prob = out_of_stock_prize.prob
    prizes = get_available_prizes()
    for prize in prizes:
        if(prize.amount > 0):
            prize.prob += (out_of_stock_prob * prize.prob) / (1 - out_of_stock_prob)
            prize.save()

def get_prize(prize_type):
    """
        Gets a prize from DB by its type
    """
    try:
        prize = Prize.objects.get(type=prize_type)
        return prize

    except Prize.DoesNotExist:
        print('No existe el premio ' + prize_type + ' que se quiere obtener')

def decrement_prize_amount(prize):
    """
        Decrement by 1 to the amount of a prize object
    """
    prize.amount -= 1
    prize.save()

def insert_coins_evolution(player, coins, game_number): #TODO implement game number
    """
        Insert a new coins_evolution object in DB 
    """
    coins_evolution = Coins_evolution(player=player, coins=coins, game_number=game_number)
    coins_evolution.save()

def get_current_game_number():
    """
        The current game number is queried by getting the highest value of current's date game number
    """
    today = 0 # TODO manage dates
    current_game_number = (
        Coins_evolution.objects
        .filter(date=today)
        .order_by('-game_number')
        .first()
    )
    return current_game_number

def get_player_coins_at_game_number(player, game_number):
    """
        Get the number of coins that a player has at a specific game number
    """
    return Coins_evolution.objects.get(player=player, game_number=game_number)


def insert_prize_evolution(player, prize, game_number):
    """
        Insert a new prizes_evolution object in DB
    """
    prize_evolution = Prizes_evolution(player=player, prize=prize, game_number=game_number)
    prize_evolution.save()
