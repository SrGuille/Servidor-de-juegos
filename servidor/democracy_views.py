from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import redirect
from . import main_controller, democracy_controller

# Create your views here.

def democracy_host_render(request):
    return render(request, 'democracy_host.html')

def democracy_client_render(request):
    return render(request, 'democracy_client.html')

def send_player_move(request):
    player_name = request.GET.get('player_name')
    move = request.GET.get('move')
    democracy_controller.register_player_move(player_name, move)
    return JsonResponse({'status': 'ok'}, safe=False)

def compute_democracy_move(request):
    vertical_force, horizontal_force = democracy_controller.compute_democracy_move()
    return JsonResponse({'vertical_force': vertical_force, 'horizontal_force': horizontal_force}, safe=False)