"""
Channels version of views.py, can be used to replace the old views.py
They can iniciate request from the server to the client
"""

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json
from . import main_controller


""" 
Inherit from WebsocketConsumer
It represents a wait room where clients will be waiting 
for the admin to join and tell them to go to certain game
"""
class WaitRoom(WebsocketConsumer):
    
    """
    Initial connection to the wait room (done by clients and admin)
    It will add every user to the wait room group
    """
    def connect(self):
        self.join_wait_room()
        self.accept()

    def disconnect(self, close_code):
        self.close()

    """
    This will only be called by admin and will send the game to all the clients in the wait room
    """
    def receive(self, text_data):
        game_id = json.loads(text_data)['game_id']
        self.send_game(game_id) # Send the redirect to all the clients

    # Adds the user to the wait room group
    def join_wait_room(self):
        self.room_group_name = 'wait_room'
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

    """ 
    Group send to all the clients in the wait room
    It calls the function send_game_type with the game_id as parameter
    """ 
    def send_game(self, game_id):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'send_game_type',
                'game_id': game_id 
            }
        )

    # Send the redirect to all the clients (necessary to be a function to be called by group_send)
    def send_game_type(self, event):
        game_id = event['game_id']
        self.send(text_data=json.dumps({
            'game_id': game_id
        }))


"""
Class to represent a playing room inside a game with the players and the admin
When a player interacts the server will check if it was the last one remaining
If it is the last one, it will inform the admin to proceed
"""
class InGameRoom(WebsocketConsumer):
    """
    Initial connection to the wait room (done by clients and admin)
    It will add every user to the players room group
    """
    def connect(self):
        self.join_room()
        self.accept()

    """
    When a player interacts with the game it will disconnect from the room
    """
    def disconnect(self, close_code):
        self.close()

    """
    This will only be called by clients and will check if it was the last one remaining
    In case it was, it will inform the admin to proceed
    """
    def receive(self, text_data):
        print('A player has interacted')
        # Check if the player is the last one remaining
        if main_controller.get_remaining_interactions() == 0:
            self.send_last_player()

    # Adds the user to the room group
    def join_room(self):
        self.room_group_name = 'in_game_room'
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

    """
    It will inform to the admin that the last player has interacted
    (players will ignore this message)
    """
    def send_last_player(self):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'send_last_player_type',
            }
        )
    
    # Send the redirect to the admin (necessary to be a function to be called by send_last_player)
    def send_last_player_type(self, event):
        self.send(text_data=json.dumps({
            'last_player': True
        }))


