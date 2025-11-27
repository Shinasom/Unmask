# backend/direct_chat/routing.py
"""
WebSocket URL routing for chat feature.
"""

from django.urls import re_path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r'^ws/chat/$', ChatConsumer.as_asgi()),
]# backend/direct_chat/routing.py
"""
WebSocket URL routing for chat feature.
"""

from django.urls import re_path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r'^ws/chat/$', ChatConsumer.as_asgi()),
]