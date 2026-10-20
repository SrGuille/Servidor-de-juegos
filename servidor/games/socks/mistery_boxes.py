""" Mistery boxes game: 
n players -> floor(n * 0.25) bad boxes, floor(n * 0.25) good boxes, floor(n * 0.5) long boxes.
Min prize: x0.3. Max prize: x2
25% bad boxes. prizes: [0.3,0.8]-[1.1,1.3]
25% good boxes. prob: [0.7,0.9]-[1.5,2]
50% long boxes. prob: [0.3,0.8]-[1.5,2]

"""

import random
import time
import os
clear = lambda: os.system('cls')

bad = ((0.3, 0.8), (1.1, 1.3))
percentage_bad = 0.25
good = ((0.7, 0.9), (1.5, 2))
percentage_good = 0.25
long = ((0.3, 0.8), (1.5, 2))
percentage_long = 0.5

class Box:
    def __init__(self, min, max):
        self.min = min
        self.max = max
        self.multiplicator = None
        self.bets = []

    def set_multiplicator(self):
        self.multiplicator = random.uniform(self.min, self.max)

    def add_bet(self, bet):
        self.bets.append(bet)

    def clear_bets(self):
        self.bets = []

    def __str__(self):
        return f"prizes x[min: {self.min:.2f}, max: {self.max:.2f}]"
    
class PlayerBet:
    def __init__(self, player_id, box_id, bet_amount):
        self.player_id = player_id
        self.box_id = box_id
        self.bet_amount = bet_amount
    
class Player:
    def __init__(self, player_id, coins):
        self.player_id = player_id
        self.coins = coins
        self.bet = None

    def set_bet(self, bet):
        self.bet = bet

    def __str__(self):
        return f"Player {self.player_id} has coins: {self.coins}"

n = 3 # number of players
m = 3 # number of boxes

def create_boxes(n):
    boxes = []
    """
    n_bad = int(n * percentage_bad) # Truncate numbers
    n_good = int(n * percentage_good)
    n_long = int(n * percentage_long)
    """

    n_bad = 1
    n_good = 1
    n_long = 1

    for _ in range(n_bad):
        boxes.append(create_box("bad"))
    for _ in range(n_good):
        boxes.append(create_box("good"))
    for _ in range(n_long):
        boxes.append(create_box("long"))

    # Shuffle the boxes to randomize their order
    random.shuffle(boxes)

    return boxes

def create_box(type):
    if type == "bad":
        min = random.uniform(*bad[0]) # unpacks the tuple
        max = random.uniform(*bad[1])
    elif type == "good":
        min = random.uniform(*good[0])
        max = random.uniform(*good[1])
    elif type == "long":
        min = random.uniform(*long[0])
        max = random.uniform(*long[1])
    else:
        raise ValueError("Invalid box type")
    return Box(min, max)

def game_loop():
    initial_coins = 100
    rounds = 5
    boxes = create_boxes(n)
    names = ["Guille", "Isa", "Nayla"]
    players = [Player(names[i], initial_coins) for i in range(n)]
    print("Welcome to the Mystery Boxes Game!")
   
    for i in range(rounds):
        print(f"Round {i+1} of {rounds}")
        for box in boxes:
            box.set_multiplicator()
        for player in players:
            successful = False
            while not successful:
                print(f"{player.player_id}, choose a box (1-{len(boxes)}):")
                choice = int(input()) - 1
                if choice < 0 or choice >= n:
                    print("Invalid choice, try again.")
                    continue
                bet_amount = int(input(f"{player.player_id}, enter your bet amount: "))
                if bet_amount <= 0 or bet_amount > player.coins:
                    print("Invalid bet amount, try again.")
                    continue
                successful = True
                bet = PlayerBet(player.player_id, choice, bet_amount)
                player.set_bet(bet)
                boxes[choice].add_bet(bet)
                player.coins -= bet_amount
                clear()
        
        print("All players have placed their bets.")

        for i in range(5, 0, -1):
            print(f"Deja de mirar en {i}")
            time.sleep(1)
        clear()
        time.sleep(1)
        
        for player in players:
            bet = player.bet
            box = boxes[bet.box_id]
            prize = round(bet.bet_amount * box.multiplicator)
            player.coins += prize
            print(f"{player.player_id} ({bet.bet_amount} -> {prize} in box {boxes.index(box)+1}).")

            for i in range(5, 0, -1):
                print(f"Deja de mirar en {i}")
                time.sleep(1)
            clear()
            time.sleep(1)
            
        for box in boxes:
            string = f"Box {boxes.index(box)+1}:"
            for bet in box.bets:
                string += f" {bet.player_id}"
            print(string)
            box.clear_bets()
    
    for player in players:
        print(player)

    for i, box in enumerate(boxes):
        print(f"Box {i+1}: {box}")

if __name__ == "__main__":
    game_loop()