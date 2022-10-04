from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import StockOrderHistory, StockPrice


@receiver(post_save, sender=StockOrderHistory)
def calculate_return_investment(sender, instance, created, **kwargs):
    if created:
        if instance.order_type == 'sell':
            instance.calculate_profit()
