"""
ASGI config for kumss_erp project.

It exposes the ASGI callable as a module-level variable named ``application``.

WebSocket support has been replaced with Server-Sent Events (SSE) + Redis Pub/Sub
for better scalability and simpler deployment.
"""

import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kumss_erp.settings.development')
django.setup()

# Standard ASGI application (SSE works over HTTP)
application = get_asgi_application()

# Old WebSocket configuration (commented out - using SSE now)
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# from channels.security.websocket import AllowedHostsOriginValidator
# import apps.communication.routing
# from apps.communication.middleware import TokenAuthMiddleware
#
# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": AllowedHostsOriginValidator(
#         AuthMiddlewareStack(
#             TokenAuthMiddleware(
#                 URLRouter(
#                     apps.communication.routing.websocket_urlpatterns
#                 )
#             )
#         )
#     ),
# })
