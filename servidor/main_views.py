from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import redirect
from . import main_controller

client_redirects = ['roulette_client_render', 'hangman_client_render', 'democracy_client_render', 'multibandits_client_render']

def login_render(request):
    return render(request, 'login.html')

def game_selector_render(request):
    return render(request, 'game_selector.html')

def ranking_render(request):
    return render(request, 'ranking.html')

def set_game(request):
    game_id = int(request.GET.get('game'))
    rounds = int(request.GET.get('rounds'))
    main_controller.set_game(game_id, rounds)
    return JsonResponse({'status': 'ok'}, safe=False)

def get_next_game(request):
    game_id = main_controller.get_next_game()
    return JsonResponse({'game': game_id}, safe=False)

# New player is registered and redirected to the active game client screen
def register_player(request):
    name = request.GET.get('name')
    print(name)
    if(name == ''):
        return JsonResponse({'status': 'error'}, safe=False)
    elif(name == 'admin'): #Set up the whole DS and redirect to game selector
        main_controller.game_setup()
        return redirect('game_selector_render')
    else: #Register player (if necessary) and redirect to the first game client
        main_controller.register_player(name)
        active_game_id = main_controller.get_active_game()
        return redirect(client_redirects[active_game_id])

def get_number_players(request):
    pass
    number_players = main_controller.get_number_players()
    return JsonResponse({'players': number_players}, safe=False)

def get_player_coins(request):
    name = request.GET.get('player_name')
    coins = main_controller.get_player_coins(name)
    return JsonResponse({'player_coins': coins}, safe=False)

def get_remaining_interactions(request):
    remaining_bets = main_controller.get_remaining_interactions()
    return JsonResponse({'remaining_interactions': remaining_bets}, safe=False)

def get_players_scores(request):
    ranking = main_controller.get_players_scores()
    return JsonResponse(ranking, safe=False)

def dont_listen_client_calls(request):
    main_controller.set_listen_client_calls(False)
    return JsonResponse({'status': 'ok'}, safe=False)

def get_available_prizes(request):
    prizes = main_controller.get_available_prizes()
    return JsonResponse(prizes, safe=False)

def create_roulettes(request):
    main_controller.create_players_roulette()
    main_controller.create_prizes_roulette()
    return JsonResponse({'status': 'ok'}, safe=False)

def send_prize_winner(request):
    winner = request.GET.get('winner')
    prize = request.GET.get('prize')
    main_controller.register_prize_winner(winner, prize)
    return JsonResponse({'status': 'ok'}, safe=False)