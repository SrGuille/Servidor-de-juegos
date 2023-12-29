from django.shortcuts import render
from django.http import JsonResponse
from . import hangman_controller

# Create your views here.

def hangman_admin_render(request):
    return render(request, 'hangman/hangman_admin.html')

def hangman_player_render(request):
    return render(request, 'hangman/hangman_player.html')

def create_sentence(request):
    sentence, pot_per_sentence_guess = hangman_controller.create_sentence()
    return JsonResponse({'partially_guessed_sentence': sentence, 
    'pot_per_sentence_guess': pot_per_sentence_guess}, safe=False)

def send_player_guess(request):
    guess = request.GET.get('guess')
    player_name = request.GET.get('player_name')
    valid_guess, eliminated, winner = hangman_controller.register_player_guess(guess, player_name)
    return JsonResponse({'valid': valid_guess, 'eliminated': eliminated,
    'winner': winner}, safe=False)

def perform_step(request):
    partially_guessed_sentence, hang_step, game_winners, pot_per_sentence_guess = hangman_controller.perform_step()
    return JsonResponse({'partially_guessed_sentence': partially_guessed_sentence, 
    'hang_step': hang_step, 'game_winners': game_winners, 
    'pot_per_sentence_guess': pot_per_sentence_guess}, safe=False)
