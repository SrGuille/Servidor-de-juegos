from servidor import main_views
import random
from typing import List, Tuple, Dict
from servidor import queries as q
import threading
import os
from servidor.classes import PalabrazoActor
import random
from . import use_openai_api as openai_api
from itertools import groupby

class PalabrazoGame:

    def __init__(self):
        print("[PalabrazoGame] Inicializando juego...")
        self.SENTENCE_WORDS = (12, 15)  # Min and max number of words in the sentence
        self.ACTORS_PER_SENTENCE = (2, 2)  # Min and max number of actors in the sentence
        self.SEED_JACKPOT_PER_PLAYER = 10  # Initial jackpot per player

        self.PUNISHMENT_PER_REVEALED_LETTER = 0 # No punishment for revealing letters (would produce deflation)
        self.REWARD_PER_GUESSED_LETTER = 5
        self.PUNISHMENT_PER_WRONG_WORD = 5

        self.JACKPOT_TOP_WINNERS = [0.5, 0.3, 0.2]  # Jackpot percentage per winner position (top1, top2, top3)

        self.jackpot = 0
        self.sentence = ""
        self.partially_guessed_sentence = []

        self.palabrazo_players_scores = {}  # Dict with the players names and their scores

        # Cargar solo los prompts de 1 actor y 2 actores
        prompts_dir = os.path.join(os.path.dirname(__file__), 'prompts')
        prompt_1_actor_path = os.path.join(prompts_dir, 'prompt_1_actor.md')
        prompt_2_actors_path = os.path.join(prompts_dir, 'prompt_2_actors.md')
        with open(prompt_1_actor_path, encoding='utf-8') as f:
            self.PROMPT_1_ACTOR = f.read()
        with open(prompt_2_actors_path, encoding='utf-8') as f:
            self.PROMPT_2_ACTORS = f.read()

        self.players_lock = threading.Lock()

        # Parámetros de ponderación para la selección de palabra y letra a revelar
        self.VOWEL_WEIGHT = 4.0
        self.FIRST_LETTER_WEIGHT = 2.0  # Peso extra para la primera letra
        self.UNCOMMON_LETTER_WEIGHT = 5.0  # Peso extra para letras poco comunes
        self.COMMON_LETTER_WEIGHT = 2.0  # Peso extra para letras comunes
        self.ADJACENT_REVEALED_PENALTY = -1.0  # Penalización si está junto a letra ya revelada
        self.UNCOMMON_LETTERS = set('qhfzjñxkw')  # consonantes poco comunes en español
        self.COMMON_LETTERS = set('srndlc')  # consonantes frecuentes en español
        self.VOWELS = set('aeiou')

    def get_partially_guessed_sentence_words(self):
        """
            Initializes the partially guessed sentence with underscores for letters.
            Leaves commas as an independent word.
        """
        partially_guessed_sentence_words = []
        for word in self.sentence_words:
            partially_guessed_sentence_word = []
            if word == ',':
                partially_guessed_sentence_word.append(',')
            else:
                underscore_word = '_' * len(word) # Totally censored word
                partially_guessed_sentence_word.extend(underscore_word)
            partially_guessed_sentence_words.append(partially_guessed_sentence_word)    
        print(f"[get_partially_guessed_sentence_words] Devuelve: {partially_guessed_sentence_words}")
        return partially_guessed_sentence_words
    
    def get_legible_partially_guessed_sentence(self) -> str:
        """
            Returns the partially guessed sentence as a legible string
        """
        legible_sentence = ''
        for word in self.partially_guessed_sentence_words:
            if word == [',']:
                legible_sentence += ', '
            else:
                legible_sentence += ''.join(word) + ' '
        resultado = legible_sentence.strip()
        return resultado

    def get_sentence_words(self, sentence: str) -> List[str]:
        """
            Splits the sentence into words. 
            Removes punctuation except commas.
            Commas are considered and extra word.
        """

        sentence_words = []
        current_word = ''
        for char in sentence:
            if char.isalpha():
                current_word += char
            else:
                if current_word != '':
                    sentence_words.append(current_word)
                    current_word = ''
                if char == ',':
                    sentence_words.append(',')
        if current_word != '':
            sentence_words.append(current_word)
        print(f"[get_sentence_words] Devuelve: {sentence_words}")
        return sentence_words
    
    def normalize_sentence_words(self, sentence_words: List[str]) -> List[str]:
        """
            Normalizes the sentence words by:
            - Leaving commas as they are (independent word)
            - Converting them to lowercase
            - Remoiving spanish accents
        """
        normalized_words = []
        for word in sentence_words:
            if word == ',':
                normalized_words.append(',')
            else:
                normalized_word = self.normalize_word(word)
                normalized_words.append(normalized_word)
        print(f"[normalize_sentence_words] Devuelve: {normalized_words}")
        return normalized_words
    
    def normalize_word(self, word: str) -> str:
        """
            Normalizes a word by:
            - Converting it to lowercase
            - Remoiving spanish accents
        """

        spanish_accents = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
                           'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U'}
        
        normalized_word = ''
        for char in word:
            if char in spanish_accents:
                normalized_word += spanish_accents[char].lower()
            elif char.isalpha():
                normalized_word += char.lower()
            elif char == '_': # Keep underscores as they are
                normalized_word += '_'

        return normalized_word
    
    def reveal_letter(self):
        self.players_lock.acquire()
        # Lógica: excluir palabras con solo una letra pendiente (en cualquier posición) de la selección normal
        normalized_sentence_words = self.normalize_sentence_words(self.sentence_words)
        normalized_partially_guessed_sentence_words = self.normalize_sentence_words(self.partially_guessed_sentence_words)
        candidates = []
        for i, (word, partial) in enumerate(zip(normalized_sentence_words, normalized_partially_guessed_sentence_words)):
            if word == ',':
                continue
            unrevealed_indices = [j for j, c in enumerate(partial) if c == '_']
            if len(unrevealed_indices) <= 1:
                continue  # Excluir palabras con solo una letra pendiente
            total_letters = len(word)
            percent_revealed = (total_letters - len(unrevealed_indices)) / total_letters
            candidates.append((percent_revealed, -total_letters, i, unrevealed_indices))
        if candidates:
            candidates.sort()
            chosen_word_idx = candidates[0][2]
            partial = self.partially_guessed_sentence_words[chosen_word_idx]
            word = self.sentence_words[chosen_word_idx]
            unrevealed_indices = candidates[0][3]
            # Elegir la letra a revelar según los parámetros originales, entre todas las letras pendientes
            letter_weights = []
            for j, (c_partial, c_real) in enumerate(zip(partial, word)):
                if c_partial != '_':
                    letter_weights.append(0)
                    continue
                weight = 0
                if c_real in self.VOWELS:
                    weight += self.VOWEL_WEIGHT
                if j == 0:
                    weight += self.FIRST_LETTER_WEIGHT
                if c_real in self.UNCOMMON_LETTERS:
                    weight += self.UNCOMMON_LETTER_WEIGHT
                if c_real in self.COMMON_LETTERS:
                    weight += self.COMMON_LETTER_WEIGHT
                adj_penalty = 0
                if j > 0 and partial[j-1] != '_':
                    adj_penalty += self.ADJACENT_REVEALED_PENALTY
                if j < len(partial)-1 and partial[j+1] != '_':
                    adj_penalty += self.ADJACENT_REVEALED_PENALTY
                weight += adj_penalty
                letter_weights.append(max(weight, 1))
            total_letter_weight = sum(letter_weights)
            if total_letter_weight == 0:
                self.players_lock.release()
                return self.get_legible_partially_guessed_sentence(), self.jackpot, self.get_num_pending_letters()
            r = random.uniform(0, total_letter_weight)
            acc = 0
            chosen_letter_idx = None
            for j, w in enumerate(letter_weights):
                acc += w
                if r <= acc:
                    chosen_letter_idx = j
                    break
            self.partially_guessed_sentence_words[chosen_word_idx][chosen_letter_idx] = self.sentence_words[chosen_word_idx][chosen_letter_idx]
            self.jackpot -= 0  # PUNISHMENT_PER_REVEALED_LETTER
            if self.jackpot < 0:
                self.jackpot = 0
            legible_partially_guessed_sentence = self.get_legible_partially_guessed_sentence()
            jackpot = self.jackpot
            num_pending_letters = self.get_num_pending_letters()
            self.players_lock.release()
            return legible_partially_guessed_sentence, jackpot, num_pending_letters
        # Si no hay candidatas normales, solo quedan palabras con una letra pendiente
        one_left_candidates = []
        for i, (word, partial) in enumerate(zip(normalized_sentence_words, normalized_partially_guessed_sentence_words)):
            if word == ',':
                continue
            unrevealed_indices = [j for j, c in enumerate(partial) if c == '_']
            if len(unrevealed_indices) == 1:
                one_left_candidates.append((i, unrevealed_indices[0]))
        if not one_left_candidates:
            self.players_lock.release()
            return self.get_legible_partially_guessed_sentence(), self.jackpot, self.get_num_pending_letters()
        # Elegir aleatoriamente una palabra y revelar su única letra pendiente (puede estar en cualquier posición)
        chosen_word_idx, idx_to_reveal = random.choice(one_left_candidates)
        self.partially_guessed_sentence_words[chosen_word_idx][idx_to_reveal] = self.sentence_words[chosen_word_idx][idx_to_reveal]
        self.jackpot -= 0  # PUNISHMENT_PER_REVEALED_LETTER
        if self.jackpot < 0:
            self.jackpot = 0
        legible_partially_guessed_sentence = self.get_legible_partially_guessed_sentence()
        jackpot = self.jackpot
        num_pending_letters = self.get_num_pending_letters()
        self.players_lock.release()
        return legible_partially_guessed_sentence, jackpot, num_pending_letters
    
    def get_palabrazo_data(self) -> Tuple[str, int]:
        """
            Returns the partially guessed sentence and the current jackpot
        """
        self.players_lock.acquire()
        legible_partially_guessed_sentence = self.get_legible_partially_guessed_sentence()
        jackpot = self.jackpot
        num_pending_letters = self.get_num_pending_letters()
        self.players_lock.release()
        return legible_partially_guessed_sentence, jackpot, num_pending_letters

    def get_num_pending_letters(self) -> int:
        """
            Counts the number of not yet revealed letters in the partially guessed sentence
        """
        num_pending_letters = 0
        for word in self.partially_guessed_sentence_words:
            for char in word:
                if char == '_':
                    num_pending_letters += 1
        return num_pending_letters
    
    def generate_input_data(self, actors: List[PalabrazoActor]):
        """
            Generate the input data for the prompt that can have 1 or 2 actors (with their characteristics) and can have a repeated letter
        """
        actor1 = actors[0]
        input_data = '\n\nLos parámetros para esta frase son:'
        if len(actors) == 1:
            input_data += f'\n-{actor1.name}: {", ".join(actor1.attributes)}.'
        else:
            actor2 = actors[1]
            input_data += f'\n-{actor1.name}: {actor1.attributes[0]}.'
            input_data += f'\n-{actor2.name}: {actor2.attributes[0]}.'
        print(input_data)
        print(f"[generate_input_data] Devuelve: {input_data}")
        return input_data
    
    def create_sentence(self) -> dict:
        """
            Decide which prompt to apply (1 or 2 actors), the involved actors, and generate the sentence with the OpenAI API
        """
        
        num_actors = random.randint(self.ACTORS_PER_SENTENCE[0], self.ACTORS_PER_SENTENCE[1])
        actors_names = random.sample(list(self.palabrazo_players_scores.keys()), num_actors)
        actors = []

        if num_actors == 1: # 1 actor with 2 attributes
            prompt_template = self.PROMPT_1_ACTOR
            actor_attributes = q.get_player_attributes(actors_names[0])
            actors.append(PalabrazoActor(actors_names[0], actor_attributes))
        else: # 2 actors with 1 attribute each
            prompt_template = self.PROMPT_2_ACTORS
            for actor_name in actors_names:
                actor_attributes = q.get_player_attributes(actor_name)
                selected_attribute = [random.choice(actor_attributes)]
                actors.append(PalabrazoActor(actor_name, selected_attribute))

        input_data = self.generate_input_data(actors)
        sentence = openai_api.generate_sentence(prompt_template, input_data)
        #sentence = "Stefany sueña que en Sofía se aprende el tiro Innazumma Eleven, con ajos"  # For testing purposes

        self.sentence_words = self.get_sentence_words(sentence)
        self.partially_guessed_sentence_words = self.get_partially_guessed_sentence_words()
        print(f"[create_sentence] Devuelve: frase='{sentence}', palabras={self.sentence_words}, parcial={self.partially_guessed_sentence_words}")

    def setup_seed_jackpot(self) -> None:
        """
            Sets up the jackpot based on the number of players
        """
        num_players = len(self.palabrazo_players_scores)
        self.jackpot = num_players * self.SEED_JACKPOT_PER_PLAYER
        for name in self.palabrazo_players_scores:
            q.add_coins_to_player(name, -self.SEED_JACKPOT_PER_PLAYER)

    def setup_palabrazo(self) -> Tuple[str, int]:
        """
            Sets up the players, sentence and the jackpot based on the number of players
        """
        self.players_lock.acquire()

        self.palabrazo_players_scores = {}
        player_names = q.get_logged_players_names()
        for name in player_names:
            self.palabrazo_players_scores[name] = 0

        self.create_sentence()
        self.setup_seed_jackpot()
        legible_partially_guessed_sentence = self.get_legible_partially_guessed_sentence()
        num_pending_letters = self.get_num_pending_letters()
        self.players_lock.release()
        print(f"[setup_palabrazo] Devuelve: frase={legible_partially_guessed_sentence}, jackpot={self.jackpot}, pendientes={num_pending_letters}")
        return legible_partially_guessed_sentence, self.jackpot, num_pending_letters
    
    def has_finished(self) -> bool:
        """
            Returns true if the game is not ready (call it only after several seconds of starting the game)
        """
        has_finished = False
        if not main_views.main_controller_.get_can_players_interact(): # The game is not ready
            has_finished = True
        print(f"[has_finished] Devuelve: {has_finished}")
        return has_finished

    def register_player_guess(self, name: str, guessed_word: str) -> bool:
        """
            Checks if the word given by the player is in the sentence. Several scenarios depending on whether the word is in the sentence or not:
            - If it is not: increases the number of wrong words of the player and returns false
            - It is, but it was already guessed: returns true but does not update anything
            - It is and was not guessed yet:
                - The word appears once: reveals the letter in the partially guessed sentence, increases the number of guessed letters of the player, gives coins to the player, and returns true
                - The word appears multiple times: reveals all the appearances in the partially guessed sentence, increases the number of guessed letters of the player accordingly, gives coins to the player accordingly, and returns true
            
            If it was not guessed yet: updates the partially guessed sentence and the player's stats accordingly
        """
        
        is_valid = False # For the case where the game is not ready

        if not main_views.main_controller_.get_can_players_interact(): # The game is not ready
            return is_valid
        
        else: # The game is ready
            self.players_lock.acquire()

            normalized_sentence_words = self.normalize_sentence_words(self.sentence_words)
            normalized_guessed_word = self.normalize_word(guessed_word)
            print(f"[register_player_guess] Recibido: {guessed_word} de {name}")
            normalized_partially_guessed_sentence_words = self.normalize_sentence_words(self.partially_guessed_sentence_words)
            print(f"[register_player_guess] Parcial: {normalized_partially_guessed_sentence_words}")
            # Determine if the word is in the sentence
            is_present = normalized_guessed_word in normalized_sentence_words
            if not is_present: # The word is not in the sentence
                is_valid = False
                self.palabrazo_players_scores[name] += -self.PUNISHMENT_PER_WRONG_WORD
                q.add_coins_to_player(name, -self.PUNISHMENT_PER_WRONG_WORD)
                self.jackpot += self.PUNISHMENT_PER_WRONG_WORD  # Increase the jackpot
                print(f"[register_player_guess] Fallo. Puntuación {name}: {self.palabrazo_players_scores[name]}, Jackpot: {self.jackpot}")
            else: # The word is in the sentence
                is_valid = True
                was_already_guessed = normalized_guessed_word in normalized_partially_guessed_sentence_words
                print(f"[register_player_guess] ¿Ya adivinada?: {was_already_guessed}")
                if not was_already_guessed: # The word was not guessed yet
                    partially_guessed_appearances = self.find_and_reveal_all_partially_guessed_appearances(guessed_word, normalized_guessed_word, normalized_sentence_words, normalized_partially_guessed_sentence_words)
                    for appearance in partially_guessed_appearances:
                        num_not_guessed_letters = self.get_number_of_not_guessed_letters(appearance)
                        player_reward = num_not_guessed_letters * self.REWARD_PER_GUESSED_LETTER
                        self.palabrazo_players_scores[name] += player_reward
                        jackpot_before = self.jackpot
                        self.jackpot -= player_reward
                        if self.jackpot < 0:
                            # Darle las monedas que quedaban en el jackpot antes de llegar a 0
                            self.jackpot = 0
                            q.add_coins_to_player(name, jackpot_before)                         
                        else:
                            q.add_coins_to_player(name, player_reward)
                        print(f"[register_player_guess] Acierto. Puntuación {name}: {self.palabrazo_players_scores[name]}, Jackpot: {self.jackpot}")
            self.players_lock.release()

        return is_valid
    
    def find_and_reveal_all_partially_guessed_appearances(self, word: str, normalized_word: str, normalized_sentence_words: str, normalized_partially_guessed_sentence_words: str) -> List[int]:
        """
            If the word appears more than once in the sentence, each instance may have different letters revealed.
            This function finds all the positions where the word appears in sentence and returns how it is revealed in the partially guessed sentence.
            Also updates the not normalized partially guessed sentence to reveal the whole word in each appearance.
        """    
        partially_guessed_appearances = []
        for i, normalized_sentence_word in enumerate(normalized_sentence_words):
            if normalized_sentence_word == normalized_word:
                partially_guessed_appearances.append(normalized_partially_guessed_sentence_words[i])
                not_normalized_word = self.sentence_words[i] # Get the original word with accents
                self.partially_guessed_sentence_words[i] = not_normalized_word  # Reveal the whole word in the partially guessed sentence
        print(f"[find_and_reveal_all_partially_guessed_appearances] Devuelve: {partially_guessed_appearances}")
        return partially_guessed_appearances        

    def get_number_of_not_guessed_letters(self, word) -> int:
        """
            Returns the number of not guessed letters in a word
        """
        num_not_guessed = 0
        for char in word:
            if char == '_':
                num_not_guessed += 1
        print(f"[get_number_of_not_guessed_letters] Devuelve: {num_not_guessed}")
        return num_not_guessed  

    def finish_palabrazo(self):
        print(f"Players: {self.palabrazo_players_scores}")
        
        players_and_prize = self.compute_prizes()
        self.give_prizes(players_and_prize)
        winner_msj = self.build_winners_message(players_and_prize)
        return winner_msj

    def compute_prizes(self) -> Dict[str, int]:
        sorted_players = sorted(
            self.palabrazo_players_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        grouped_by_score = [
            list(group)
            for _, group in groupby(sorted_players, key=lambda x: x[1])
        ]

        total_positions = len(self.JACKPOT_TOP_WINNERS)

        prizes_percentage = {}   # jugador -> porcentaje ganado
        awarded_players = set()
        position = 0
        unassigned_percentage = 0.0

        for group in grouped_by_score:
            if position >= total_positions:
                break

            group_size = len(group)
            positions_covered = range(
                position,
                min(position + group_size, total_positions)
            )

            if not positions_covered:
                break

            percentage = sum(self.JACKPOT_TOP_WINNERS[p] for p in positions_covered)
            share = percentage / group_size

            for player, _ in group:
                prizes_percentage[player] = prizes_percentage.get(player, 0) + share
                awarded_players.add(player)

            position += len(positions_covered)

        # Porcentaje que quedó sin asignar (posiciones vacías)
        assigned_percentage = sum(prizes_percentage.values())
        unassigned_percentage = 1.0 - assigned_percentage

        if unassigned_percentage > 0 and awarded_players:
            bonus = unassigned_percentage / len(awarded_players)
            for player in awarded_players:
                prizes_percentage[player] += bonus

        # Convertir a monedas
        players_and_prize = {
            player: round(self.jackpot * pct)
            for player, pct in prizes_percentage.items()
        }
    
        return players_and_prize

    def build_winners_message(self, prizes: dict) -> str:
        """
        Construye el mensaje HTML del top de ganadores a partir de puntuaciones
        y premios ya calculados.
        """

        sorted_players = sorted(
            self.palabrazo_players_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        grouped_by_score = [
            list(group)
            for _, group in groupby(sorted_players, key=lambda x: x[1])
        ]

        message = "Top de ganadores:<br>"
        position = 1

        for group in grouped_by_score:
            players = [player for player, _ in group]

            # Solo mostramos jugadores premiados
            players = [p for p in players if p in prizes]
            if not players:
                break

            score = group[0][1]
            prize = prizes[players[0]]

            if len(players) == 1:
                message += (
                    f"<br>{position}º {players[0]}, "
                    f"con una puntuación de {score} "
                    f"se lleva {prize} monedas del bote."
                )
            else:
                names = ", ".join(players)
                message += (
                    f"<br>{position}º (empatados) {names}, "
                    f"con una puntuación de {score} "
                    f"se llevan {prize} monedas del bote cada uno."
                )

            position += len(players)

        return message
        
    def give_prizes(self, players_and_prize: Dict[str, int]) -> None:
        """
            Gives the prizes to the winners
        """
        self.players_lock.acquire()

        for winner_name, prize in players_and_prize.items():
            q.add_coins_to_player(winner_name, prize)

        self.players_lock.release()
        print(f"[give_prizes] Devuelve: {players_and_prize}")

