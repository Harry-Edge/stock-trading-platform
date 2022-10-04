from django.contrib import admin
from .models import Portfolio, StocksOwned


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('user', 'free_cash', 'currency')
    search_fields = ('user__username', 'free_cash', 'currency')


@admin.register(StocksOwned)
class StocksOwnedAdmin(admin.ModelAdmin):
    list_display = ('portfolio', 'stock', 'quantity', 'average_price')
    search_fields = ('portfolio__user__username', 'stock__ticker', 'stock__name', 'quantity', 'average_price')
    list_filter = ('portfolio', 'stock')
