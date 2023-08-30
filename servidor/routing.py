"""
Route consumers, channels version of urls.py
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/wait_room/', consumers.WaitRoom.as_asgi()) 
]