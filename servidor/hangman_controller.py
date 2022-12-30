import threading
from . import models
import json
from . import main_controller
#from googletrans import Translator
#from wonderwords import RandomSentence
from . import oraciones

sentence = ""
guessed_letters_pos = [] # Binary array of guessed letters
guessed_letters = [] # Array of guessed letters
round_player_guess_appearances = []
player_cumulative_appearances = []
player_guessed_letters = []
player_final_guesses = []
coins_per_guessed_letter = 10
coins_per_sentence_guess = 0
loss_coins_per_wrong_guess = 10
letters_to_guess = 0
step = 0
max_steps = 5

# Use library to generate spanish random words
def create_sentence():
    global sentence, guessed_letters_pos, letters_to_guess, coins_per_sentence_guess, player_cumulative_appearances
    #translator = Translator() #defining the translator object
    #sentence = RandomSentence() #defining the random sentence object
    #translated_sentence = translator.translate(sentence, src='en', dest='es') #translating the sentence to spanish
    #sentence = translated_sentence.text #getting the translated sentence
    sentence = oraciones.get_random_sentence().lower().replace(".", "")
    guessed_letters_pos = [0] * len(sentence) # Initialize the guessed letters array
    num_spaces_apperances = register_guessed_letter(" ") #Register spaces
    letters_to_guess = sentence - num_spaces_apperances # Calculate the number of letters to guess
    coins_per_sentence_guess = (letters_to_guess * coins_per_guessed_letter) / 2 # Calculate the number of coins per sentence guess
    
    reset_variables() # Initialize the variables
    main_controller.get_players_lock().acquire()
    player_cumulative_appearances = [0] * len(main_controller.get_players()) # Cumulative apperances of the guess of each player in all the rounds
    main_controller.get_players_lock().release()

# Initialize the guessed letters array
def reset_variables():
    global round_player_guess_appearances, player_cumulative_appearances, player_guessed_letters, player_final_guesses
    main_controller.get_players_lock().acquire()
    players = main_controller.get_players()
    round_player_guess_appearances = [0] * len(players) # Apperances of the guess of each player in the round
    player_guessed_letters = [None] * len(players) # Last letter guessed by each player
    player_final_guesses = [None] * len(players) # Final guess of each player
    main_controller.reset_elements() # Empty the elements list of all players
    main_controller.get_players_lock().release()

# Register guessed letter positions in the binary array
def register_guessed_letter(letter):
    apperances = 0
    for i in range(len(sentence)):
        if(sentence[i] == letter):
            guessed_letters_pos[i] = 1
            guessed_letters.append(letter)
            apperances += 1

    return apperances

# Get the sentence with _ instead of the letters that have not been guessed yet
def get_censured_sentence():
    censured_sentence = ""
    for i in range(len(sentence)):
        if(guessed_letters_pos[i] == 1):
            censured_sentence += sentence[i]
        else:
            censured_sentence += "_"

    return censured_sentence

# Register player guessed letter and apperances only if it is the turn of the player
def register_player_guess(guess):
    valid_guess = False
    listen_client_calls = main_controller.get_listen_client_calls()
    if(listen_client_calls):
        
        main_controller.get_players_lock().acquire()
        player = main_controller.get_player(guess['player_name'])
        if(player != None): 
            
            player_id = player.id
            guess = guess['letter'].lower()
            if(guess not in guessed_letters): # If the letter has not been guessed yet
                
                valid_guess = True
                player.elements.append(models.Guess(guess)) # Add the guess to the player elements
                if(len(guess) == len(sentence)): # If the guess is a sentence guess
                    
                    if(guess == sentence): # If the guess is correct
                        player_final_guesses[player_id - 1] = 'Correct'
                        round_player_guess_appearances[player_id - 1] = 0
                    else:
                        player_final_guesses[player_id - 1] = 'Incorrect'
                        round_player_guess_appearances[player_id - 1] = 0

                elif(len(guess) == 1): # If the guess is a letter guess
                    
                    player_guessed_letters[player_id - 1] = guess['letter']
                    num_apperances = sentence.count(guess['letter'])
                    round_player_guess_appearances[player_id - 1] = num_apperances
                    player_cumulative_appearances[player_id - 1] += num_apperances

                else:
                    valid_guess = False

        main_controller.get_players_lock().release()

    return valid_guess

