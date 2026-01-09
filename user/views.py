# user/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.middleware.csrf import get_token
from .models import User


def signup(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    context = {'csrf_token': get_token(request)}
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        
        # Preserve input values
        context['email'] = email
        context['username'] = username
        
        # Validation
        if not email or not password or not username:
            messages.error(request, 'All fields are required')
            return render(request, 'user/signup.j2', context)
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match')
            return render(request, 'user/signup.j2', context)
        
        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters')
            return render(request, 'user/signup.j2', context)
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return render(request, 'user/signup.j2', context)
        
        # Create user
        try:
            user = User.objects.create(
                email=email,
                username=username,
                password=make_password(password)
            )
            # Log in the user
            # Specify backend to avoid "multiple authentication backends" error
            user.backend = 'user.backends.EmailOrUsernameBackend'
            login(request, user)
            messages.success(request, f'Welcome {username}! Your account has been created.')
            return redirect('home')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'user/signup.j2', context)
    
    return render(request, 'user/signup.j2', context)


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        remember_me = request.POST.get('remember_me')
        
        if not email or not password:
            messages.error(request, 'Email and password are required')
            return render(request, 'user/login.j2')
        
        # Authenticate user
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            
            # Set session expiry based on remember me
            if not remember_me:
                request.session.set_expiry(0)  # Session expires when browser closes
            else:
                request.session.set_expiry(1209600)  # 2 weeks
            
            messages.success(request, f'Welcome back, {user.username}!')
            
            # Redirect to next parameter or home
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password')
            return render(request, 'user/login.j2')
    
    context = {'csrf_token': get_token(request)}
    return render(request, 'user/login.j2', context)


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('user:login')


def contact_form_submit(request):
    """
    Handle contact form submission via AJAX
    Returns JSON response with validation errors or success message
    """
    from django.http import JsonResponse
    from django.views.decorators.http import require_http_methods
    from .forms import ContactForm
    from .models import ContactMessage

    if request.method == 'POST':
        # Check if it's an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        # Use POST data (form sends URL-encoded data, not JSON)
        form = ContactForm(request.POST)
        
        if form.is_valid():
            # Save using ModelForm's save method which automatically handles metadata
            # The form's save() method will extract IP, user agent, and user from request
            contact_message = form.save(commit=True, request=request)
            
            # Get cleaned data for response
            name = contact_message.name
            email = contact_message.email
            subject = contact_message.subject
            
            # TODO: Send email notification
            # Example using Django's send_mail:
            # from django.core.mail import send_mail
            # from django.conf import settings
            # send_mail(
            #     subject=f"New Contact Form: {subject}",
            #     message=f"From: {name} ({email})\n\n{contact_message.message}\n\n---\nMessage ID: {contact_message.id}\nSubmitted at: {contact_message.created_at}",
            #     from_email=settings.DEFAULT_FROM_EMAIL,
            #     recipient_list=['support@stockbasket.com'],
            #     fail_silently=False,
            # )
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': 'Thank you for your message! We will get back to you soon.',
                    'data': {
                        'id': contact_message.id,
                        'name': name,
                        'email': email,
                        'subject': subject,
                        'submitted_at': contact_message.created_at.isoformat()
                    }
                })
            else:
                messages.success(request, 'Thank you for your message! We will get back to you soon.')
                return redirect('contact_us')
        else:
            # Form has validation errors
            if is_ajax:
                # Return field-specific errors for AJAX
                errors = {}
                for field, error_list in form.errors.items():
                    errors[field] = [str(error) for error in error_list]
                
                return JsonResponse({
                    'success': False,
                    'errors': errors,
                    'message': 'Please correct the errors below'
                }, status=400)
            else:
                # Regular form submission
                messages.error(request, 'Please correct the errors below')
                context = {
                    'csrf_token': get_token(request),
                    'form': form
                }
                return render(request, 'stocks/contact.j2', context)
    
    # GET request
    return JsonResponse({
        'success': False,
        'message': 'Method not allowed'
    }, status=405)


# ============ OTP-Based Password Reset Views ============

from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_http_methods
from .otp_utils import OTPManager
import json

User = get_user_model()


