# stocks/admin.py

from django.contrib import admin
from .models import Stock, Basket, BasketItem


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'name', 'current_price', 'last_updated']
    search_fields = ['symbol', 'name']
    list_filter = ['last_updated']
    ordering = ['symbol']


class BasketItemInline(admin.TabularInline):
    model = BasketItem
    extra = 0
    readonly_fields = ['quantity', 'purchase_price', 'allocated_amount']


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'investment_amount', 'created_at', 'get_current_value', 'get_profit_loss']
    search_fields = ['name', 'description', 'user__email']
    list_filter = ['created_at', 'user']
    ordering = ['-created_at']
    inlines = [BasketItemInline]

    def get_current_value(self, obj):
        return f"₹{obj.get_total_value():,.2f}"

    get_current_value.short_description = 'Current Value'

    def get_profit_loss(self, obj):
        pl = obj.get_profit_loss()
        return f"₹{pl:,.2f}"

    get_profit_loss.short_description = 'P/L'


@admin.register(BasketItem)
class BasketItemAdmin(admin.ModelAdmin):
    list_display = ['basket', 'stock', 'weight_percentage', 'allocated_amount', 'quantity', 'purchase_price']
    list_filter = ['basket', 'purchase_date']
    search_fields = ['basket__name', 'stock__symbol']