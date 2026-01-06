"""
Contact form for the user app
"""
from django import forms
from django.core.validators import EmailValidator, MinLengthValidator
from django.core.exceptions import ValidationError
from .models import ContactMessage
import re


class ContactForm(forms.ModelForm):
    """
    Contact form based on ContactMessage model
    ModelForm automatically handles model field constraints
    """
    
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        
        # Custom widgets with HTML attributes
        widgets = {
            'name': forms.TextInput(attrs={
                'id': 'name',
                'placeholder': 'John Doe',
                'autocomplete': 'name',
            }),
            'email': forms.EmailInput(attrs={
                'id': 'email',
                'placeholder': 'john@example.com',
                'autocomplete': 'email',
            }),
            'subject': forms.TextInput(attrs={
                'id': 'subject',
                'placeholder': 'How can we help you?',
            }),
            'message': forms.Textarea(attrs={
                'id': 'message',
                'placeholder': 'Tell us more about your inquiry...',
                'rows': 6,
            }),
        }
        
        # Custom error messages
        error_messages = {
            'name': {
                'required': 'Please enter your name',
                'max_length': 'Name cannot exceed 100 characters',
            },
            'email': {
                'required': 'Please enter your email address',
                'invalid': 'Please enter a valid email address',
            },
            'subject': {
                'required': 'Please enter a subject',
                'max_length': 'Subject cannot exceed 200 characters',
            },
            'message': {
                'required': 'Please enter your message',
            }
        }
    
    def __init__(self, *args, **kwargs):
        """Initialize form with additional field configurations"""
        super().__init__(*args, **kwargs)
        
        # Add field-level validations
        self.fields['name'].validators.append(
            MinLengthValidator(2, message="Name must be at least 2 characters long")
        )
        self.fields['subject'].validators.append(
            MinLengthValidator(5, message="Subject must be at least 5 characters long")
        )
        self.fields['message'].validators.append(
            MinLengthValidator(10, message="Message must be at least 10 characters long")
        )
        
        # Make all fields required
        self.fields['name'].required = True
        self.fields['email'].required = True
        self.fields['subject'].required = True
        self.fields['message'].required = True
    
    def clean_name(self):
        """Validate name field"""
        name = self.cleaned_data.get('name', '').strip()
        
        # Check if name contains only letters, spaces, and basic punctuation
        if not re.match(r"^[a-zA-Z\s\.\-']+$", name):
            raise ValidationError("Name can only contain letters, spaces, dots, hyphens, and apostrophes")
        
        # Check if name has at least one letter
        if not re.search(r'[a-zA-Z]', name):
            raise ValidationError("Name must contain at least one letter")
        
        return name
    
    def clean_subject(self):
        """Validate subject field"""
        subject = self.cleaned_data.get('subject', '').strip()
        
        # Remove excessive whitespace
        subject = ' '.join(subject.split())
        
        return subject
    
    def clean_message(self):
        """Validate message field"""
        message = self.cleaned_data.get('message', '').strip()
        
        # Check for minimum word count (at least 3 words)
        word_count = len(message.split())
        if word_count < 3:
            raise ValidationError("Message must contain at least 3 words")
        
        # Remove excessive whitespace
        message = ' '.join(message.split())
        
        return message
    
    def clean_email(self):
        """Validate email field with additional checks"""
        email = self.cleaned_data.get('email', '').lower().strip()
        
        # Check for common disposable email domains (optional)
        disposable_domains = ['tempmail.com', 'throwaway.email', '10minutemail.com']
        domain = email.split('@')[-1] if '@' in email else ''
        
        if domain in disposable_domains:
            raise ValidationError("Please use a permanent email address")
        
        return email
    
    def save(self, commit=True, request=None):
        """
        Save the form and automatically populate metadata fields
        
        Args:
            commit: Whether to save to database immediately
            request: HttpRequest object to extract metadata
        
        Returns:
            ContactMessage instance
        """
        instance = super().save(commit=False)
        
        # Set default status if not set
        if not instance.status:
            instance.status = 'new'
        
        # Extract metadata from request if provided
        if request:
            # Get client IP address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            instance.ip_address = ip
            
            # Get user agent (limit to 500 chars)
            instance.user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
            
            # Link to authenticated user
            if request.user.is_authenticated:
                instance.user = request.user
        
        if commit:
            instance.save()
        
        return instance

