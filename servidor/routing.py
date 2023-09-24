"""
Route consumers, channels version of urls.py
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/wait_room/', consumers.WaitRoom.as_asgi()),
    re_path(r'ws/in_game_room/', consumers.InGameRoom.as_asgi()),
]