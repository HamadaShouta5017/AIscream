import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.sessions import SessionMiddlewareStack
from django.core.asgi import get_asgi_application
from transcriber.routing import websocket_urlpatterns
from django.conf import settings
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whisper_project.settings')

# HTTP アプリケーション（開発中は静的ファイルも配信）
http_app = get_asgi_application()
if settings.DEBUG:
    http_app = ASGIStaticFilesHandler(http_app)

# ProtocolTypeRouter に渡す
application = ProtocolTypeRouter({
    "http": http_app,
    "websocket": SessionMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
