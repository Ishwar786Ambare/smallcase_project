# stocks/models.py

from django.db import models
from django.utils import timezone


class Stock(models.Model):
    """Model to store stock information"""
    symbol = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.symbol} - {self.name}"

    class Meta:
        ordering = ['symbol']


class Basket(models.Model):
    """Model to store stock baskets"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    investment_amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_total_value(self):
        """Calculate total current value of basket"""
        total = sum(item.get_current_value() for item in self.items.all())
        return total

    def get_profit_loss(self):
        """Calculate profit/loss"""
        current_value = self.get_total_value()
        return int(current_value) - int(self.investment_amount)

    def get_profit_loss_percentage(self):
        """Calculate profit/loss percentage"""
        if self.investment_amount > 0:
            return (self.get_profit_loss() / self.investment_amount) * 100
        return 0


class BasketItem(models.Model):
    """Model to store individual stocks in a basket with equal weight"""
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, related_name='items')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    weight_percentage = models.DecimalField(max_digits=5, decimal_places=2)  # Equal weight
    allocated_amount = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.DecimalField(max_digits=10, decimal_places=4)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.basket.name} - {self.stock.symbol}"

    def get_current_value(self):
        """Calculate current value of this stock in basket"""
        if self.stock.current_price:
            return float(self.quantity) * float(self.stock.current_price)
        return float(self.allocated_amount)

    def get_profit_loss(self):
        """Calculate profit/loss for this stock"""
        return self.get_current_value() - float(self.allocated_amount)

    class Meta:
        unique_together = ['basket', 'stock']
        ordering = ['stock__symbol']