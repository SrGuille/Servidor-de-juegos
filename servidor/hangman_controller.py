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
player_guessed_letters = []
player_final_guesses = []
coins_per_guess = 10
letters_to_guess = 0
round = 0
max_rounds = 5

# Use library to generate spanish random words
def create_sentence():
    global sentence, guessed_letters_pos, letters_to_guess
    translator = Translator() #defining the translator object
    sentence = RandomSentence() #defining the random sentence object
    translated_sentence = translator.translate(sentence, src='en', dest='es') #translating the sentence to spanish
    sentence = translated_sentence.text #getting the translated sentence
    
    guessed_letters_pos = [0] * len(sentence) # Initialize the guessed letters array
    num_apperances = register_guessed_letter(" ") #Register spaces

    letters_to_guess = sentence - num_apperances # Calculate the number of letters to guess

# Initialize the guessed letters array
def empty_variables():
    main_controller.get_players_lock().acquire()
    players = main_controller.get_players()
    round_player_guess_appearances = [0] * len(players) # Apperances of the guess of each player in the round
    player_cumulative_appearances = [0] * len(players) # Cumulative apperances of the guess of each player in all the rounds
    player_guessed_letters = [None] * len(players) # Last letter guessed by each player
    player_final_guesses = [None] * len(players) # Final guess of each player
    main_controller.get_players_lock().release()

# Register guessed letter positions in the binary array
def register_guessed_letter(letter):
    apperances = 0
    for i in range(len(sentence)):
        if(sentence[i] == letter):
            guessed_letters_pos[i] = 1
            apperances += 1

    return apperances

# Register player guessed letter and apperances only if it is the turn of the player
def register_player_guess(guess):
    valid_guess = False
    listen_client_calls = main_controller.get_listen_client_calls()
    if(listen_client_calls):
        valid_guess = True
        main_controller.get_players_lock().acquire()
        player = main_controller.get_player(guess['player_name'])
        if(player != None): 
            player_id = player.id
            guess = guess['letter'].lower()
            if(len(guess) == len(sentence)): # If the guess is a sentence guess
                if(guess == sentence): # If the guess is correct
                    player_final_guesses[player_id] = 'Correct'
                else:
                    player_final_guesses[player_id] = 'Incorrect'

            elif(len(guess) == 1): # If the guess is a letter guess
                player_guessed_letters[player_id - 1] = guess['letter']
                num_apperances = sentence.count(guess['letter'])
                round_player_guess_appearances[player_id - 1] = num_apperances
                player_cumulative_appearances[player_id - 1] += num_apperances

            else:
                valid_guess = False

        main_controller.get_players_lock().release()

    return valid_guess

# Gets the best guess and the players that have made it
def get_winners_and_losers():
    main_controller.get_players_lock().acquire()

    if('Correct' in player_final_guesses):
        winner_guesses_and_players = {'Correct': [main_controller.get_player_by_id(player_final_guesses.index('Correct'))]}
        main_controller.get_players_lock().release()
        return winner_guesses_and_players, None

    elif('Incorrect' in player_final_guesses):
        worst_guesses_and_players = {'Incorrect': [main_controller.get_player_by_id(player_final_guesses.index('Incorrect'))]}
        main_controller.get_players_lock().release()
        return None, worst_guesses_and_players

    best_guess_apperances = max(round_player_guess_appearances)
    winner_guesses_and_players = search_guesses_and_players(round_player_guess_appearances, best_guess_apperances)

    worst_guess_apperances = min(round_player_guess_appearances)
    worst_guesses_and_players = search_guesses_and_players(round_player_guess_appearances, worst_guess_apperances)

    main_controller.get_players_lock().release()
    return winner_guesses_and_players, worst_guesses_and_players


# For every guess with the number of apperances, get the players that have made it (needs the lock)
def search_guesses_and_players(apperances, number):
    all_players = main_controller.get_players()
    guesses_and_players = {}
    for i in range(len(apperances)):
        if(apperances[i] == number):
            guessed_letter = player_guessed_letters[i]
            if(guessed_letter not in guesses_and_players):
                guesses_and_players[guessed_letter] = [all_players[i]] # Add player to the list of players that have guessed that letter
            else:
                guesses_and_players[guessed_letter].append(all_players[i])
    return guesses_and_players

    
def update_winners_coins(winner_guesses_and_players):
    main_controller.get_players_lock().acquire()

    for guess in winner_guesses_and_players:
        apperances = register_guessed_letter(guess)
        coins_per_player = round(coins_per_guess * apperances)

        for player in winner_guesses_and_players[guess]:
            player.coins += coins_per_player

    main_controller.get_players_lock().release()


def update_hanged_players_coins():
    main_controller.get_players_lock().acquire()

    worse_cumulative_guess = min(player_cumulative_appearances)
    hanged_players = search_guesses_and_players(round_player_guess_appearances, worse_cumulative_guess)

    for guess in hanged_players:
        for player in hanged_players[guess]:
            player_id = player.id
            num_guessed_letters = player_cumulative_appearances[player_id]
            num_non_guessed_letters = letters_to_guess - num_guessed_letters
            player.coins -= round(coins_per_guess * num_non_guessed_letters)

    main_controller.get_players_lock().release()