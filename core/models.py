from django.db import models
from django.contrib.auth.models import User


class StockExchange(models.Model):

    COUNTRIES = (
        ('US', 'United States'),
        ('CA', 'Canada'),
        ('UK', 'United Kingdom'),
        ('DE', 'Germany')
    )

    CURRENCIES = (
        ('USD', 'US Dollar'),
        ('CAD', 'Canadian Dollar'),
        ('MXN', 'Mexican Peso'),
        ('GBP', 'British Pound'),
        ('EUR', 'Euro')
    )

    NAMES = (
        ('NYSE', 'New York Stock Exchange'),
        ('NASDAQ', 'NASDAQ'),
        ('TSX', 'Toronto Stock Exchange'),
        ('LSE', 'London Stock Exchange'),
        ('FWB', 'Frankfurt Stock Exchange')
    )

    name = models.CharField(max_length=100, choices=NAMES)
    country = models.CharField(max_length=2, choices=COUNTRIES)
    currency = models.CharField(max_length=100, choices=CURRENCIES)
    website = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Stock Exchanges'


class Stock(models.Model):
    ticker = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    description = models.TextField()
    market_cap = models.FloatField()
    open = models.FloatField(null=True)
    previous_close = models.FloatField(null=True)
    exchange = models.ForeignKey(StockExchange, on_delete=models.CASCADE)
    logo = models.ImageField(upload_to='stock_logos', blank=True)

    def __str__(self):
        return f'{self.ticker} - {self.name}'

    def get_latest_price(self) -> float:
        return self.stockprice_set.latest('datetime_created').price

    def return_investment_for_user_if_applicable(self, user: User):
        if self.stocksowned_set.filter(portfolio__user=user).exists():
            return self.stocksowned_set.get(portfolio__user=user)
        return None


class StockPrice(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    datetime_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.stock.ticker} - {self.price}'

    class Meta:
        verbose_name_plural = 'Stock Prices'
        ordering = ['-datetime_created', 'stock']


class StockOrderHistory(models.Model):

    TYPE_OPTIONS = (
        ('buy', 'Buy'),
        ('sell', 'Sell')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField()
    order_type = models.CharField(max_length=4, choices=TYPE_OPTIONS)
    datetime_created = models.DateTimeField(auto_now_add=True)
    price_executed = models.DecimalField(max_digits=10, decimal_places=2)
    profit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} - {self.stock.ticker} - {self.quantity} - {self.order_type}'

    class Meta:
        verbose_name_plural = 'Stock Order History'
        ordering = ['-datetime_created']

    def calculate_profit(self):
        self.profit = self.price_executed * self.quantity
        self.save()




