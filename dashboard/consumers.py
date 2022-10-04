import json
from channels.generic.websocket import WebsocketConsumer
import time
import random
import decimal
from core.models import StockPrice
import time
from asgiref.sync import async_to_sync


class ReturnStockDataConsumer(WebsocketConsumer):

    def __init__(self):
        super().__init__()

    def connect(self):

        self.room_group_name = 'stock_data'

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        print('disconnected')

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print(text_data_json)
        stock_ids = text_data_json['stockIDS']

        for i in range(1):
            time.sleep(1)
            stock_prices = []

            # check the socket is still open
            for stock_id in stock_ids:
                latest_stock_price = StockPrice.objects.filter(stock_id=stock_id).latest('datetime_created')
                stock_prices.append({
                    'stock_id': stock_id,
                    'name': latest_stock_price.stock.name,
                    'price': float(latest_stock_price.price),
                })

            self.send(text_data=json.dumps({
                'stock_prices': stock_prices
            }))
            #
            # response = requests.get('http://localhost:8000/api/v1/generate-dummy-stock-data/')
            # print(response.json())

    def send_stock_data(self, event, type='send_stock_data'):
        print('sending stock data')
        self.send(text_data=json.dumps(event))



