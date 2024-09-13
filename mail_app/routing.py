from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/as_mail/', consumers.AsyncMailConsumer.as_asgi()),
]
