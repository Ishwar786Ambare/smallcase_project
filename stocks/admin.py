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


# ==========================================
# Chat Admin Configuration
# ==========================================

from .models import ChatGroup, ChatGroupMember, ChatMessage


class ChatGroupMemberInline(admin.TabularInline):
    model = ChatGroupMember
    extra = 1
    autocomplete_fields = ['user']


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ['sender', 'content', 'message_type', 'created_at', 'is_read']
    can_delete = False
    max_num = 10
    ordering = ['-created_at']
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ChatGroup)
class ChatGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'group_type', 'created_by', 'get_members_count', 'is_active', 'created_at']
    list_filter = ['group_type', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'created_by__email']
    ordering = ['-created_at']
    inlines = [ChatGroupMemberInline]
    autocomplete_fields = ['created_by']
    date_hierarchy = 'created_at'
    
    def get_members_count(self, obj):
        return obj.get_members_count()
    get_members_count.short_description = 'Members'


@admin.register(ChatGroupMember)
class ChatGroupMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'group', 'role', 'is_active', 'notifications_enabled', 'joined_at']
    list_filter = ['role', 'is_active', 'notifications_enabled', 'joined_at']
    search_fields = ['user__email', 'group__name']
    autocomplete_fields = ['user', 'group']
    ordering = ['-joined_at']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['get_short_content', 'group', 'sender', 'message_type', 'is_read', 'created_at']
    list_filter = ['message_type', 'is_read', 'is_deleted', 'created_at']
    search_fields = ['content', 'sender__email', 'group__name']
    autocomplete_fields = ['sender', 'group', 'reply_to']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    get_short_content.short_description = 'Message'