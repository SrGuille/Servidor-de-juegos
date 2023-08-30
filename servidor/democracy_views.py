from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import redirect
from . import main_controller, democracy_controller

# Create your views here.

def democracy_admin_render(request):
    return render(request, 'democracy_admin.html')

def democracy_client_render(request):
    return render(request, 'democracy_client.html')

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
    colors_per_second = request.GET.get('colors_per_second')
    winner_msj = democracy_controller.send_colors_per_second(colors_per_second)
    return JsonResponse({'winner_msj': winner_msj}, safe=False)