from django.urls import path, re_path
from . import consumers

websocket_urlpatterns = [
    path('ws/as_mail/<str:email>/', consumers.AsyncMailConsumer.as_asgi()),
]
