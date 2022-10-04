from django.test import TestCase
from .models import StockExchange, Stock, StockOrderHistory, StockPrice
from django.contrib.auth.models import User
from portfolio.models import Portfolio, StocksOwned


def create_dummy_user_portfolio_stock() -> (User, Portfolio, Stock):
    """
    Creates generic user, portfolio, stock, stock price, stock exchange
    so we can test as this data is required for the most tests
    """

    test_user = User.objects.create_user(username='testuser', password='12345')
    test_portfolio = Portfolio.objects.create(user=test_user, free_cash=1000, currency='GBP')
    test_stock_exchange = StockExchange.objects.create(name='NASDAQ', country='US', currency='USD')
    test_stock = Stock.objects.create(
        ticker='AAPL', name='Apple Inc.', description='Apple Inc.', market_cap=1000, exchange=test_stock_exchange
    )
    StockPrice.objects.create(stock=test_stock, price=100)

    return test_user, test_portfolio, test_stock


def delete_dummy_user_portfolio_stock() -> None:
    """
    Deletes generic user, portfolio, stock, stock price, stock exchange
    so we can test as this data is required for the most tests
    """

    User.objects.all().delete()
    Portfolio.objects.all().delete()
    Stock.objects.all().delete()
    StockPrice.objects.all().delete()
    StockExchange.objects.all().delete()


class StockTestCase(TestCase):
    def setUp(self):
        self.test_user, self.test_portfolio, self.test_stock = create_dummy_user_portfolio_stock()

    def test_get_latest_price(self):
        self.assertEqual(self.test_stock.get_latest_price(), 100)

    def test_return_investment_for_user_if_applicable(self):
        self.assertEqual(self.test_stock.return_investment_for_user_if_applicable(self.test_user), None)
        StocksOwned.objects.create(portfolio=self.test_portfolio, stock=self.test_stock, quantity=10, average_price=100)
        self.assertEqual(self.test_stock.return_investment_for_user_if_applicable(self.test_user).quantity, 10)

    def tearDown(self) -> None:
        delete_dummy_user_portfolio_stock()