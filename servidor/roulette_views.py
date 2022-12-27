from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import redirect
from . import roulette_controller, main_controller

# Create your views here.

def roulette_host_render(request):
    return render(request, 'roulette_host.html')

def roulette_client_render(request):
    return render(request, 'roulette_client.html')

def send_roulette_result(request):
    result = request.GET.get('result')
    print(result)
    roulette_controller.assign_prizes(result)
    main_controller.reset_elements()
    return JsonResponse({'status': 'ok'}, safe=False)

def send_player_bets(request):
    global number_bets
    json_str = request.GET.get('bets')
    roulette_controller.register_player_bets(json_str)
    return JsonResponse({'status': 'ok'}, safe=False)

