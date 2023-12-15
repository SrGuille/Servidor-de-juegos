from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import redirect
from . import main_controller

def login_render(request):
    return render(request, 'login.html')

def game_selector_render(request):
    return render(request, 'game_selector.html')

def ranking_and_prizes_render(request):
    return render(request, 'ranking_and_prizes.html')

def wait_room_render(request):
    return render(request, 'wait_room.html')

def set_game(request):
    game_id = int(request.GET.get('game'))
    rounds = int(request.GET.get('rounds'))
    main_controller.set_game(game_id, rounds)
    return JsonResponse({'status': 'ok'}, safe=False)

def transition_to_next_game(request):
    game_id = main_controller.transition_to_next_game()
    return JsonResponse({'game_id': game_id}, safe=False)

def get_ready_to_join_game(request):
    game_id = main_controller.get_ready_to_join_game()
    return JsonResponse({'game_id': game_id}, safe=False)

def set_can_players_join(request):
    can_join = bool(request.GET.get('can_join'))
    main_controller.set_can_players_join(can_join)
    return JsonResponse({'status': 'ok'}, safe=False)

def set_can_players_interact(request):
    can_interact = bool(request.GET.get('can_interact'))
    main_controller.set_can_players_interact(can_interact)
    return JsonResponse({'status': 'ok'}, safe=False)

 
def login_player(request):
    """
        New player is loged and redirected to the current game client screen
    """
    name = request.GET.get('name')
    nick = request.GET.get('nick')
    print(name)
    if(name == ''):
        return JsonResponse({'status': 'error'}, safe=False)
    
    elif(nick == 'admin'): #TODO Set up the whole DS and redirect to game selector
        main_controller.game_setup()
        return redirect('game_selector_render')
    
    else: #Register player (if necessary) and redirect to the wait room
        nick = request.GET.get('nick')
        if(nick == ''): # If the player has not set a nick, use the name
            nick = name
        main_controller.login_player(name, nick)
        return redirect('wait_room_render')
    
def get_players_names(request):
    players_names = main_controller.get_players_names()
    return JsonResponse({'names': players_names}, safe=False)
        
def logout(request):
    name = request.GET.get('name')
    main_controller.logout(name)
    return JsonResponse({'status': 'ok'}, safe=False)

def get_number_players(request):
    number_players = main_controller.get_number_players()
    return JsonResponse({'players': number_players}, safe=False)

def get_player_coins(request):
    name = request.GET.get('player_name')
    coins = main_controller.get_player_coins(name)
    return JsonResponse({'player_coins': coins}, safe=False)

def get_players_scores(request):
    ranking = main_controller.get_players_scores()
    return JsonResponse(ranking, safe=False)

def get_available_prizes(request):
    prizes = main_controller.get_available_prizes()
    return JsonResponse(prizes, safe=False)

def create_roulettes(request):
    main_controller.create_players_roulette()
    main_controller.create_prizes_roulette()
    return JsonResponse({'status': 'ok'}, safe=False)

def send_prize_to_winner(request):
    winner = request.GET.get('winner')
    prize = request.GET.get('prize')
    main_controller.register_prize_winner(winner, prize)
    return JsonResponse({'status': 'ok'}, safe=False)