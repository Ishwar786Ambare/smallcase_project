# user/models.py

from django.db import models
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


class ContactMessage(models.Model):
    """
    Model to store contact form submissions
    Tracks all user inquiries with status and metadata
    """
    
    # Status choices
    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('spam', 'Spam'),
    ]
    
    # Contact information
    name = models.CharField(
        max_length=100,
        help_text="Name of the person contacting"
    )
    email = models.EmailField(
        max_length=254,
        help_text="Email address for response"
    )
    subject = models.CharField(
        max_length=200,
        help_text="Subject of the inquiry"
    )
    message = models.TextField(
        help_text="Message content"
    )
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        db_index=True,
        help_text="Current status of the inquiry"
    )
    
    # Optional: Link to user if logged in
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contact_messages',
        help_text="User who submitted the form (if authenticated)"
    )
    
    # Metadata
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the submitter"
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        help_text="Browser user agent string"
    )
    
    # Admin notes
    admin_notes = models.TextField(
        blank=True,
        help_text="Internal notes by staff (not visible to user)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When the message was submitted"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last time the message was updated"
    )
    replied_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the inquiry was replied to"
    )
    
    class Meta:
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'
        ordering = ['-created_at']  # Most recent first
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.subject} ({self.get_status_display()})"
    
    def mark_as_read(self):
        """Mark message as read"""
        if self.status == 'new':
            self.status = 'read'
            self.save(update_fields=['status', 'updated_at'])
    
    def mark_as_resolved(self):
        """Mark message as resolved"""
        from django.utils import timezone
        self.status = 'resolved'
        if not self.replied_at:
            self.replied_at = timezone.now()
        self.save(update_fields=['status', 'replied_at', 'updated_at'])
    
    def mark_as_spam(self):
        """Mark message as spam"""
        self.status = 'spam'
        self.save(update_fields=['status', 'updated_at'])
    
    @property
    def is_new(self):
        """Check if message is new/unread"""
        return self.status == 'new'
    
    @property
    def short_message(self):
        """Return truncated message for list views"""
        if len(self.message) > 100:
            return self.message[:100] + '...'
        return self.message

