from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import redirect
from . import roulette_controller, main_controller, hangman_controller

# Create your views here.

def hangman_host_render(request):
    return render(request, 'hangman_host.html')

def hangman_client_render(request):
    return render(request, 'hangman_client.html')

def send_player_guess(request):
    guess = request.GET.get('guess')
    hangman_controller.register_player_guess(guess)
    return JsonResponse({'status': 'ok'}, safe=False)

def get_best_guess(request):
    best_guess, partial_word = hangman_controller.get_best_guess()
    return JsonResponse({'best_guess': best_guess, 'partial_word': partial_word}, safe=False)

def get_hanged_players(request):
    hanged_players = hangman_controller.get_hanged_players()
    return JsonResponse({'hanged_players': hanged_players}, safe=False)