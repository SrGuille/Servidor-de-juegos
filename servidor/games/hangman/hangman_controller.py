from servidor.classes import Actor, HangmanPlayer, Guess
from typing import List, Tuple
from servidor import main_controller, main_views
from . import use_openai_api as oai_api
from servidor import queries as q
import random
import math

original_sentence = ""
without_tildes_sentence = "" # Sentence without tildes

logged_players_names = []
revealed_letters_pos = [] # Binary array of guessed letters
revealed_letters = [] # Array of guessed letters

hangman_players = {} # Dictionary of name: HangmanPlayer
step_correct_guesses = {} # Dictionary of letter: [Guess]
num_step_wrong_guesses = 0
game_winners = []
eliminated_players = [] 

COINS_PER_GUESSED_LETTER = 5
pot_per_sentence_guess = 105 # Initial pot
COINS_POT_DECREASE_PER_STEP = 5
LOSS_COINS_PER_SENTENCE_WRONG_GUESS = 20
MAX_WRONG_GUESSES_PER_ROUND = 0 # Initialized in the init function
LOSS_COINS_PER_HANG_WRONG_GUESS = 5

letters_to_guess = 0
hang_step = 0
MAX_HANG_STEPS = 5
ALPHABET = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 
            'j', 'k', 'l', 'm', 'n', 'ñ', 'o', 'p', 'q', 
            'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

def get_sentence_params() -> Tuple[List[Actor], str]:
    """
        Returns a list of 1 or 2 random actors (name and random attribute) and a repeated letter (or None)
    """
    num_actors = random.randint(1, 2)
    use_repeated_letter = random.randint(0, 1)
    repeated_letter = None
    if(use_repeated_letter == 1):
        repeated_letter = random.choice(ALPHABET)
    
    # Choose num_actors players randomly
    random_actors = random.sample(logged_players_names, num_actors)
    actors = []
    for actor in random_actors: # Get one attribute of each actor
        all_attributes = q.get_player_attributes(actor).split(',')
        attribute = random.choice(all_attributes) # choose 1 attribute randomly
        actor = Actor(actor, attribute)
        actors.append(actor)

    return actors, repeated_letter

def parse_sentence_to_without_tildes(sentence: str) -> str:
    """
        Remove the tildes from the sentence and convert it to lowercase
    """
    without_tildes_sentence = sentence.lower().replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').replace('ü', 'u')
    return without_tildes_sentence
    
# Use library to generate spanish random words
def create_sentence() -> str:
    global original_sentence, without_tildes_sentence, logged_players_names, revealed_letters_pos, letters_to_guess
    
    logged_players_names = q.get_logged_players_names()    
    actors, repeated_letter = get_sentence_params()
    prompt = oai_api.generate_prompt(actors, repeated_letter)
    original_sentence = oai_api.generate_sentence(prompt)
    #original_sentence = "En un arranque de gula, Toña ganó un guante dorado robándole los gusanos a un galgo"
    without_tildes_sentence = parse_sentence_to_without_tildes(original_sentence)

    revealed_letters_pos = [0] * len(original_sentence) # Initialize the guessed letters array
    num_spaces_apperances = reveal_guessed_letter(" ") #Register spaces
    num_commas_apperances = reveal_guessed_letter(",") #Register commas
    #letters_to_guess = len(sentence) - num_spaces_apperances - num_commas_apperances # Calculate the number of letters to guess
    #COINS_PER_SENTENCE_GUESS = (letters_to_guess * COINS_PER_GUESSED_LETTER) / 2 # Calculate the number of coins per sentence guess
    
    initialize_variables() # Initialize the global variables
    
    print(get_censured_sentence())
    return get_censured_sentence(), pot_per_sentence_guess

def initialize_variables():
    global logged_players_names, hangman_players, MAX_WRONG_GUESSES_PER_ROUND, pot_per_sentence_guess, game_winners, eliminated_players, revealed_letters, step_correct_guesses, num_step_wrong_guesses, hang_step
    
    hangman_players = {} # Dictionary of name: HangmanPlayer
    logged_players_names = q.get_logged_players_names()
    for player_name in logged_players_names:
        hangman_players[player_name] = HangmanPlayer()
    pot_per_sentence_guess = 80 # Initial pot
    
    logged_players_names = []
    revealed_letters = [] # Array of guessed letters

    game_winners = []
    eliminated_players = [] 
    hang_step = 0
    MAX_WRONG_GUESSES_PER_ROUND = math.floor(len(logged_players_names) / 4)

    reset_step_variables() # Initialize the step variables

# Initialize the guessed letters array
def reset_step_variables():
    """
        All the needed variables to start a new step are initialized
    """
    global step_correct_guesses, num_step_wrong_guesses, pot_per_sentence_guess
    step_correct_guesses = {} # Dictionary of letter: [Guess]
    num_step_wrong_guesses = 0
    main_views.main_controller_.reset_elements() # Empty the elements list of all players
    pot_per_sentence_guess -= COINS_POT_DECREASE_PER_STEP # Decrease the pot

# Register guessed letter positions in the binary array
def reveal_guessed_letter(letter):
    apperances = 0
    for i in range(len(without_tildes_sentence)):
        if(without_tildes_sentence[i] == letter):
            revealed_letters_pos[i] = 1
            revealed_letters.append(letter)
            apperances += 1

    return apperances

# Get the sentence with '_' instead of the letters that have not been guessed yet
def get_censured_sentence():
    censured_sentence = ""
    for i in range(len(original_sentence)):
        if(revealed_letters_pos[i] == 1):
            censured_sentence += original_sentence[i]
        else:
            censured_sentence += "_"

    return censured_sentence

