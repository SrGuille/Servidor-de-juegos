from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import redirect
from . import controller

# Create your views here.

def index(request):
    return render(request, 'index.html')

# New player is registered and redirected to roulette_bet
def register_player(request):
    name = request.GET.get('name')
    controller.register_player(name)
    return redirect('roulette_bet')

def get_number_players(request):
    global number_players
    return JsonResponse({'players': number_players}, safe=False)

def get_player_coins(request):
    name = request.GET.get('player_name')
    coins = controller.get_player_coins(name)
    return JsonResponse({'player_coins': coins}, safe=False)

def get_remaining_bets(request):
    remaining_bets = controller.get_remaining_bets()
    return JsonResponse({'remaining_bets': remaining_bets}, safe=False)

def roulette(request):
    return render(request, 'roulette.html')

def send_roulette_result(request):
    result = request.GET.get('result')
    print(result)
    controller.assign_prizes(result)
    controller.reset_bets()
    return JsonResponse({'status': 'ok'}, safe=False)

def ranking(request):
    return render(request, 'ranking.html')

def roulette_bet(request):
    return render(request, 'roulette_bet.html')

def send_bets(request):
    global number_bets
    json_str = request.GET.get('bets')
    controller.register_player_bets(json_str)
    return JsonResponse({'status': 'ok'}, safe=False)

def get_ranking(request):
    ranking = controller.get_ranking()
    return JsonResponse(ranking, safe=False)

def get_pie_chart(request):
    ranking = controller.get_pie_chart()
    return JsonResponse({'status': 'ok'}, safe=False)

