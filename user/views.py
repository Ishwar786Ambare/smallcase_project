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