def register_player_guess(guess: str, name: str) -> bool:
    """
        Register the player guess if it is valid (letter guess or sentence guess)
        and if the player is allowed to guess (not eliminated) TODO
    """
    global num_step_wrong_guesses, game_winners, eliminated_players
    valid_guess = False
    eliminated = False
    winner = False
    if(main_views.main_controller_.get_can_players_interact()):
        main_views.main_controller_.get_players_lock().acquire()
        player_guesses = main_views.main_controller_.get_player_elems(name)
        if(player_guesses != None): # If player exists in memory
            guess = parse_sentence_to_without_tildes(guess) # Remove tildes and convert to lowercase
            if(len(guess) == len(without_tildes_sentence)): # If the guess is a sentence guess
                valid_guess = True
                player_guesses.append(guess) # Add guess to player
                if(guess == without_tildes_sentence): # If the guess is correct
                    winner = True
                    game_winners.append(name) # Earnings will be updated in the perform_step function
                else: # Eliminate the player from the game
                    eliminated = True
                    eliminated_players.append(name)
                    hangman_players[name].earnings -= LOSS_COINS_PER_SENTENCE_WRONG_GUESS

            # If the guess is a valid letter guess (not revealed yet and in the alphabet)
            elif(len(guess) == 1 and guess not in revealed_letters and guess in ALPHABET): 
                valid_guess = True
                player_guesses.append(guess) # Add guess to player
                hangman_player = hangman_players[name]
                num_apperances = without_tildes_sentence.count(guess)

                if num_apperances == 0:
                    hangman_player.num_wrong_guesses += 1
                    num_step_wrong_guesses += 1
                else:
                    if(guess in step_correct_guesses): # Add player to the list of players that have guessed that letter
                        step_correct_guesses[guess].players.append(name)
                    else:
                        step_correct_guesses[guess] = Guess(num_apperances, name)

        main_views.main_controller_.get_players_lock().release()

    return valid_guess, eliminated, winner

def get_best_guess_and_players():
    """
        Returns the best guesses, the number of apperances and the players that have guessed them
    """
    best_guesses_and_players = {} # Dictionary of letter: [players]
    best_guess_apperances = 0
    for guessed_letter in step_correct_guesses: # Dictionary of letter: Guess
        guess_appereances = step_correct_guesses[guessed_letter].num_appereances
        if(guess_appereances > best_guess_apperances): # Found the best of all
            best_guess_apperances = guess_appereances
            best_guesses_and_players.clear() # Delete all past best guesses
            best_guesses_and_players[guessed_letter] = step_correct_guesses[guessed_letter].players
        elif(guess_appereances == best_guess_apperances): # Add new best guess (equal quality)
            if guessed_letter not in best_guesses_and_players:
                best_guesses_and_players[guessed_letter] = []
            else:
                best_guesses_and_players[guessed_letter].append(step_correct_guesses[guessed_letter].players)

    return best_guesses_and_players, best_guess_apperances


def perform_step():
    global hang_step, game_winners, num_step_wrong_guesses, pot_per_sentence_guess
    game_end = False
    main_views.main_controller_.get_players_lock().acquire()
 
    # If there are players with correct guesses, end
    if(len(game_winners) > 0): # If there are players with correct guesses, end
        update_game_winners_coins(game_winners)
        partially_guessed_sentence = original_sentence # Reveal sentence
        game_end = True
    else:
        best_guesses_and_players, best_guess_apperances = get_best_guess_and_players()
        step_winners(best_guesses_and_players, best_guess_apperances) # Reveal best letters and assign earnings
        partially_guessed_sentence = get_censured_sentence()
        
        if num_step_wrong_guesses > MAX_WRONG_GUESSES_PER_ROUND: # Advance to the next hang step
            hang_step += 1
        if(hang_step > MAX_HANG_STEPS): # Loss condition
            game_winners = ["Loss"]
            substract_wrong_guesses_coins()
            game_end = True

    for player in hangman_players:
        print(f"{player}: {hangman_players[player].earnings}")
        print(f"{player}: {hangman_players[player].num_wrong_guesses}")

    if game_end:
        earnings_to_coins()
    
    reset_step_variables()
    main_views.main_controller_.get_players_lock().release()
    
    return partially_guessed_sentence, hang_step, game_winners, pot_per_sentence_guess

def earnings_to_coins():
    """
        Convert the earnings of the players to coins in DB
    """
    for player_name in hangman_players:
        q.add_coins_to_player(player_name, hangman_players[player_name].earnings)

def step_winners(winner_guesses_and_players, num_apperances):
    """
        Register the best letters and accumulate the earnings of the players that have guessed them
    """
    for guessed_letter in winner_guesses_and_players:
        reveal_guessed_letter(guessed_letter) # Reveal letters
        total_coins_prize = COINS_PER_GUESSED_LETTER * num_apperances
        winners = winner_guesses_and_players[guessed_letter]
        # Give the proportional part of the coins to each player
        for winner in winner_guesses_and_players[guessed_letter]:
            earnings = math.ceil(total_coins_prize / len(winners))
            hangman_players[winner].earnings += earnings # Accumulate earnings

def substract_wrong_guesses_coins():
    """
        Substract coins to all players that have done wrong guesses (hang punishment)
    """
    for player_name in hangman_players:
        num_wrong_guesses = hangman_players[player_name].num_wrong_guesses
        hangman_players[player_name].earnings -= LOSS_COINS_PER_HANG_WRONG_GUESS * num_wrong_guesses

def update_game_winners_coins(game_winners):
    """
        Divide the prize between the players that have guessed the sentence
        (accumulate it in the player's earnings)
    """
    for name in game_winners:
        hangman_players[name].earnings += math.ceil(pot_per_sentence_guess / len(game_winners))
