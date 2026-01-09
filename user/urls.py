# user/urls.py

from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('contact/submit/', views.contact_form_submit, name='contact_submit'),
    
    # OTP-based password reset
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('api/request-password-reset-otp/', views.request_password_reset_otp, name='request_password_reset_otp'),
    path('api/verify-password-reset-otp/', views.verify_password_reset_otp, name='verify_password_reset_otp'),
    path('api/reset-password-with-token/', views.reset_password_with_token, name='reset_password_with_token'),
]

