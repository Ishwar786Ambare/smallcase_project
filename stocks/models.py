# stocks/models.py

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):
    """Custom manager for User model with email as username"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user with the given email and password"""
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        
        # Auto-generate username from email if not provided
        if 'username' not in extra_fields or not extra_fields.get('username'):
            extra_fields['username'] = email.split('@')[0]
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser with the given email and password"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user model with email as username"""
    email = models.EmailField(unique=True, db_index=True)
    # Make username non-unique since email is the primary identifier
    username = models.CharField(max_length=150, blank=True)
    
    # Use email for authentication
    USERNAME_FIELD = 'email'
    # Username is auto-generated from email if not provided
    REQUIRED_FIELDS = []
    
    # Use custom manager
    objects = UserManager()
    
    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        # Auto-generate username from email if not set
        if not self.username:
            self.username = self.email.split('@')[0]
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


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