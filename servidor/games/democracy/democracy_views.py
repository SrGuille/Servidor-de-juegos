from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import redirect
from . import democracy_controller
import json

# Create your views here.

def democracy_admin_render(request):
    return render(request, 'democracy/democracy_admin.html')

def democracy_player_render(request):
    return render(request, 'democracy/democracy_player.html')

def create_teams(request):
    teams = democracy_controller.create_teams()
    return JsonResponse({'teams': teams}, safe=False)

def send_player_move(request):
    player_name = request.GET.get('player_name')
    move = request.GET.get('move')
    democracy_controller.register_player_move(player_name, move)
    return JsonResponse({'status': 'ok'}, safe=False)

def get_democratic_move(request):
    vertical_force, horizontal_force = democracy_controller.get_democratic_move()
    return JsonResponse({'vertical_force': vertical_force, 'horizontal_force': horizontal_force}, safe=False)

def get_my_team(request):
    player_name = request.GET.get('player_name')
    team = democracy_controller.get_my_team(player_name)
    return JsonResponse({'team': team}, safe=False)

def send_colors_per_second(request):
    winner_per_step = request.GET.get('colors_per_second')
    winner_per_step = json.loads(winner_per_step)
    winner_msj = democracy_controller.decide_winner_and_give_prizes(winner_per_step)
    return JsonResponse({'winner_msj': winner_msj}, safe=False)