def perform_step():
    global step

    main_controller.get_players_lock().acquire()
    players = main_controller.get_players()
    correct_guesses_and_players, incorrect_guesses_and_players, winner_guesses_and_players, hanged_guesses_and_candidates = get_winners_and_losers()
    hanged_candidates = []

    if(len(incorrect_guesses_and_players) > 0):
        substract_coins_step_fails(incorrect_guesses_and_players)

    if(len(winner_guesses_and_players) > 0):
        update_step_winners_coins(winner_guesses_and_players)

    if(len(hanged_guesses_and_candidates) > 0):
        for guess in hanged_guesses_and_candidates:
            for player in guess:
                hanged_candidates.append(player.player_name)

    if(len(correct_guesses_and_players) > 0): # If there are players with correct guesses, end
        update_round_winners_coins(correct_guesses_and_players)
    
    step += 1
    if(round > step):
        return False

    return True

# Gets the best guess and the players that have made it
def get_winners_and_losers():
    main_controller.get_players_lock().acquire()
    correct_guesses_and_players = {}
    incorrect_guesses_and_players = {}

    if('Correct' in player_final_guesses):
        correct_guesses_and_players = search_guesses_and_players(player_final_guesses, 'Correct')

    elif('Incorrect' in player_final_guesses):
        incorrect_guesses_and_players = search_guesses_and_players(player_final_guesses, 'Incorrect')

    best_guess_apperances = max(round_player_guess_appearances)
    winner_guesses_and_players = search_guesses_and_players(round_player_guess_appearances, best_guess_apperances)

    worst_cumulative_guess_apperances = min(player_cumulative_appearances)
    hanged_candidates = search_guesses_and_players(player_cumulative_appearances, worst_cumulative_guess_apperances)

    main_controller.get_players_lock().release()
    return correct_guesses_and_players, incorrect_guesses_and_players, winner_guesses_and_players, hanged_candidates

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

# Update the coins of the players that have guessed some letters correctly    
def update_step_winners_coins(winner_guesses_and_players):
    main_controller.get_players_lock().acquire()

    for guess in winner_guesses_and_players:
        apperances = register_guessed_letter(guess)
        total_coins_prize = coins_per_guessed_letter * apperances

        # Give the proportional part of the coins to each player
        for player in winner_guesses_and_players[guess]:
            player.coins += round(total_coins_prize / len(winner_guesses_and_players[guess])) # Add coins to the player

    main_controller.get_players_lock().release()

# Update the coins of the players that have been hanged
def update_hanged_players_coins():
    main_controller.get_players_lock().acquire()

    worse_cumulative_guess = min(player_cumulative_appearances)
    hanged_players = search_guesses_and_players(round_player_guess_appearances, worse_cumulative_guess)

    for guess in hanged_players:
        for player in hanged_players[guess]:
            player_id = player.id
            num_guessed_letters = player_cumulative_appearances[player_id]
            num_non_guessed_letters = letters_to_guess - num_guessed_letters
            player.coins -= round(coins_per_guessed_letter * num_non_guessed_letters)

    main_controller.get_players_lock().release()

def update_round_winners_coins(correct_guesses_and_players):
    main_controller.get_players_lock().acquire()
    for guess in correct_guesses_and_players:
        for player in correct_guesses_and_players[guess]:
            player.coins += round(coins_per_sentence_guess / len(correct_guesses_and_players[guess]))
    main_controller.get_players_lock().release()

def substract_coins_step_fails(incorrect_guesses_and_players):
    main_controller.get_players_lock().acquire()
    for guess in incorrect_guesses_and_players:
        for player in incorrect_guesses_and_players[guess]:
            player.coins -= round(loss_coins_per_wrong_guess / len(incorrect_guesses_and_players[guess]))
    main_controller.get_players_lock().release()
