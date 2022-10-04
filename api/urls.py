from django.urls import path
from .views import StockOrderView, GenerateDummyStockData, ReturnPortfolio

urlpatterns = [
    path('stock-order/', StockOrderView.as_view(), name='stock-order'),
    path('generate-dummy-stock-data/', GenerateDummyStockData.as_view(), name='generate-dummy-stock-data'),
    path('return-portfolio/<int:user_id>/', ReturnPortfolio.as_view(), name='return-portfolio'),
]
