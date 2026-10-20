import pytest
from itertools import groupby

class DummyGame:
    JACKPOT_TOP_WINNERS = [0.5, 0.3, 0.2]

    def __init__(self, scores, jackpot=1000):
        self.palabrazo_players_scores = scores
        self.jackpot = jackpot
        self.given_prizes = None

    def give_prizes(self, prizes):
        self.given_prizes = prizes

    def finish_palabrazo(self):
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

        self.give_prizes(players_and_prize)


# 1️⃣ Un solo jugador
def test_single_player_gets_full_jackpot():
    game = DummyGame({"A": 10})
    game.finish_palabrazo()
    print(f"Given prizes: {game.given_prizes}")
    assert game.given_prizes == {"A": 1000}

# 2️⃣ Dos jugadores sin empate
def test_two_players_no_tie():
    game = DummyGame({"A": 10, "B": 5})
    game.finish_palabrazo()
    print(f"Given prizes: {game.given_prizes}")
    assert game.given_prizes == {"A": 600, "B": 400}

# 3️⃣ Dos jugadores empatados en 1º
def test_two_players_tied_first():
    game = DummyGame({"A": 10, "B": 10})
    game.finish_palabrazo()
    print(f"Given prizes: {game.given_prizes}")
    assert game.given_prizes == {"A": 500, "B": 500}

# 4️⃣ Tres jugadores sin empates
def test_three_players_no_tie():
    game = DummyGame({"A": 10, "B": 8, "C": 6})
    game.finish_palabrazo()
    print(f"Given prizes: {game.given_prizes}")
    assert game.given_prizes == {"A": 500, "B": 300, "C": 200}

# 5️⃣ Empate en 2º lugar
def test_tie_second_place():
    game = DummyGame({"A": 10, "B": 8, "C": 8})
    game.finish_palabrazo()
    print(f"Given prizes: {game.given_prizes}")
    assert game.given_prizes == {"A": 500, "B": 250, "C": 250}

# 5️⃣ Empate en 1º lugar, no en 3º
def test_tie_first_place_not_third():
    game = DummyGame({"A": 10, "B": 10, "C": 8})
    game.finish_palabrazo()
    print(f"Given prizes: {game.given_prizes}")
    assert game.given_prizes == {"A": 400, "B": 400, "C": 200}

# 6️⃣ Empate triple en 1º
def test_three_way_tie_first():
    game = DummyGame({"A": 10, "B": 10, "C": 10})
    game.finish_palabrazo()
    print(f"Given prizes: {game.given_prizes}")
    assert game.given_prizes == {"A": 333, "B": 333, "C": 333}

# 7️⃣ Más de 3 jugadores empatados en 1º (caso crítico)
def test_more_than_three_players_tied_first():
    game = DummyGame({"A": 10, "B": 10, "C": 10, "D": 10})
    game.finish_palabrazo()
    total = int(1000 * (0.5 + 0.3 + 0.2))
    per_player = round(total / 4)
    print(f"Given prizes: {game.given_prizes}")
    assert game.given_prizes == {"A": per_player, "B": per_player, "C": per_player, "D": per_player}

# 8️⃣ Empate en 3º con más jugadores detrás
def test_tie_third_place_with_extra_players():
    game = DummyGame({"A": 10, "B": 9, "C": 8, "D": 8, "E": 8, "F": 1})
    game.finish_palabrazo()
    print(f"Given prizes: {game.given_prizes}")
    assert game.given_prizes == {"A": 500, "B": 300, "C": 67, "D": 67, "E": 67}

def test_tie_third_place_with_extra_players_alternative():
    game = DummyGame({"A": 15, "B": 15, "C": 5, "D": 5, "E": 4, "F": 4})
    game.finish_palabrazo()
    print(f"Given prizes: {game.given_prizes}")
    assert game.given_prizes == {"A": 400, "B": 400, "C": 100, "D": 100}

# 9️⃣ Jugadores fuera del top no reciben premio
def test_players_outside_top_receive_nothing():
    game = DummyGame({"A": 10, "B": 9, "C": 8, "D": 7})
    game.finish_palabrazo()
    print(f"Given prizes: {game.given_prizes}")
    assert "D" not in game.given_prizes

# 🔟 Jackpot no divisible limpiamente (redondeo)
def test_rounding_does_not_crash():
    game = DummyGame({"A": 10, "B": 10, "C": 10}, jackpot=1001)
    game.finish_palabrazo()
    print(f"Given prizes: {game.given_prizes}")
    assert sum(game.given_prizes.values()) <= 1002

def test_lots_of_players_tied_on_second_place():
    game = DummyGame({
        "A": 10, "B": 9, "C": 9,
        "D": 9, "E": 9, "F": 9,
        "G": 8, "H": 8, "I": 8,
        "J": 1
    })
    game.finish_palabrazo()
    print(f"Given prizes: {game.given_prizes}")
    expected_prizes = {
        "A": 500, "B": 100, "C": 100,
        "D": 100, "E": 100, "F": 100
    }
    assert game.given_prizes == expected_prizes

# Lanzar todos los tests si se ejecuta este archivo directamente
if __name__ == "__main__":
    # Llamar a cada test
    test_single_player_gets_full_jackpot()
    test_two_players_no_tie()
    test_two_players_tied_first()
    test_three_players_no_tie()
    test_tie_second_place()
    test_tie_first_place_not_third()
    test_three_way_tie_first()
    test_more_than_three_players_tied_first()
    test_tie_third_place_with_extra_players()
    test_tie_third_place_with_extra_players_alternative()
    test_players_outside_top_receive_nothing()
    test_rounding_does_not_crash()
    test_lots_of_players_tied_on_second_place()

    print("All tests passed!")
