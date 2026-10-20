from django.shortcuts import render
from django.http import JsonResponse
from . import palabrazo_controller

palabrazo_game = palabrazo_controller.PalabrazoGame()

# Create your views here.

def palabrazo_admin_render(request):
    return render(request, 'palabrazo/palabrazo_admin.html')

def palabrazo_player_render(request):
    return render(request, 'palabrazo/palabrazo_player.html')

def setup_palabrazo(request):
    partially_guessed_sentence, current_jackpot, num_pending_letters = palabrazo_game.setup_palabrazo()
    return JsonResponse({'partially_guessed_sentence': partially_guessed_sentence, 
    'current_jackpot': current_jackpot, 'num_pending_letters': num_pending_letters}, safe=False)

def send_player_guess(request):
    player_name = request.GET.get('player_name')
    guessed_word = request.GET.get('guessed_word')
    valid_guess = palabrazo_game.register_player_guess(player_name, guessed_word)
    return JsonResponse({'valid': valid_guess}, safe=False)

def get_palabrazo_data(request):
    partially_guessed_sentence, current_jackpot, num_pending_letters = palabrazo_game.get_palabrazo_data()
    return JsonResponse({'partially_guessed_sentence': partially_guessed_sentence, 
                         'current_jackpot': current_jackpot, 'num_pending_letters': num_pending_letters}, safe=False)

def reveal_letter(request):
    partially_guessed_sentence, current_jackpot, num_pending_letters = palabrazo_game.reveal_letter()
    return JsonResponse({'partially_guessed_sentence': partially_guessed_sentence, 
                         'current_jackpot': current_jackpot, 'num_pending_letters': num_pending_letters}, safe=False)

def finish_palabrazo(request):
    winner_msj = palabrazo_game.finish_palabrazo()
    return JsonResponse({'winner_msj': winner_msj}, safe=False)

def has_finished_palabrazo(request):
    has_finished = palabrazo_game.has_finished()
    return JsonResponse({'has_finished': has_finished}, safe=False)