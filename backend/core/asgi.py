# backend/core/asgi.py
"""
ASGI config for core project.
Upgraded to handle both HTTP and WebSocket connections.
"""

import os
from django.core.asgi import get_asgi_application

# Must set Django settings before importing Channels
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django_asgi_app = get_asgi_application()

# Now import Channels components
from channels.routing import ProtocolTypeRouter, URLRouter
from direct_chat.routing import websocket_urlpatterns
from direct_chat.middleware import JWTAuthMiddlewareStack

application = ProtocolTypeRouter({
    # HTTP requests → Django's traditional request/response
    "http": django_asgi_app,
    
    # WebSocket requests → Django Channels
    "websocket": JWTAuthMiddlewareStack(  # Removed AllowedHostsOriginValidator for testing
        URLRouter(websocket_urlpatterns)
    ),
})