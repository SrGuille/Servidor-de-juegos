from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import redirect
from . import main_controller

redirects = ['roulette_client_render', 'hangman_client_render', 'democracy_client_render', 'multibandits_client_render']

def index_render(request):
    return render(request, 'index.html')

def game_selector_render(request):
    return render(request, 'game_selector.html')

def ranking_render(request):
    return render(request, 'ranking.html')

def set_game(request):
    game = request.GET.get('game')
    rounds = request.GET.get('rounds')
    main_controller.set_game(game, rounds)
    return JsonResponse({'status': 'ok'}, safe=False)

def get_active_game(request):
    game = main_controller.get_active_game()
    return JsonResponse({'game': game}, safe=False)

# New player is registered and redirected to roulette_bet
def register_player(request):
    name = request.GET.get('name')
    main_controller.register_player(name)
    active_game_id = main_controller.get_active_game()
    return redirect(redirects[active_game_id])

def get_number_players(request):
    global number_players
    return JsonResponse({'players': number_players}, safe=False)

def get_player_coins(request):
    name = request.GET.get('player_name')
    coins = main_controller.get_player_coins(name)
    return JsonResponse({'player_coins': coins}, safe=False)

def get_ranking(request):
    ranking = main_controller.get_ranking()
    return JsonResponse(ranking, safe=False)

def get_pie_chart(request):
    ranking = main_controller.get_pie_chart()
    return JsonResponse({'status': 'ok'}, safe=False)