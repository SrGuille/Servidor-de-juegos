from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import redirect
from . import gunman_controller

gunman_game = gunman_controller.GunmanGame()


def gunman_admin_render(request):
    return render(request, 'gunman/gunman_admin.html')

def gunman_player_render(request):
    return render(request, 'gunman/gunman_player.html')

def create_initial_duel(request):
    """
        Selects 2 random players from the list of players and returns their names
    """
    # Select 2 random players from the list of players
    duel_players = gunman_game.create_initial_duel()
    print(duel_players)
    return JsonResponse({'duel_players': duel_players}, safe=False)

def create_special_duel(request): 
    player1 = request.GET.get('player1')
    player2 = request.GET.get('player2')
    duel_players = gunman_game.create_special_duel(player1, player2)
    return JsonResponse({'duel_players': duel_players}, safe=False)

def get_duel_data(request):
    name = request.GET.get('name')
    player_data, is_special_duel = gunman_game.get_duel_data(name)
    return JsonResponse({'player_data': player_data, 'is_special_duel': is_special_duel}, safe=False)

def send_player_action(request):
    name = request.GET.get('name')
    action = request.GET.get('action') #Shoot, shield, reload
    allowed = gunman_game.register_player_action(name, action)
    return JsonResponse({'allowed': allowed}, safe=False)

def duel_step(request):
    current_duel_players, next_duel_new_players = gunman_game.duel_step()
    return JsonResponse({'current_duel_players': current_duel_players, 'next_duel_new_players': next_duel_new_players}, safe=False)

def special_duel_step(request):
    duel_players = gunman_game.special_duel_step()
    return JsonResponse({'duel_players': duel_players}, safe=False)

