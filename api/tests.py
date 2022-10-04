from django.test import TestCase
from .views import StockOrderView
from django.contrib.auth.models import User
from core.models import Stock, StockOrderHistory, StockPrice, StockExchange
from portfolio.models import Portfolio, StocksOwned
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from core.tests import create_dummy_user_portfolio_stock, delete_dummy_user_portfolio_stock


class StockOrderViewBuyStockTest(TestCase):
    def setUp(self) -> None:
        self.user, self.portfolio, self.stock = create_dummy_user_portfolio_stock()
        self.buy_stock_object = StockOrderView.StockOrder(
            user_id=self.user.id, stock_id=self.stock.id, quantity=10
        )

    def test_check_if_stock_already_owned(self):
        self.assertIsNone(self.buy_stock_object.check_if_stock_already_owned())

    def test_update_stock_owned(self):
        self.buy_stock_object.add_new_stock_owned()

        new_stock_object = StockOrderView.StockOrder(
            user_id=self.user.id, stock_id=self.stock.id, quantity=10
        )

        new_stock_object.update_stock_owned(new_stock_object.check_if_stock_already_owned())
        self.assertEqual(StocksOwned.objects.get(portfolio=self.portfolio, stock=self.stock).quantity, 20)

    def test_add_new_stock_owned(self):
        bought, msg = self.buy_stock_object.execute_buy_order()
        self.assertTrue(bought)

    def tearDown(self) -> None:
        delete_dummy_user_portfolio_stock()


class StockOrderViewSellStockTest(TestCase):
    def setUp(self) -> None:
        self.user, self.portfolio, self.stock = create_dummy_user_portfolio_stock()
        self.buy_stock_object = StockOrderView.StockOrder(
            user_id=self.user.id, stock_id=self.stock.id, quantity=10
        )
        self.buy_stock_object.execute_buy_order()

    def test_sell_stock(self):
        sold, msg = self.buy_stock_object.execute_sell_order()
        self.assertTrue(sold)


class StockBuyOrderTest(APITestCase):
    def setUp(self) -> None:
        self.user, self.portfolio, self.stock = create_dummy_user_portfolio_stock()

    def test_buy_stock(self):
        response = self.client.post(reverse('stock-order'), data={
            'user_id': self.user.id,
            'stock_id': self.stock.id,
            'quantity': 10,
            'order_type': 'buy'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_buy_stock_not_enough_cash(self):
        self.portfolio.free_cash = 0
        self.portfolio.save()
        print('Free cash: ', self.portfolio.free_cash)

        response = self.client.post(reverse('stock-order'), data={
            'user_id': self.user.id,
            'stock_id': self.stock.id,
            'quantity': 10,
            'order_type': 'buy'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Insufficient Funds')

    def tearDown(self) -> None:
        delete_dummy_user_portfolio_stock()
