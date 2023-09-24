from django.shortcuts import render
from django.http import JsonResponse
from . import hangman_controller

# Create your views here.

def hangman_admin_render(request):
    return render(request, 'hangman/hangman_admin.html')

def hangman_player_render(request):
    return render(request, 'hangman/hangman_player.html')

def create_sentence(request):
    sentence = hangman_controller.create_sentence()
    return JsonResponse({'partially_guessed_sentence': sentence}, safe=False)

def send_player_guess(request):
    guess = request.GET.get('guess')
    player_name = request.GET.get('player_name')
    hangman_controller.register_player_guess(guess, player_name)
    return JsonResponse({'status': 'ok'}, safe=False)

def perform_step(request):
    hanged_candidates, partially_guessed_sentence, round_winner_players = hangman_controller.perform_step()
    return JsonResponse({'hanged_candidates': hanged_candidates, 
    'partially_guessed_sentence': partially_guessed_sentence, 
    'round_winner_players': round_winner_players}, safe=False)