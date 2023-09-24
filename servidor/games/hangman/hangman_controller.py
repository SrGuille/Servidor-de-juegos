import threading
from servidor import models
import json
from servidor import main_controller
#from googletrans import Translator
#from wonderwords import RandomSentence

sentence = ""
guessed_letters_pos = [] # Binary array of guessed letters
guessed_letters = [] # Array of guessed letters
round_player_guess_appearances = []
player_cumulative_appearances = []
player_guessed_letters = []
round_winner_players = []
step_fails_players = []
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
    #sentence = oraciones.get_random_sentence().lower().replace(".", "")
    sentence = "hola" # TODO use chatgpt to generate sentences
    print("Sentence: " + sentence)
    guessed_letters_pos = [0] * len(sentence) # Initialize the guessed letters array
    num_spaces_apperances = register_guessed_letter(" ") #Register spaces
    letters_to_guess = len(sentence) - num_spaces_apperances # Calculate the number of letters to guess
    coins_per_sentence_guess = (letters_to_guess * coins_per_guessed_letter) / 2 # Calculate the number of coins per sentence guess
    
    reset_variables() # Initialize the variables
    main_controller.get_players_lock().acquire()
    player_cumulative_appearances = [0] * len(main_controller.get_players()) # Cumulative apperances of the guess of each player in all the rounds
    main_controller.get_players_lock().release()

    print(get_censured_sentence())
    return get_censured_sentence()

# Initialize the guessed letters array
def reset_variables():
    global round_player_guess_appearances, player_guessed_letters, player_final_guesses, round_winner_players, step_fails_players
    main_controller.get_players_lock().acquire()
    players = main_controller.get_players()
    round_player_guess_appearances = [0] * len(players) # Apperances of the guess of each player in the round
    player_guessed_letters = [None] * len(players) # Last letter guessed by each player
    player_final_guesses = [None] * len(players) # Final guess of each player
    round_winner_players = [] # Winner players of the round
    step_fails_players = [] # Fails players of the round
    main_controller.reset_elements() # Empty the elements list of all players and recieve calls from clients
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
def register_player_guess(guess, player_name):
    valid_guess = False
    ready_to_play_game = main_controller.is_current_game_ready()
    if(ready_to_play_game):
        main_controller.get_players_lock().acquire()
        player = main_controller.get_player(player_name)
        if(player != None): 
            player_id = player.id
            guess = guess.lower()
            if(guess not in guessed_letters): # If the letter has not been guessed yet
                
                valid_guess = True
                player.elements.append(models.Guess(guess)) # Add the guess to the player elements
                if(len(guess) == len(sentence)): # If the guess is a sentence guess
                    
                    if(guess == sentence): # If the guess is correct
                        round_winner_players.append(player)
                        round_player_guess_appearances[player_id - 1] = 0
                    else:
                        step_fails_players.append(player)
                        round_player_guess_appearances[player_id - 1] = 0

                elif(len(guess) == 1): # If the guess is a letter guess
                    
                    player_guessed_letters[player_id - 1] = guess
                    num_apperances = sentence.count(guess)
                    round_player_guess_appearances[player_id - 1] = num_apperances
                    player_cumulative_appearances[player_id - 1] += num_apperances

                else:
                    valid_guess = False

        main_controller.get_players_lock().release()

    return valid_guess

def perform_step():
    global step

    partially_guessed_sentence = get_censured_sentence()
    round_winner_names = []
    hanged_candidates_names = []

    main_controller.get_players_lock().acquire()
 
    # If there are players with correct guesses, end
    if(len(round_winner_players) > 0): # If there are players with correct guesses, end
        update_round_winners_coins(round_winner_players)
        round_winner_names = get_player_names(round_winner_players)
    else:
        # If there are players with incorrect guesses
        if(len(step_fails_players) > 0):
            substract_coins_step_fails(step_fails_players)

        best_guess_apperances = max(round_player_guess_appearances)
        if(best_guess_apperances > 0):
            winner_guesses_and_players = search_guesses_and_players(round_player_guess_appearances, best_guess_apperances)
            update_step_winners_coins(winner_guesses_and_players)
            partially_guessed_sentence = get_censured_sentence()
        
        # Candidates to be hanged
        worst_cumulative_guess_apperances = min(player_cumulative_appearances)
        hanged_candidates = search_players(player_cumulative_appearances, worst_cumulative_guess_apperances)
        hanged_candidates_names = get_player_names(hanged_candidates)

        step += 1
        if(step >= round): # Lose condition
            round_winner_names = ["Loss"]
            substract_hanged_players_coins(hanged_candidates)


    main_controller.get_players_lock().release()
    
    return hanged_candidates_names, partially_guessed_sentence, round_winner_names


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

def search_players(apperances, number):
    all_players = main_controller.get_players()
    players = []
    for i in range(len(apperances)):
        if(apperances[i] == number):
            players.append(all_players[i])
    return players

def get_player_names(list_of_players):
    names = []
    for player in list_of_players:
        names.append(player.name)
    return names

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
def substract_hanged_players_coins(hanged_players):
    for player in hanged_players:
        player_id = player.id
        num_guessed_letters = player_cumulative_appearances[player_id]
        num_non_guessed_letters = letters_to_guess - num_guessed_letters
        player.coins -= round(coins_per_guessed_letter * num_non_guessed_letters)

def update_round_winners_coins(round_winner_players):
    for player in round_winner_players:
        player.coins += round(coins_per_sentence_guess / len(round_winner_players))

def substract_coins_step_fails(step_fails_players):
    for player in step_fails_players:
        player.coins -= round(loss_coins_per_wrong_guess / len(step_fails_players))
