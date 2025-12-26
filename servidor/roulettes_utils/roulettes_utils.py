import os
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import random
import numpy as np
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
from servidor import constants as c

START_ANGLE = 90
COUNTERCLOCK = False
LABEL_DISTANCE = 0.95
ROTATE_LABELS = True
DONUT_HOLE_RADIUS = 0.4  # Radio del hueco central (0 = sin hueco, 1 = todo hueco)
matplotlib.rcParams['font.family'] = 'Arial'
matplotlib.rcParams['font.size'] = 10
matplotlib.rcParams['font.weight'] = 'bold'

# Colores para premios (fijos y distintivos)
PRIZE_COLORS = {
    "R. Grande": ("red", "600"),
    "R. Mediano": ("orange", "400"),
    "R. Pequeño": ("green", "600"),
}

# Imágenes para premios (ruta relativa desde la raíz del proyecto)
PRIZE_IMAGES = {
    "R. Grande": "servidor/static/img/iconos_regalos/regalo_grande.png",
    "R. Mediano": "servidor/static/img/iconos_regalos/regalo_mediano.png",
    "R. Pequeño": "servidor/static/img/iconos_regalos/regalo_peque.png",
}

# Creates the players roulette image with players with coins
def create_players_roulette(players):
    labels = []
    sizes = []

    for player in players:
        if(player.coins > 0): # Only players with coins
            labels.append(player.nick)
            sizes.append(player.coins)

    sizes = np.array(sizes)
    color_palette, text_colors = get_players_color_palette(len(labels))

    print(labels)
    print(sizes)

    create_roulette_image(labels, sizes, color_palette, text_colors, 'players_roulette')

# Creates the prizes roulette image with available prizes
def create_prizes_roulette(prizes):
    labels = []
    sizes = []
    colors = []
    images = []

    for prize in prizes:
        if(prize.amount > 0): # If there are prizes of this type
            label = prize.type.replace("Regalo", "R.")
            labels.append(label)
            sizes.append(prize.prob)
            
            family, intensity = PRIZE_COLORS.get(label)
            colors.append(c.COLOR_PALETTE[family][intensity])
            images.append(PRIZE_IMAGES.get(label))

    sizes = np.array(sizes)

    create_prizes_roulette_image(labels, sizes, colors, images, 'prizes_roulette')


def create_prizes_roulette_image(labels, sizes, colors, images, filename):
    """Crea la ruleta de premios con imágenes en cada gajo."""
    fig, ax = plt.subplots(figsize=(6, 6))
    
    wedge_width = 1 - DONUT_HOLE_RADIUS
    
    # Crear el pie chart sin labels (None para no mostrar ninguna etiqueta)
    wedges, _ = ax.pie(sizes, labels=None, colors=colors, 
                       startangle=START_ANGLE, counterclock=COUNTERCLOCK,
                       wedgeprops={'width': wedge_width, 'edgecolor': 'white', 'linewidth': 2})
    
    # Calcular las posiciones para las imágenes (centro de cada gajo)
    total = sum(sizes)
    cumulative = 0
    
    for i, (wedge, size, img_path) in enumerate(zip(wedges, sizes, images)):
        # Calcular el ángulo central del gajo
        angle_start = START_ANGLE - (cumulative / total) * 360
        angle_end = START_ANGLE - ((cumulative + size) / total) * 360
        angle_mid = np.radians((angle_start + angle_end) / 2)
        
        # Posición en el centro del anillo del donut
        r = 1 - wedge_width / 2  # Radio medio del anillo
        x = r * np.cos(angle_mid)
        y = r * np.sin(angle_mid)
        
        # Cargar y añadir la imagen si existe
        if img_path and os.path.exists(img_path):
            img = Image.open(img_path)
            # Asegurar que la imagen está en modo RGBA para transparencia correcta
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Calcular el tamaño proporcional al gajo
            proportion = size / total
            img_zoom = max(0.08, min(0.25, proportion * 0.8))  # Ajustado para mejor visualización
            
            imagebox = OffsetImage(img, zoom=img_zoom)
            ab = AnnotationBbox(imagebox, (x, y), frameon=False, zorder=10)
            ax.add_artist(ab)
        
        cumulative += size
    
    ax.set_aspect('equal')
    
    if os.path.exists(f'servidor/static/img/{filename}.png'):
        os.remove(f'servidor/static/img/{filename}.png')
    plt.savefig(f'servidor/static/img/{filename}.png', transparent=True, dpi=150, bbox_inches='tight')
    plt.close()

