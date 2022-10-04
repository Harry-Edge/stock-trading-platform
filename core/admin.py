from django.contrib import admin
from .models import Stock, StockExchange, StockPrice, StockOrderHistory


@admin.register(StockExchange)
class StockExchangeAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'currency', 'website')
    search_fields = ('name', 'country', 'currency', 'website')


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'name', 'exchange')
    search_fields = ('ticker', 'name', 'exchange__name')


@admin.register(StockPrice)
class StockPriceAdmin(admin.ModelAdmin):
    list_display = ('stock', 'price', 'datetime_created')
    search_fields = ('stock__ticker', 'stock__name', 'price')
    list_filter = ('stock', 'datetime_created')


@admin.register(StockOrderHistory)
class StockOrderHistoryAdmin(admin.ModelAdmin):
    list_display = ('stock', 'price_executed', 'datetime_created', 'order_type', 'profit')
    list_filter = ('stock', 'datetime_created')