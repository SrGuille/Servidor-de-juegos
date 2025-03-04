from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import redirect
from servidor import main_controller
from . import roulette_controller
import json

roulette_game = roulette_controller.RouletteGame()

# Create your views here.

def roulette_admin_render(request):
    return render(request, 'roulette/roulette_admin.html')

def roulette_player_render(request):
    return render(request, 'roulette/roulette_player.html')

def send_roulette_result(request):
    result = request.GET.get('result')
    print(result)
    roulette_game.assign_prizes(result)
    return JsonResponse({'status': 'ok'}, safe=False)

def send_player_bets(request):
    global number_bets
    bets_str = request.GET.get('bets') #Get json
    bets = json.loads(bets_str) #Convert json to dict
    name = bets['player_name']
    bets = bets['bets']
    bets = json.loads(bets) #Convert string to list
    allowed = roulette_game.register_player_bets(name, bets)
    return JsonResponse({'allowed': allowed}, safe=False)

