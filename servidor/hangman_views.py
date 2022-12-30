from django.shortcuts import render
from django.http import JsonResponse
from . import hangman_controller

# Create your views here.

def hangman_host_render(request):
    return render(request, 'hangman_host.html')

def hangman_client_render(request):
    return render(request, 'hangman_client.html')

def create_sentence(request):
    sentence = hangman_controller.create_sentence()
    return JsonResponse({'partially_guessed_sentence': sentence}, safe=False)

def send_player_guess(request):
    guess = request.GET.get('guess')
    hangman_controller.register_player_guess(guess)
    return JsonResponse({'status': 'ok'}, safe=False)

def perform_step(request):
    hanged_candidates, partially_guessed_sentence, round_winner_players = hangman_controller.perform_step()
    return JsonResponse({'hanged_candidates': hanged_candidates, 
    'partially_guessed_sentence': partially_guessed_sentence, 
    'round_winner_players': round_winner_players}, safe=False)