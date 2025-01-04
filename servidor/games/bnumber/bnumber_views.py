from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import redirect
from . import bnumber_controller
import json

bnumber_game = bnumber_controller.BNumberGame()

# Create your views here.

def bnumber_admin_render(request):
    return render(request, 'bnumber/bnumber_admin.html')

def bnumber_player_render(request):
    return render(request, 'bnumber/bnumber_player.html')

def create_teams_bnumber(request):
    new_number_green, new_number_red = bnumber_game.create_teams()
    return JsonResponse({'new_number_green': new_number_green, 'new_number_red': new_number_red}, safe=False)

def get_my_team_bnumber(request):
    player_name = request.GET.get('player_name')
    team, leader, first_number = bnumber_game.get_my_team(player_name)
    print(team, leader)
    return JsonResponse({'team': team, 'leader': leader, 'first_number': first_number}, safe=False)

def send_position(request):
    player_name = request.GET.get('player_name')
    position = int(request.GET.get('position'))
    new_number, is_impossible = bnumber_game.register_position(player_name, position)
    return JsonResponse({'new_number': new_number, 'is_impossible': is_impossible}, safe=False)

def get_bnumber_data(request):
    teams_positions, teams_new_number = bnumber_game.get_bnumber_data()
    return JsonResponse({'teams_positions': teams_positions, 'teams_new_number': teams_new_number}, safe=False)

def finish_bnumber(request):
    winner_msj = bnumber_game.finish_bnumber()
    return JsonResponse({'winner_msj': winner_msj}, safe=False)