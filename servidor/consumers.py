"""
Channels version of views.py, can be used to replace the old views.py
They can iniciate request from the server to the client
"""

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json
import logging
from urllib.parse import parse_qs
from . import main_views
from .games.gunman import gunman_views
from .games.roulette import roulette_views
from .games.socks import socks_views
from .games.flare_curse.flare_curse_engine import (
    ROOM_GROUP_NAME,
    flare_curse_engine,
    get_player_group_name,
)


logger = logging.getLogger(__name__)


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
        main_views.main_controller_.get_players_lock().acquire()
        print('A player has interacted')
        game_id = main_views.main_controller_.get_ready_to_join_game() # Get the game id
        print('game_id', game_id)
        if game_id == 0: # Roulette
            # Check if the player is the last one remaining
            if roulette_views.roulette_game.get_remaining_interactions() == 0:
                self.send_last_player()
        elif game_id == 2 or game_id == 4: # Palabrazo or BNumber
            self.notify_admin_update()
        elif game_id == 3: # Gunman
            if gunman_views.gunman_game.get_remaining_interactions() == 0:
                self.send_last_player()
        elif game_id == 5: # Socks
            if socks_views.socks_game.get_remaining_interactions() == 0:
                self.send_last_player()
        
        main_views.main_controller_.get_players_lock().release()

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


    def notify_admin_update(self):
        """
        Broadcasts a message that the admin can interpret as “Update needed.”
        """
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'admin_update_needed'
            }
        )

    # This function must match the 'type' in group_send above
    def admin_update_needed(self, event):
        """
        Sends a minimal JSON saying “admin_update_needed”: true
        """
        self.send(text_data=json.dumps({
            'admin_update_needed': True
        }))


class FlareCurseRoom(WebsocketConsumer):
    """
    Dedicated socket room for Flare Curse.
    - Player actions are sent here.
    - The server periodically pushes game events from its own loop.
    """

    def connect(self):
        query_params = parse_qs(self.scope.get('query_string', b'').decode())
        names = query_params.get('name', [])
        self.player_name = names[0] if names else None
        logger.info('FlareCurse connect player=%s', self.player_name)

        # Everyone joins the game room to receive broadcasts.
        async_to_sync(self.channel_layer.group_add)(
            ROOM_GROUP_NAME,
            self.channel_name,
        )

        # Players also join a personal group for private events.
        if self.player_name:
            async_to_sync(self.channel_layer.group_add)(
                get_player_group_name(self.player_name),
                self.channel_name,
            )

        self.accept()

        try:
            started = flare_curse_engine.ensure_started()
        except Exception:
            logger.exception('FlareCurse ensure_started failed player=%s', self.player_name)
            self._send_internal_error()
            return

        if not started:
            self.send(text_data=json.dumps({
                'type': 'Error',
                'message': 'Flare Curse no esta listo en este momento.'
            }))
            return

        if self.player_name:
            self._send_snapshot_to_self()

    def disconnect(self, close_code):
        logger.info('FlareCurse disconnect player=%s code=%s', self.player_name, close_code)
        async_to_sync(self.channel_layer.group_discard)(
            ROOM_GROUP_NAME,
            self.channel_name,
        )

        if self.player_name:
            async_to_sync(self.channel_layer.group_discard)(
                get_player_group_name(self.player_name),
                self.channel_name,
            )

    def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            self.send(text_data=json.dumps({'type': 'Error', 'message': 'Mensaje JSON invalido.'}))
            return

        action = data.get('action')
        if action is None:
            self.send(text_data=json.dumps({'type': 'Error', 'message': 'Accion no indicada.'}))
            return

        # Read-only snapshot request.
        if action == 'GetJugadores':
            if not self._require_player_name():
                return
            self._send_snapshot_to_self()
            return

        # Actions below require player identity.
        if not self._require_player_name():
            return

        if action == 'PedirDestello':
            color = data.get('color')
            try:
                accepted = flare_curse_engine.claim_flare(self.player_name, color)
            except Exception:
                logger.exception('FlareCurse PedirDestello failed player=%s color=%s', self.player_name, color)
                self._send_internal_error()
                return

            self.send(text_data=json.dumps({
                'type': 'PedirDestelloResult',
                'accepted': accepted,
                'color': color,
            }))
            self._send_snapshot_to_self()

        elif action == 'LanzarDestello':
            try:
                accepted = flare_curse_engine.launch_flare(self.player_name)
            except Exception:
                logger.exception('FlareCurse LanzarDestello failed player=%s', self.player_name)
                self._send_internal_error()
                return

            self.send(text_data=json.dumps({
                'type': 'LanzarDestelloResult',
                'accepted': accepted,
            }))
            self._send_snapshot_to_self()

        elif action == 'LanzarDestelloFantasma':
            try:
                in_time, points, cooldown = flare_curse_engine.launch_ghost_flare(self.player_name)
            except Exception:
                logger.exception('FlareCurse LanzarDestelloFantasma failed player=%s', self.player_name)
                self._send_internal_error()
                return

            self.send(text_data=json.dumps({
                'type': 'LanzarDestelloFantasmaResult',
                'in_time': in_time,
                'points': points,
                'cooldown_seconds': cooldown,
            }))
            self._send_snapshot_to_self()

        elif action == 'Maldecir':
            target = data.get('target')
            try:
                accepted, victim_is_enemy, cursed_player = flare_curse_engine.cast_curse(self.player_name, target)
            except Exception:
                logger.exception('FlareCurse Maldecir failed player=%s target=%s', self.player_name, target)
                self._send_internal_error()
                return

            self.send(text_data=json.dumps({
                'type': 'MaldecirResult',
                'accepted': accepted,
                'victim_is_enemy': victim_is_enemy,
                'cursed_player': cursed_player,
            }))
            self._send_snapshot_to_self()

        else:
            logger.warning('FlareCurse unsupported action=%s player=%s', action, self.player_name)
            self.send(text_data=json.dumps({'type': 'Error', 'message': 'Accion no soportada.'}))

    def flare_curse_event(self, event):
        self.send(text_data=json.dumps(event['payload']))

    def _require_player_name(self):
        if self.player_name:
            return True
        self.send(text_data=json.dumps({'type': 'Error', 'message': 'Este socket necesita un nombre de jugador.'}))
        return False

    def _send_snapshot_to_self(self):
        try:
            snapshot = flare_curse_engine.get_snapshot_for_player(self.player_name)
        except Exception:
            logger.exception('FlareCurse snapshot failed player=%s', self.player_name)
            self._send_internal_error()
            return

        self.send(text_data=json.dumps(snapshot))

    def _send_internal_error(self):
        self.send(text_data=json.dumps({'type': 'Error', 'message': 'Error interno de Flare Curse.'}))


