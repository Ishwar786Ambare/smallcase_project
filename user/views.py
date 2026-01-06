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


