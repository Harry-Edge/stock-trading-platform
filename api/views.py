from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.models import Stock, StockPrice, StockOrderHistory
from portfolio.models import Portfolio, StocksOwned
from rest_framework.permissions import AllowAny
import json
import decimal
import random
from datetime import datetime, timedelta
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .serializers import PortfolioSerializer
import time


class StockOrderView(APIView):
    permission_classes = (AllowAny,)

    class StockOrder:
        def __init__(self, user_id: int, stock_id: int, quantity: int) -> None:
            self.portfolio = Portfolio.objects.get(user_id=user_id)
            self.stock = Stock.objects.filter(id=stock_id)

            if self.stock.exists():
                self.stock = self.stock.first()
            else:
                raise Exception('Stock Does Not Exist')

            self.quantity = decimal.Decimal(quantity)
            self.latest_price = decimal.Decimal(self.stock.get_latest_price())

        def check_if_stock_already_owned(self) -> StocksOwned or None:
            try:
                stock_owned = StocksOwned.objects.get(portfolio=self.portfolio, stock=self.stock)
                return stock_owned
            except StocksOwned.DoesNotExist:
                return None

        def update_stock_owned(self, stock_owned: StocksOwned) -> None:
            """
            If the stock is already owned, we need to update the average price, and quantity owned
            """
            stock_owned.update_stock_owned(new_quantity=int(self.quantity), price_purchased=self.latest_price)

        def add_new_stock_owned(self) -> None:
            StocksOwned.objects.create(
                portfolio=self.portfolio,
                stock=self.stock,
                quantity=self.quantity,
                average_price=self.latest_price
            )

        def remove_cash_from_portfolio(self, amount: decimal.Decimal) -> None:
            self.portfolio.free_cash -= amount
            self.portfolio.save()

        def add_cash_to_portfolio(self, amount: decimal.Decimal) -> None:
            self.portfolio.free_cash += amount
            self.portfolio.save()

        def add_stock_order_history(self, order_type: str) -> None:
            """
            Add the order to the stock order history
            param order_type: Buy or Sell
            :return: None
            """
            StockOrderHistory.objects.create(
                user=self.portfolio.user,
                stock=self.stock,
                quantity=self.quantity,
                order_type=order_type,
                price_executed=self.latest_price
            )

        def execute_buy_order(self) -> (bool, dict):
            """
            Execute the order by checking if the portfolio has enough cash to buy the stock/s
            if so then update the portfolio and the stock/s owned if the stock is already owned,
            if not then create a new stock owned record
            """
            if self.portfolio.check_portfolio_has_enough_funds_for_purchase(self.latest_price * self.quantity):
                stock_already_owned = self.check_if_stock_already_owned()
                if stock_already_owned:
                    self.update_stock_owned(stock_already_owned)
                else:
                    self.add_new_stock_owned()
                self.remove_cash_from_portfolio(self.latest_price * self.quantity)
                self.add_stock_order_history(order_type='buy')
                return True, {'message': f'{self.stock.name} Buy Order Executed'}
            else:
                return False, {'message': 'Insufficient Funds'}

        def execute_sell_order(self) -> (bool, dict):
            """
               Execute the order by checking if the portfolio has enough stock/s to sell
               if so then update the portfolio and the stock/s owned if the stock is already owned,
               if not then create a new stock owned record
            """
            stock_already_owned = self.check_if_stock_already_owned()
            if stock_already_owned:
                if stock_already_owned.quantity >= self.quantity:
                    stock_already_owned.update_stock_owned(new_quantity=-self.quantity, price_purchased=self.latest_price)
                    self.add_cash_to_portfolio(self.latest_price * self.quantity)
                    self.add_stock_order_history(order_type='sell')
                    return True, {'message': f'{self.stock.name} Sell Order Executed'}
                else:
                    return False, {'message': 'Insufficient Stock Quantity'}
            else:
                return False, {'message': 'Stock Not Owned'}

    @staticmethod
    def check_post_data(data: dict) -> list:
        """
        Check the post data to make sure it is valid
        """
        if 'stock_id' not in data or 'quantity' not in data or 'order_type' not in data or 'user_id' not in data:
            return []
        else:
            return [data['stock_id'], data['quantity'], data['order_type'], data['user_id']]

    def post(self, request) -> Response:

        data = self.check_post_data(request.data)

        time.sleep(2)

        if data:
            stock_id, quantity, order_type, user_id = data

            execute_order = self.StockOrder(user_id, stock_id, quantity)

            successful, response = execute_order.execute_buy_order() \
                if order_type == 'buy' else execute_order.execute_sell_order()

            if successful:
                return Response(response, status=status.HTTP_201_CREATED)
            else:
                if response['message'] == 'Insufficient Funds':
                    return Response(response, status=status.HTTP_200_OK)

                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'Invalid Post Data'}, status=status.HTTP_400_BAD_REQUEST)


class ReturnPortfolio(APIView):
    """
    Return the portfolio for the user
    """

    def get(self, request, user_id) -> Response:
        portfolio = Portfolio.objects.filter(user_id=user_id)

        if portfolio.exists():
            portfolio_serializer = PortfolioSerializer(portfolio.first())
            return Response(portfolio_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Portfolio Does Not Exist'}, status=status.HTTP_400_BAD_REQUEST)


class GenerateDummyStockData(APIView):
    permission_classes = (AllowAny,)

    @staticmethod
    def get(request):

        stocks = Stock.objects.all()

        for stock in stocks:

            current_price = stock.get_latest_price()
            new_price = current_price

            if random.randint(1, 3) != 1:
                # So 30% the price will remain the same
                new_price = float(current_price) * (1 + (random.randint(1, 5) / 1000))

            StockPrice.objects.create(
                stock=stock,
                price=decimal.Decimal(new_price)
            )

            # convert new_price to two decimal places
            new_price = decimal.Decimal(new_price).quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN)

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'stock_data',
                {'stock_prices': [{
                    'type': 'send_stock_data',
                    'stock_id': stock.id,
                    'price': float(
                        decimal.Decimal(new_price).quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_DOWN)
                        ),
                    'time': datetime.now().strftime('%H:%M:%S')}]
                }
            )

        return Response({'response': 'ok'}, status=status.HTTP_201_CREATED)
