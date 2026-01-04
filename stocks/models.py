# stocks/models.py

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

# Get the User model (which is now in the user app)
User = get_user_model()


class Stock(models.Model):
    """Model to store stock information"""
    symbol = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True, db_index=True)

    def __str__(self):
        return f"{self.symbol} - {self.name}"

    class Meta:
        ordering = ['symbol']
        indexes = [
            models.Index(fields=['symbol']),
            models.Index(fields=['last_updated']),
        ]


class Basket(models.Model):
    """Model to store stock baskets"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='baskets', null=True, blank=True, db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    investment_amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    def __str__(self):
        return self.name

    def get_total_value(self):
        """Calculate total current value of basket"""
        # OPTIMIZATION: Access prefetched items if available
        if hasattr(self, '_prefetched_objects_cache') and 'items' in self._prefetched_objects_cache:
            items = self.items.all()
        else:
            items = self.items.select_related('stock').all()
        
        total = sum(item.get_current_value() for item in items)
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
    
    class Meta:
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['updated_at']),
        ]


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
        indexes = [
            models.Index(fields=['basket', 'stock']),
        ]


# ==========================================
# Chat Models for Group Messaging
# ==========================================

class ChatGroup(models.Model):
    """Model to store chat groups for group messaging"""
    GROUP_TYPE_CHOICES = [
        ('support', 'Support Chat'),
        ('group', 'Group Chat'),
        ('direct', 'Direct Message'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    group_type = models.CharField(max_length=20, choices=GROUP_TYPE_CHOICES, default='support')
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='created_chat_groups'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    avatar = models.CharField(max_length=10, default='👥')  # Emoji avatar
    is_ai_only = models.BooleanField(default=False)  # True for AI-only support chats
    
    def __str__(self):
        return f"{self.name} ({self.get_group_type_display()})"
    
    def get_members_count(self):
        return self.members.filter(is_active=True).count()
    
    def get_last_message(self):
        return self.messages.order_by('-created_at').first()
    
    def get_unread_count(self, user):
        """Get count of unread messages for a specific user"""
        return self.messages.exclude(sender=user).filter(is_read=False).count()
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['group_type']),
        ]


class ChatGroupMember(models.Model):
    """Model to store group membership"""
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
        ('member', 'Member'),
    ]
    
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_group_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    notifications_enabled = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.email} in {self.group.name}"
    
    class Meta:
        unique_together = ['group', 'user']
        ordering = ['joined_at']
        indexes = [
            models.Index(fields=['group', 'user']),
        ]


class ChatMessage(models.Model):
    """Model to store chat messages"""
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text Message'),
        ('system', 'System Message'),
        ('notification', 'Notification'),
    ]
    
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='sent_messages'
    )
    content = models.TextField()
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='text')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_read = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    
    # For replies
    reply_to = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='replies'
    )
    
    def __str__(self):
        sender_name = self.sender.email if self.sender else 'System'
        return f"{sender_name}: {self.content[:50]}..."
    
    def get_sender_name(self):
        if self.sender:
            return self.sender.username or self.sender.email.split('@')[0]
        return 'Support Team'
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['group', '-created_at']),
            models.Index(fields=['sender']),
        ]