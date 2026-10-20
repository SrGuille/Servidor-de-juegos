
import unittest
import random
import threading

class PalabrazoGame:
    def reveal_letter_random(self):
        self.players_lock.acquire()
        not_revealed_positions = []
        for i, word in enumerate(self.partially_guessed_sentence_words):
            if word == [',']:
                continue
            for j, char in enumerate(word):
                if char == '_':
                    not_revealed_positions.append((i, j))
        if not not_revealed_positions:
            self.players_lock.release()
            return self.get_legible_partially_guessed_sentence(), self.jackpot, self.get_num_pending_letters()
        i, j = random.choice(not_revealed_positions)
        self.partially_guessed_sentence_words[i][j] = self.sentence_words[i][j]
        self.jackpot -= 0
        if self.jackpot < 0:
            self.jackpot = 0
        legible_partially_guessed_sentence = self.get_legible_partially_guessed_sentence()
        jackpot = self.jackpot
        num_pending_letters = self.get_num_pending_letters()
        self.players_lock.release()
        return legible_partially_guessed_sentence, jackpot, num_pending_letters
    def __init__(self):
        sentence = "Stef jura que en Sofía se aprende el tiro Inazuma Eleven, con ajos"
        # Procesar la frase igual que en el controlador original
        self.sentence_words = []
        current_word = ''
        for char in sentence:
            if char.isalpha():
                current_word += char
            else:
                if current_word != '':
                    self.sentence_words.append(current_word)
                    current_word = ''
                if char == ',':
                    self.sentence_words.append(',')
        if current_word != '':
            self.sentence_words.append(current_word)
        self.partially_guessed_sentence_words = [['_']*len(w) if w != ',' else [','] for w in self.sentence_words]
        self.jackpot = 100
        # self.WORD_LENGTH_WEIGHT = 3.0
        # self.WORD_UNREVEALED_WEIGHT = 2.0
        self.VOWEL_WEIGHT = 4.0
        self.FIRST_LETTER_WEIGHT = 2.0  # Peso extra para la primera letra
        self.UNCOMMON_LETTER_WEIGHT = 5.0  # Peso extra para letras poco comunes
        self.COMMON_LETTER_WEIGHT = 2.0  # Peso extra para letras comunes
        self.ADJACENT_REVEALED_PENALTY = -1.0  # Penalización si está junto a letra ya revelada
        self.UNCOMMON_LETTERS = set('qhfzjñxkw')  # consonantes poco comunes en español
        self.COMMON_LETTERS = set('srndlc')  # consonantes frecuentes en español
        self.VOWELS = set('aeiouáéíóú')
        self.players_lock = threading.Lock()

    def get_legible_partially_guessed_sentence(self):
        legible_sentence = ''
        for word in self.partially_guessed_sentence_words:
            if word == [',']:
                legible_sentence += ', '
            else:
                legible_sentence += ''.join(word) + ' '
        return legible_sentence.strip()

    def get_num_pending_letters(self):
        num_pending_letters = 0
        for word in self.partially_guessed_sentence_words:
            for char in word:
                if char == '_':
                    num_pending_letters += 1
        return num_pending_letters

    def reveal_letter(self):
        self.players_lock.acquire()
        # 1. Buscar palabras con más de una letra sin revelar (candidatas normales)
        candidates = []
        for i, (word, partial) in enumerate(zip(self.sentence_words, self.partially_guessed_sentence_words)):
            if word == [',']:
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
                if c_real.lower() in self.VOWELS:
                    weight += self.VOWEL_WEIGHT
                if j == 0:
                    weight += self.FIRST_LETTER_WEIGHT
                if c_real.lower() in self.UNCOMMON_LETTERS:
                    weight += self.UNCOMMON_LETTER_WEIGHT
                if c_real.lower() in self.COMMON_LETTERS:
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
        # 2. Si no hay candidatas normales, solo quedan palabras con una letra sin revelar
        one_left_candidates = []
        for i, (word, partial) in enumerate(zip(self.sentence_words, self.partially_guessed_sentence_words)):
            if word == [',']:
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

