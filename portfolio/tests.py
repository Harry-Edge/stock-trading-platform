from django.test import TestCase
from .models import Portfolio, StocksOwned
from core.models import Stock, StockExchange, StockPrice
from django.contrib.auth.models import User
import decimal


class PortfolioTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='testuser', password='12345')
        Portfolio.objects.create(user=user, free_cash=1000.00, currency='GBP')

    def test_portfolio_creation(self):
        portfolio = Portfolio.objects.get(user__username='testuser')
        self.assertEqual(portfolio.free_cash, 1000.00)
        self.assertEqual(portfolio.currency, 'GBP')

    def test_portfolio_total_value(self):
        portfolio = Portfolio.objects.get(user__username='testuser')
        self.assertEqual(portfolio.total_portfolio_value, 0)
        self.assertEqual(portfolio.total_account_value, 1000.00)

    def test_get_total_account_value(self):
        portfolio = Portfolio.objects.get(user__username='testuser')
        self.assertEqual(portfolio.total_account_value, 1000.00)


class StocksOwnedTestCase(TestCase):
    def setUp(self) -> None:
        user = User.objects.create_user(username='testuser', password='12345')
        portfolio = Portfolio.objects.create(user=user, free_cash=1000.00, currency='GBP')
        stock_exchange = StockExchange.objects.create(name='NASDAQ', country='US', currency='USD', )
        stock = Stock.objects.create(ticker='AAPL', name='Apple Inc.', description='Apple Inc.',
                                     market_cap=1000, exchange=stock_exchange)
        StocksOwned.objects.create(portfolio=portfolio, stock=stock, quantity=10, average_price=100.00)
        StockPrice.objects.create(stock=stock, price=100.00)

    def test_total_value_of_investment(self):
        stock = StocksOwned.objects.get(portfolio=Portfolio.objects.get(user__username='testuser'), stock__ticker='AAPL')
        self.assertEqual(stock.total_value_of_investment, 1000.00)

    def test_return_new_average_price(self):
        stock = StocksOwned.objects.get(portfolio=Portfolio.objects.get(user__username='testuser'))
        self.assertEqual(stock.return_new_average_price(10, decimal.Decimal(110)), 105.00)
        self.assertEqual(stock.return_new_average_price(20, decimal.Decimal(130)), 120.00)

    def test_add_stock_owned(self):
        portfolio = Portfolio.objects.get(user__username='testuser')

        stock_owned = StocksOwned.objects.get(portfolio=portfolio, stock__ticker='AAPL')
        stock_owned.update_stock_owned(10, decimal.Decimal(110))
        self.assertEqual(stock_owned.quantity, 20)
        self.assertEqual(stock_owned.average_price, 105.00)

    def test_remove_stock_owned(self):
        portfolio = Portfolio.objects.get(user__username='testuser')
        stock_owned = StocksOwned.objects.get(portfolio=portfolio, stock__ticker='AAPL')
        stock_owned.update_stock_owned(-5, decimal.Decimal(110))
        self.assertEqual(stock_owned.quantity, 5)
        self.assertEqual(stock_owned.average_price, 100)