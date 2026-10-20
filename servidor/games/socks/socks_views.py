from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import redirect
from . import socks_controller
import json

socks_game = socks_controller.SocksGame()
from typing import List

def socks_admin_render(request):
    return render(request, 'socks/socks_admin.html')

def socks_player_render(request):
    return render(request, 'socks/socks_player.html')

# Admin

def initialize_socks(request):
    """ Initializes the socks with predefined min and max multiplicators """
    num_socks = socks_game.initialize_socks()
    return JsonResponse({'num_socks': num_socks}, safe=False)

def run_socks_round(request):
    """
    For every sock:
        - List of 3 players that have historically bet on it (name x times + if they are currently betting)
        - Total historical bets on that sock
    """
    socks_data_msjs = socks_game.run_socks_round()
    return JsonResponse({'socks_data_msjs': socks_data_msjs}, safe=False)

def get_socks_average_performance(request):
    socks_average_performance = socks_game.get_socks_average_performance()
    return JsonResponse({'socks_average_performance': socks_average_performance}, safe=False)

# Players

def get_num_socks(request):
    """ Returns the number of socks available for the first round (player call)"""
    num_socks = socks_game.get_num_socks()
    return JsonResponse({'num_socks': num_socks}, safe=False)

def send_sock_bet(request):
    # Go to the list of socks, find that one and add the player + bet
    # Substract player coins
    player_name = request.GET.get('player_name')
    sock_id = int(request.GET.get('sock_id'))
    coins = int(request.GET.get('coins'))
    valid = socks_game.register_sock_bet(player_name, sock_id, coins)
    return JsonResponse({'valid': valid}, safe=False)
    
def get_player_available_and_previous_coins(request) -> List[int]:
    """ Returns the number of available coins for the player """
    player_name = request.GET.get('player_name')
    coins, previous_coins = socks_game.get_player_available_and_previous_coins(player_name)
    return JsonResponse({'available_coins': coins, 'previous_coins': previous_coins}, safe=False)

        