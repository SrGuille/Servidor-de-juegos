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

def perform_step(request):
    censured_sentence, hanged_candidates = hangman_controller.perform_step()
    return JsonResponse({'partial_word': censured_sentence, 
    'hanged_candidates': hanged_candidates}, safe=False)