# Creates the roulette image (first delete it if it exists)
def create_roulette_image(labels, sizes, color_palette, text_colors, filename):
    fig, ax = plt.subplots()
    
    wedge_width = 1 - DONUT_HOLE_RADIUS
    
    wedges, _ = ax.pie(
        sizes,
        labels=None,
        colors=color_palette,
        startangle=START_ANGLE,
        counterclock=COUNTERCLOCK,
        wedgeprops={'width': wedge_width, 'edgecolor': 'white', 'linewidth': 1}
    )

    total = sum(sizes)
    proportions = [s / total for s in sizes]

    for label, size, text_color, proportion, wedge in zip(
        labels, sizes, text_colors, proportions, wedges
    ):
        theta1, theta2 = wedge.theta1, wedge.theta2
        angle_mid = (theta1 + theta2) / 2

        # Normalizar ángulo a [-180, 180]
        angle_norm = (angle_mid + 180) % 360 - 180
        angle_rad = np.deg2rad(angle_mid)

        # Posición del texto
        r = 1 - wedge_width / 2
        x = r * np.cos(angle_rad)
        y = r * np.sin(angle_rad)

        # Tamaño de fuente
        if proportion < 0.03:
            fontsize = 6
        elif proportion < 0.05:
            fontsize = 7
        elif proportion < 0.08:
            fontsize = 8
        elif proportion < 0.12:
            fontsize = 9
        else:
            fontsize = 10

        if len(label) > 15:
            fontsize = max(6, fontsize - 3)
        elif len(label) > 12:
            fontsize = max(6, fontsize - 2)
        elif len(label) > 9:
            fontsize = max(6, fontsize - 1)

        # --- ROTACIÓN CORRECTA (RADIAL Y LEGIBLE) ---
        if ROTATE_LABELS:
            rotation = angle_mid
            ha = 'center'

            # Si está en la mitad izquierda, girar 180°
            if angle_norm < -90 or angle_norm > 90:
                rotation = angle_mid + 180
        else:
            rotation = 0
            ha = 'center'

        ax.text(
            x,
            y,
            label,
            ha=ha,
            va='center',
            color=text_color,
            fontsize=fontsize,
            fontweight='bold',
            rotation=rotation,
            rotation_mode='anchor'
        )

    ax.set_aspect('equal')

    if os.path.exists(f'servidor/static/img/{filename}.png'):
        os.remove(f'servidor/static/img/{filename}.png')

    plt.savefig(
        f'servidor/static/img/{filename}.png',
        transparent=True,
        dpi=150,
        bbox_inches='tight'
    )
    plt.close()


def _get_text_color(family, intensity):
    """
    Devuelve blanco si la intensidad supera el umbral, negro en caso contrario.
    """
    threshold = c.WHITE_LETTERS_THRESHOLD.get(family, 500)
    return "white" if int(intensity) > threshold else "black"


def get_players_color_palette(number_colors):
    """
    Genera una paleta de colores para jugadores usando los colores de constants.
    Garantiza que colores adyacentes nunca tengan la misma familia ni intensidad.
    Usa un patrón determinista con rotación aleatoria.
    
    Returns:
        tuple: (lista de colores hex, lista de colores de texto)
    """
    color_families = ["red", "green", "blue", "orange"]
    intensities = ["300", "400", "500", "600", "700", "800"]
    
    # Patrón determinista de 24 colores que garantiza:
    # - Familias adyacentes siempre diferentes (ciclo: 0,1,2,3,0,1,2,3...)
    # - Intensidades adyacentes siempre diferentes
    # - Circularidad: el último y el primero también son diferentes
    full_pattern = [
        (0, 0), (1, 2), (2, 4), (3, 1),  # red-300, green-500, blue-700, orange-400
        (0, 3), (1, 5), (2, 1), (3, 4),  # red-600, green-800, blue-400, orange-700
        (0, 5), (1, 1), (2, 3), (3, 0),  # red-800, green-400, blue-600, orange-300
        (0, 2), (1, 4), (2, 0), (3, 3),  # red-500, green-700, blue-300, orange-600
        (0, 4), (1, 0), (2, 2), (3, 5),  # red-700, green-300, blue-500, orange-800
        (0, 1), (1, 3), (2, 5), (3, 2),  # red-400, green-600, blue-800, orange-500
    ]
    
    # Buscar un punto de inicio válido que garantice circularidad
    # para el número de colores solicitado
    valid_starts = []
    for start in range(len(full_pattern)):
        rotated = full_pattern[start:] + full_pattern[:start]
        subset = rotated[:number_colors]
        
        # Verificar circularidad (último vs primero)
        first_family, first_intensity = subset[0]
        last_family, last_intensity = subset[-1]
        
        if first_family != last_family and first_intensity != last_intensity:
            valid_starts.append(start)
    
    # Si hay puntos válidos, elegir uno aleatoriamente
    if valid_starts:
        start = random.choice(valid_starts)
    else:
        # Fallback: usar cualquier punto (no debería ocurrir con 24 colores)
        start = random.randint(0, len(full_pattern) - 1)
    
    rotated_pattern = full_pattern[start:] + full_pattern[:start]
    rotated_pattern = rotated_pattern[:number_colors]
    
    # Convertir patrón a colores y colores de texto
    colors = []
    text_colors = []
    
    for f, i in rotated_pattern:
        family = color_families[f]
        intensity = intensities[i]
        colors.append(c.COLOR_PALETTE[family][intensity])
        text_colors.append(_get_text_color(family, intensity))
    
    return colors, text_colors


def get_color_palette(number_colors):
    n = 30
    palette = sns.color_palette("husl", n_colors=n)
    random.shuffle(palette)
    palette = palette[:number_colors]
    return palette