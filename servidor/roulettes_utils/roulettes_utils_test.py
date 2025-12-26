import os
import sys

# Añadir el directorio raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from servidor import constants as c
from servidor.roulettes_utils.roulettes_utils import (
    create_players_roulette,
    create_prizes_roulette,
    get_players_color_palette,
    _get_text_color
)

# ============== TESTS ==============

class MockPlayer:
    """Clase mock para simular jugadores."""
    def __init__(self, nick, coins):
        self.nick = nick
        self.coins = coins


class MockPrize:
    """Clase mock para simular premios."""
    def __init__(self, type, amount, prob):
        self.type = type
        self.amount = amount
        self.prob = prob


def test_players_roulette_16():
    """Test de ruleta con 16 jugadores."""
    players = [
        MockPlayer("Alice", 150),
        MockPlayer("Bob", 200),
        MockPlayer("Carlos", 80),
        MockPlayer("Diana", 120),
        MockPlayer("Eduardo Gumersindo", 90),
        MockPlayer("Fiona", 175),
        MockPlayer("Gabriel", 60),
        MockPlayer("Helena", 140),
        MockPlayer("Iván", 110),
        MockPlayer("Julia", 95),
        MockPlayer("Kevin", 130),
        MockPlayer("Laura", 85),
        MockPlayer("Miguel", 160),
        MockPlayer("Nadia", 70),
        MockPlayer("Oscar", 145),
        MockPlayer("Patricia", 100),
        MockPlayer("Quentin de la Rosa", 50),
        MockPlayer("Rita", 1),
        MockPlayer("Sergio", 300),
        MockPlayer("Tania", 0),
    ]
    
    print("=== Test: Ruleta de 16 jugadores ===")
    create_players_roulette(players)
    print("✓ Ruleta de jugadores creada: servidor/static/img/players_roulette.png\n")


def test_prizes_roulette():
    """Test de ruleta de premios."""
    prizes = [
        MockPrize("Regalo Grande", 2, 0.3333),
        MockPrize("Regalo Mediano", 5, 0.3333),
        MockPrize("Regalo Pequeño", 10, 0.3333),
    ]
    
    print("=== Test: Ruleta de premios ===")
    create_prizes_roulette(prizes)
    print("✓ Ruleta de premios creada: servidor/static/img/prizes_roulette.png\n")


def test_color_palette_constraints():
    """Verifica que la paleta cumple las restricciones."""
    print("=== Test: Restricciones de paleta de colores ===")
    
    color_families = ["red", "green", "blue", "orange"]
    intensities = ["300", "400", "500", "600", "700", "800"]
    
    # Crear mapeo inverso: hex -> (familia, intensidad)
    hex_to_info = {}
    for family in color_families:
        for intensity in intensities:
            hex_color = c.COLOR_PALETTE[family][intensity]
            hex_to_info[hex_color] = (family, intensity)
    
    # Probar varias veces (por la rotación aleatoria)
    for test_num in range(5):
        colors, text_colors = get_players_color_palette(16)
        
        for i in range(len(colors)):
            current = hex_to_info[colors[i]]
            next_idx = (i + 1) % len(colors)
            next_color = hex_to_info[colors[next_idx]]
            
            # Verificar familia diferente
            assert current[0] != next_color[0], \
                f"Error: Familias iguales en posición {i} y {next_idx}: {current[0]}"
            
            # Verificar intensidad diferente
            assert current[1] != next_color[1], \
                f"Error: Intensidades iguales en posición {i} y {next_idx}: {current[1]}"
    
    print("✓ Todas las restricciones de familia e intensidad cumplidas")
    print("✓ Verificado para 5 rotaciones aleatorias\n")


def test_text_colors():
    """Verifica que los colores de texto son correctos."""
    print("=== Test: Colores de texto ===")
    
    # Test casos específicos
    assert _get_text_color("red", "300") == "black", "red-300 debería ser negro"
    assert _get_text_color("red", "500") == "white", "red-500 debería ser blanco"
    assert _get_text_color("green", "400") == "black", "green-400 debería ser negro"
    assert _get_text_color("green", "600") == "white", "green-600 debería ser blanco"
    assert _get_text_color("blue", "400") == "black", "blue-400 debería ser negro"
    assert _get_text_color("blue", "500") == "white", "blue-500 debería ser blanco"
    assert _get_text_color("orange", "500") == "black", "orange-500 debería ser negro"
    assert _get_text_color("orange", "600") == "white", "orange-600 debería ser blanco"
    
    print("✓ Todos los colores de texto son correctos\n")


if __name__ == "__main__":
    # Asegurar que existe el directorio de salida
    os.makedirs("servidor/static/img", exist_ok=True)
    
    # Ejecutar tests
    test_text_colors()
    test_color_palette_constraints()
    test_players_roulette_16()
    test_prizes_roulette()
    
    print("=" * 40)
    print("✓ Todos los tests pasaron correctamente")