@require_http_methods(["POST"])
def request_password_reset_otp(request):
    """
    Request OTP for password reset via email or SMS.
    
    POST data:
        - identifier: email or phone number
        - method: 'email' or 'sms'
    
    Returns:
        JSON response with success status and message
    """

    try:
    # Parse request data

        data = request.POST.dict()
        identifier = data.get('identifier', '').strip()
        method = data.get('method', 'email').lower()

        print(identifier, method)
        if not identifier:
            return JsonResponse({
                'success': False,
                'message': 'Email or phone number is required'
            }, status=400)
        
        # Check if user exists
        if method == 'email':
            try:

                from django.db.models import Q
                user = User.objects.get(Q(email=identifier.lower()) | Q(username=identifier))
            except User.DoesNotExist:
                # Don't reveal if email exists (security)
                return JsonResponse({
                    'success': True,
                    'message': 'If this email is registered, you will receive an OTP shortly.'
                })
        else:
            # For SMS, check phone number (mobile_number field in User model)
            try:
                user = User.objects.get(mobile_number=identifier)
            except User.DoesNotExist:
                return JsonResponse({
                    'success': True,
                    'message': 'If this phone number is registered, you will receive an OTP shortly.'
                })
            except AttributeError:
                return JsonResponse({
                    'success': False,
                    'message': 'SMS feature not configured. Please use email method.'
                }, status=400)
        
        # Generate OTP
        otp = OTPManager.generate_otp()
        # otp = 123456
        # Send OTP
        try:
            if method == 'email':
                OTPManager.send_otp_email(identifier.lower(), otp, purpose='password_reset')
                return JsonResponse({
                    'success': True,
                    'message': 'OTP sent to your email. Please check your inbox.',
                    'identifier': identifier.lower()
                })
            else:
                OTPManager.send_otp_sms(identifier, otp, purpose='password_reset')
                return JsonResponse({
                    'success': True,
                    'message': 'OTP sent to your phone. Please check your messages.',
                    'identifier': identifier
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
def verify_password_reset_otp(request):
    """
    Verify OTP for password reset.
    
    POST data:
        - identifier: email or phone number
        - otp: The OTP code
    
    Returns:
        JSON response with success status and reset token
    """
    try:
        # Parse request data
        data = request.POST.dict()
  
        identifier = data.get('identifier', '').strip()
        otp = data.get('otp', '').strip()
        
        print(identifier, otp)

        if not identifier or not otp:
            return JsonResponse({
                'success': False,
                'message': 'Identifier and OTP are required'
            }, status=400)
        
        # Verify OTP
        result = OTPManager.verify_otp(identifier, otp, otp_type='password_reset')
        print('result',result)
        if result['success']:
            # Generate a temporary reset token
            from django.core.cache import cache
            import secrets
            
            reset_token = secrets.token_urlsafe(32)
            
            # Store the reset token with identifier mapping (valid for 10 minutes)
            cache.set(f'password_reset_token_{reset_token}', identifier, 600)
            
            return JsonResponse({
                'success': True,
                'message': result['message'],
                'reset_token': reset_token
            })
        else:
            return JsonResponse({
                'success': False,
                'message': result['message']
            }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
def reset_password_with_token(request):
    """
    Reset password using verified OTP token.
    
    POST data:
        - reset_token: Token from OTP verification
        - new_password: New password
        - confirm_password: Password confirmation
    
    Returns:
        JSON response with success status
    """
    try:
        # Parse request data
        data = request.POST.dict()
        print('data', data)
        reset_token = data.get('reset_token', '').strip()
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')
        print('---------------------------------------------')
        print(reset_token, new_password, confirm_password)
        print('----------------------------------------------')
        if not reset_token or not new_password or not confirm_password:
            return JsonResponse({
                'success': False,
                'message': 'All fields are required'
            }, status=400)
        
        if new_password != confirm_password:
            return JsonResponse({
                'success': False,
                'message': 'Passwords do not match'
            }, status=400)
        
        if len(new_password) < 8:
            return JsonResponse({
                'success': False,
                'message': 'Password must be at least 8 characters'
            }, status=400)
        
        # Verify reset token
        from django.core.cache import cache
        
        identifier = cache.get(f'password_reset_token_{reset_token}')
        
        if not identifier:
            return JsonResponse({
                'success': False,
                'message': 'Invalid or expired reset token. Please request a new OTP.'
            }, status=400)
        
        # Find user
        try:
            # Try email first
            try:
                from django.db.models import Q
                user = User.objects.get(Q(email=identifier) | Q(username=identifier))
            except User.DoesNotExist:
                # Try mobile number
                user = User.objects.get(mobile_number=identifier)
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'User not found'
            }, status=404)
        
        # Update password
        from django.contrib.auth.hashers import make_password
        
        user.password = make_password(new_password)
        user.save()
        
        # Clear reset token
        cache.delete(f'password_reset_token_{reset_token}')
        
        return JsonResponse({
            'success': True,
            'message': 'Password reset successfully. You can now login with your new password.'
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)


from django.views.decorators.csrf import ensure_csrf_cookie

@ensure_csrf_cookie
def forgot_password(request):
    """
    Display forgot password page.
    """
    if request.user.is_authenticated:
        return redirect('home')
    
    context = {'csrf_token': get_token(request)}
    return render(request, 'user/forgot_password.j2', context)

