# Admin

from typing import List

def get_multibandits_info() -> List[List]:
    """
    For every multibandit:
        - List of last round players names that bet on it
        - List of historical number of players that bet on it
    """
    pass

def run_multibandits():
    pass

# Players

def get_num_multibandits() -> int:
    pass

def send_bet(player_name, multibandit_id, coins):
    # Go to the list of multibandits, find that one and add the player + bet
    # Substract player coins
    pass
    
def get_player_coins_and_new_coins(player_name) -> List[int]:
    pass


        