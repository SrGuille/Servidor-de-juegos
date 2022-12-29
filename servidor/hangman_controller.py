import threading
from . import models
import json
from . import main_controller
from googletrans import Translator
from wonderwords import RandomSentence

sentence = ""
guessed_letters_pos = [] # Binary array of guessed letters
round_player_guess_appearances = [] 
player_cumulative_appearances = []
round = 0
max_rounds = 5

# Use library to generate spanish random words
def create_sentence():
    translator = Translator() #defining the translator object
    sentence = RandomSentence() #defining the random sentence object
    translated_sentence = translator.translate(sentence, src='en', dest='es') #translating the sentence to spanish
    sentence = translated_sentence.text #getting the translated sentence
    
    guessed_letters_pos = [0] * len(sentence) # Initialize the guessed letters array
    register_guessed_letter(" ") #Register spaces

# Initialize the guessed letters array
def empty_players_guess():
    main_controller.get_players_lock().acquire()
    players = main_controller.get_players()
    for player in players:
        player.elements = [None]
    main_controller.get_players_lock().release()

# Register guessed letter positions in the binary array
def register_guessed_letter(letter):
    for i in range(len(sentence)):
        if(sentence[i] == letter):
            guessed_letters_pos[i] = 1

# Register player guessed letter and apperances only if it is the turn of the player
def register_player_guess(guess):
    listen_client_calls = main_controller.get_listen_client_calls()
    if(listen_client_calls):
        main_controller.get_players_lock().acquire()
        player = main_controller.get_player(guess['player_name'])
        if(player != None): 
            num_apperances = sentence.count(guess['letter'])
            player.elements[0] = models.Guess(guess['letter'], num_apperances) #Add guess to player
        main_controller.get_players_lock().release()
"""
# Gets the best guess and the players that have made it
def get_best_guess():
    main_controller.get_players_lock().acquire()
    players = main_controller.get_players()
    apperances = []
    for player in players:
        number_appearances = player.elements[0].appearances
        apperances.append(number_appearances)

    best_guess_apperances = max(apperances)
    winners = search_players_and_guess(apperances, best_guess_apperances)

    worst_guess_apperances = min(apperances)
    losers = search_players_and_guess(apperances, worst_guess_apperances)

    main_controller.get_players_lock().release()
    return best_guess, winners
"""
"""
# Gets the players that have made the guess with that number of apperances
def search_players_and_guess(apperances, number):
    main_controller.get_players_lock().acquire()
    all_players = main_controller.get_players()
    searched_players = []
    for i in range(len(apperances)):
        if(apperances[i] == number):
            winners.append(players[i])
    main_controller.get_players_lock().release()
    return winners
"""
"""
def get_hanged_players():
    main_controller.get_players_lock().acquire()
    players = main_controller.get_players()
    apperances = []
    for player in players:
        if(player.elements[0] != None):
            number_appearances = player.elements[0].appearances
            apperances.append(number_appearances)

    best_guess = max(apperances)
    winners = get_winners(apperances, best_guess)

    main_controller.get_players_lock().release()
    return best_guess, winners
"""