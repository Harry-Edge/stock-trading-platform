from django.urls import path
from .consumers import ReturnStockDataConsumer

websocket_urlpatterns = [
    path('ws/return-stock-data/', ReturnStockDataConsumer.as_asgi()),
]