import os
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import random
import numpy as np

START_ANGLE = 90
COUNTERCLOCK = False
LABEL_DISTANCE = 0.95
ROTATE_LABELS = True
matplotlib.rcParams['font.family'] = 'Arial'
matplotlib.rcParams['font.size'] = 10

# Creates the players roulette image with players with coins
def create_players_roulette(players):
    labels = []
    sizes = []

    for player in players.values():
        if(player.coins > 0): # If player has coins
            labels.append(player.nick)
            sizes.append(player.coins)

    sizes = np.array(sizes)
    color_palette = get_color_palette(len(labels))

    print(labels)
    print(sizes)

    create_roulette_image(labels, sizes, color_palette, 'players_roulette')

# Creates the prizes roulette image with available prizes
def create_prizes_roulette(prizes):
    labels = []
    sizes = []

    for prize in prizes.values():
        if(prize.amount > 0): # If there are prizes of this type
            label = prize.type.replace("Regalo", "R.")
            labels.append(label)
            sizes.append(prize.prob)

    sizes = np.array(sizes)
    color_palette = get_color_palette(len(labels))

    create_roulette_image(labels, sizes, color_palette, 'prizes_roulette')

# Creates the roulette image (first delete it if it exists)
def create_roulette_image(labels, sizes, color_palette, filename):
    _, texts = plt.pie(sizes, labels=labels, colors=color_palette, 
                       startangle=START_ANGLE, counterclock = COUNTERCLOCK, 
                       labeldistance=LABEL_DISTANCE, rotatelabels=ROTATE_LABELS)
    
    # Adjust distance between labels and pie to put the labels inside the pie 
    for t in texts:
        t.set_ha('right' if t.get_ha() == 'left' else 'left')
        t.set_va('top' if t.get_va() == 'bottom' else 'bottom')

    if(os.path.exists(f'servidor/static/img/{filename}.png')):
        os.remove(f'servidor/static/img/{filename}.png')
    plt.savefig(f'servidor/static/img/{filename}.png', transparent=True, dpi=150, bbox_inches='tight')
    plt.close()

def get_color_palette(number_colors):
    n = 30
    palette = sns.color_palette("husl", n_colors=n)
    random.shuffle(palette)
    palette = palette[:number_colors]
    return palette