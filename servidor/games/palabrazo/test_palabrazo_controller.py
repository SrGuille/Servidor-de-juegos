import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
import unittest
from unittest.mock import patch, MagicMock
from palabrazo_controller import PalabrazoGame

class TestPalabrazoGame(unittest.TestCase):
    def setUp(self):
        self.game = PalabrazoGame()
        self.game.player_names = ['Ana', 'Luis', 'Marta']

    @patch('servidor.games.palabrazo.palabrazo_controller.q.get_logged_players_names')
    @patch('servidor.games.palabrazo.palabrazo_controller.q.get_player_attributes')
    @patch('servidor.games.palabrazo.palabrazo_controller.openai_api.generate_sentence')
    @patch('servidor.games.palabrazo.palabrazo_controller.q.add_coins_to_player')
    @patch('servidor.games.palabrazo.palabrazo_controller.main_views.main_controller_.get_can_players_interact')
    def test_full_game_flow(self, mock_interact, mock_add_coins, mock_generate_sentence, mock_get_attrs, mock_get_names):
        # Setup mocks
        mock_get_names.return_value = ['Ana', 'Luis', 'Marta']
        mock_get_attrs.side_effect = lambda name: ['inteligente', 'rápido']
        mock_generate_sentence.return_value = 'gato, perro, casa, árbol, coche, sol, luna, Ana, Luis, Marta, rápido, inteligente'
        mock_interact.return_value = True

        # Setup game
        sentence, jackpot = self.game.setup_palabrazo()
        self.assertTrue(isinstance(sentence, str))
        self.assertEqual(jackpot, 30)
        self.assertEqual(len(self.game.palabrazo_players_scores), 3)

        # Simulate guesses
        self.assertTrue(self.game.register_player_guess('Ana', 'gato'))
        self.assertFalse(self.game.register_player_guess('Luis', 'noexiste'))
        self.assertTrue(self.game.register_player_guess('Marta', 'perro'))
        self.assertTrue(self.game.register_player_guess('Ana', 'casa'))

        # Finish game and check winners
        result = self.game.finish_palabrazo()
        self.assertIn('top de ganadores', result)
        self.assertTrue(any(name in result for name in ['Ana', 'Luis', 'Marta']))

if __name__ == '__main__':
    unittest.main()