class TestRevealLetter(unittest.TestCase):
    def test_reveal_timing_statistics(self):
        runs = 1000
        word_indices = [i for i, w in enumerate(PalabrazoGame().sentence_words) if w != ',']
        word_names = [PalabrazoGame().sentence_words[i] for i in word_indices]
        # Para cada letra, cuántas veces se reveló antes del 25%, 50% y 75% de los turnos
        stats_25 = {w: [0]*len(w) for w in word_names}
        stats_50 = {w: [0]*len(w) for w in word_names}
        stats_75 = {w: [0]*len(w) for w in word_names}

        for _ in range(runs):
            game = PalabrazoGame()
            total_letters = sum(len(w) for w in game.partially_guessed_sentence_words if w != [','])
            reveal_turn = {w: [None]*len(w) for w in word_names}
            for turn in range(total_letters):
                before = [list(word) for word in game.partially_guessed_sentence_words]
                legible, jackpot, pending = game.reveal_letter()
                after = game.partially_guessed_sentence_words
                for idx, widx in enumerate(word_indices):
                    for j, (b, a) in enumerate(zip(before[widx], after[widx])):
                        if b == '_' and a != '_':
                            reveal_turn[word_names[idx]][j] = turn
            for w in word_names:
                for j, t in enumerate(reveal_turn[w]):
                    if t is not None:
                        if t < total_letters * 0.25:
                            stats_25[w][j] += 1
                        if t < total_letters * 0.5:
                            stats_50[w][j] += 1
                        if t < total_letters * 0.75:
                            stats_75[w][j] += 1

        print("\n--- % de veces que cada letra se reveló antes del 25%, 50% y 75% de los turnos (ponderado) ---")
        for w in word_names:
            print(f"Palabra: {w}")
            print(f"  <25%:  {[f'{100*x/runs:.1f}%' for x in stats_25[w]]}")
            print(f"  <50%:  {[f'{100*x/runs:.1f}%' for x in stats_50[w]]}")
            print(f"  <75%:  {[f'{100*x/runs:.1f}%' for x in stats_75[w]]}")
    
    # def test_reveal_letter_random(self):
    #     # Usar una nueva instancia para no mezclar con el test principal
    #     game = PalabrazoGame()
    #     total_letters = sum(len(w) for w in game.partially_guessed_sentence_words if w != [','])
    #     for _ in range(total_letters):
    #         legible, jackpot, pending = game.reveal_letter_random()
    #         print(f"[Random] Frase: {legible} | Jackpot: {jackpot} | Pendientes: {pending}")
    #         self.assertLessEqual(sum(w.count('_') for w in game.partially_guessed_sentence_words), total_letters)
    #         self.assertGreaterEqual(jackpot, 0)

    def setUp(self):
        self.game = PalabrazoGame()

    def test_reveal_letter(self):
        total_letters = sum(len(w) for w in self.game.partially_guessed_sentence_words if w != [','])
        for _ in range(total_letters):
            legible, jackpot, pending = self.game.reveal_letter()
            print(f"Frase: {legible} | Jackpot: {jackpot} | Pendientes: {pending}")
            self.assertLessEqual(sum(w.count('_') for w in self.game.partially_guessed_sentence_words), total_letters)
            self.assertGreaterEqual(jackpot, 0)

    #     # Llamar al test de revelado aleatorio a continuación
    #     print("\n--- Revelado aleatorio ---")
    #     game = PalabrazoGame()
    #     total_letters = sum(len(w) for w in game.partially_guessed_sentence_words if w != [','])
    #     for _ in range(total_letters):
    #         legible, jackpot, pending = game.reveal_letter_random()
    #         print(f"[Random] Frase: {legible} | Jackpot: {jackpot} | Pendientes: {pending}")
    #         self.assertLessEqual(sum(w.count('_') for w in game.partially_guessed_sentence_words), total_letters)
    #         self.assertGreaterEqual(jackpot, 0)

if __name__ == '__main__':
    unittest.main()
