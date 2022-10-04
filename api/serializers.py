from core.models import Stock, StockPrice, StockOrderHistory
from portfolio.models import Portfolio, StocksOwned
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from django.contrib.auth.models import User


class PortfolioSerializer(ModelSerializer):

    total_account_value = SerializerMethodField()
    total_portfolio_value = SerializerMethodField()
    stocks_owned = SerializerMethodField()
    user = SerializerMethodField()

    class Meta:
        model = Portfolio
        fields = '__all__'

    @staticmethod
    def get_total_account_value(obj):
        return obj.total_account_value

    @staticmethod
    def get_total_portfolio_value(obj):
        return obj.total_portfolio_value

    @staticmethod
    def get_stocks_owned(obj):
        return obj.stocks_owned

    @staticmethod
    def get_user(obj):
        return {
            'username': obj.user.username,
            'email': obj.user.email,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name
        }

