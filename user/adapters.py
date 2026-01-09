"""
Custom Django Allauth Adapters

These adapters customize the behavior of Django Allauth for:
- Account creation and management
- Social account integration
- Custom email/username handling
"""

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.contrib import messages


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter for Django Allauth account management.
    
    Customizations:
    - Custom email validation
    - Custom username generation
    - Custom redirect URLs
    """
    
    def get_login_redirect_url(self, request):
        """
        Return the URL to redirect to after a successful login.
        """
        # Check if there's a 'next' parameter in the request
        next_url = request.GET.get('next') or request.POST.get('next')
        if next_url:
            return next_url
        
        # Default redirect URL
        return settings.LOGIN_REDIRECT_URL
    
    def get_signup_redirect_url(self, request):
        """
        Return the URL to redirect to after a successful signup.
        """
        return settings.LOGIN_REDIRECT_URL
    
    def is_open_for_signup(self, request):
        """
        Whether to allow signups.
        """
        return True
    
    def save_user(self, request, user, form, commit=True):
        """
        Save a newly created user.
        """
        user = super().save_user(request, user, form, commit=False)
        
        # Add custom logic here if needed
        # For example, set additional user fields
        
        if commit:
            user.save()
        
        return user
    
    def send_confirmation_mail(self, request, emailconfirmation, signup):
        """
        Send email confirmation message.
        """
        # You can customize the email sending logic here
        super().send_confirmation_mail(request, emailconfirmation, signup)
        
        # Add a success message
        messages.success(
            request,
            f"Confirmation email sent to {emailconfirmation.email_address.email}. "
            "Please check your inbox and click the verification link."
        )


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter for Django Allauth social account management.
    
    Customizations:
    - Custom social account connection
    - Auto-populate user data from social providers
    """
    
    def is_open_for_signup(self, request, sociallogin):
        """
        Whether to allow signups via social accounts.
        """
        return True
    
    def populate_user(self, request, sociallogin, data):
        """
        Populate user information from social provider data.
        """
        user = super().populate_user(request, sociallogin, data)
        
        # Customize user data here
        # For example, extract first_name and last_name from social provider
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        
        return user
    
    def pre_social_login(self, request, sociallogin):
        """
        Called just after a user successfully authenticates via a social provider,
        but before the login is actually processed.
        
        This is useful for:
        - Connecting social account to existing user
        - Auto-login if email matches existing account
        """
        # If user is already logged in, connect the social account
        if request.user.is_authenticated:
            return
        
        # Try to connect social account to existing user by email
        try:
            email_address = sociallogin.account.extra_data.get('email')
            if email_address:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                
                # Check if user with this email already exists
                try:
                    user = User.objects.get(email=email_address)
                    # Connect the social account to existing user
                    sociallogin.connect(request, user)
                    messages.info(
                        request,
                        f"Your {sociallogin.account.provider.capitalize()} account "
                        f"has been connected to your existing account."
                    )
                except User.DoesNotExist:
                    pass  # No existing user, will create new one
        except Exception as e:
            # Log error but don't break the login flow
            pass
    
    def save_user(self, request, sociallogin, form=None):
        """
        Save a newly created user authenticated via social provider.
        """
        user = super().save_user(request, sociallogin, form)
        
        # Add custom logic here if needed
        # For example, extract profile picture from social provider
        
        return user
