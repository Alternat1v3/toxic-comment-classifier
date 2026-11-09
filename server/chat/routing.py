from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # One socket per conversation; the other side is the signed-in user (from the session cookie).
    re_path(r"^ws/chat/(?P<username>[\w.@+-]+)/$", consumers.ChatConsumer.as_asgi()),
]
