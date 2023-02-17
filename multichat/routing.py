from django.urls import path

from chat.consumers import ChatConsumer


websocket_urlpatterns = [
    path("chat/stream/", ChatConsumer.as_asgi()),
]