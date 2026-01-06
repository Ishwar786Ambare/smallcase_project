# user/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ContactMessage


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for custom User model"""
    list_display = ['email', 'username', 'is_staff', 'is_active', 'date_joined']
    list_filter = ['is_staff', 'is_active', 'date_joined']
    search_fields = ['email', 'username']
    ordering = ['-date_joined']
    
    # Fields for editing user
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('username', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates',{'fields': ('last_login', 'date_joined')}),
    )
    
    # Fields for creating user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """Admin configuration for ContactMessage model"""
    
    list_display = [
        'id',
        'name',
        'email',
        'subject',
        'status',
        'created_at',
        'is_new',
    ]
    
    list_filter = [
        'status',
        'created_at',
        'updated_at',
    ]
    
    search_fields = [
        'name',
        'email',
        'subject',
        'message',
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'replied_at',
        'ip_address',
        'user_agent',
        'user',
    ]
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'subject', 'message')
        }),
        ('Status', {
            'fields': ('status', 'admin_notes')
        }),
        ('Metadata', {
            'fields': ('user', 'ip_address', 'user_agent'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'replied_at'),
            'classes': ('collapse',),
        }),
    )
    
    ordering = ['-created_at']
    
    date_hierarchy = 'created_at'
    
    list_per_page = 25
    
    # Custom actions
    actions = [
        'mark_as_read',
        'mark_as_in_progress',
        'mark_as_resolved',
        'mark_as_spam',
    ]
    
    def mark_as_read(self, request, queryset):
        """Mark selected messages as read"""
        updated = queryset.filter(status='new').update(status='read')
        self.message_user(request, f'{updated} message(s) marked as read.')
    mark_as_read.short_description = 'Mark as Read'
    
    def mark_as_in_progress(self, request, queryset):
        """Mark selected messages as in progress"""
        updated = queryset.update(status='in_progress')
        self.message_user(request, f'{updated} message(s) marked as in progress.')
    mark_as_in_progress.short_description = 'Mark as In Progress'
    
    def mark_as_resolved(self, request, queryset):
        """Mark selected messages as resolved"""
        from django.utils import timezone
        for message in queryset:
            message.mark_as_resolved()
        self.message_user(request, f'{queryset.count()} message(s) marked as resolved.')
    mark_as_resolved.short_description = 'Mark as Resolved'
    
    def mark_as_spam(self, request, queryset):
        """Mark selected messages as spam"""
        updated = queryset.update(status='spam')
        self.message_user(request, f'{updated} message(s) marked as spam.')
    mark_as_spam.short_description = 'Mark as Spam'
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete contact messages"""
        return request.user.is_superuser

