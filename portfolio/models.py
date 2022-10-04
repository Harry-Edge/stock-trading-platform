import decimal
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from core.models import Stock
from core.models import StockOrderHistory


class Portfolio(models.Model):

    CURRENCY_CHOICES = (
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('GBP', 'GBP'),
        ('JPY', 'JPY')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    free_cash = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='GBP')

    def __str__(self) -> str:
        return f'{self.user.username}\'s Portfolio'

    @property
    def total_portfolio_value(self) -> float:
        total_portfolio_value = 0
        for stock in self.stocksowned_set.all():
            total_portfolio_value += stock.total_value_of_investment
        return total_portfolio_value

    @property
    def total_account_value(self) -> float:
        return self.total_portfolio_value + float(self.free_cash)

    @property
    def current_portfolio_return(self):
        total_portfolio_return = 0
        for stock in self.stocksowned_set.all():
            total_portfolio_return += stock.stock.get_latest_price() * stock.quantity
        return total_portfolio_return

    @property
    def total_invested(self) -> float:
        all_stock_orders = StockOrderHistory.objects.filter(user=self.user)
        total_invested = 0
        for stock_order in all_stock_orders:
            if stock_order.order_type == 'buy':
                total_invested += stock_order.price_executed * stock_order.quantity
            elif stock_order.order_type == 'sell':
                total_invested -= stock_order.price_executed * stock_order.quantity
        return total_invested

    @property
    def stocks_owned(self) -> list:
        stocks_owned = []
        for stock in self.stocksowned_set.all():
            stocks_owned.append(stock)
        return stocks_owned

    def check_portfolio_has_enough_funds_for_purchase(self, amount: float) -> bool:
        if float(self.free_cash) >= amount:
            return True
        return False

    def add_portfolio_cash(self, amount: float):
        self.free_cash = Decimal(self.free_cash) + Decimal(amount)
        self.save()

    def remove_portfolio_cash(self, amount: float):
        self.free_cash = Decimal(self.free_cash) - Decimal(amount)
        self.save()


class StocksOwned(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    average_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        return f'{self.stock} - {self.quantity} @ {self.average_price}'

    class Meta:
        verbose_name_plural = 'Stocks Owned'

    @property
    def total_value_of_investment(self) -> float:
        return self.quantity * float(self.stock.get_latest_price())

    def return_new_average_price(self, new_quantity: int, price_purchased: Decimal) -> Decimal:
        total_inventory_value = self.quantity * self.average_price
        new_average_price = (total_inventory_value + (price_purchased * new_quantity)) / (self.quantity + new_quantity)
        return new_average_price

    def update_stock_owned(self, new_quantity: int, price_purchased: Decimal) -> None:

        if new_quantity > 0:
            self.average_price = self.return_new_average_price(new_quantity, price_purchased)
        self.quantity += new_quantity
        self.save()

        if self.quantity == 0:
            self.delete()


