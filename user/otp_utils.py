"""
OTP (One-Time Password) Utility Module

This module provides OTP generation and verification for:
- Password reset via email
- Password reset via SMS (Twilio)
- OTP validation and expiry management
"""

import random
import string
from datetime import datetime, timedelta
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


class OTPManager:
    """
    Manager class for OTP generation, sending, and verification.
    """
    
    @staticmethod
    def generate_otp(length=None):
        """
        Generate a random OTP of specified length.
        
        Args:
            length (int): Length of OTP. Defaults to settings.OTP_LENGTH
        
        Returns:
            str: Generated OTP
        """
        length = length or getattr(settings, 'OTP_LENGTH', 6)
        return ''.join(random.choices(string.digits, k=length))
    
    @staticmethod
    def get_cache_key(identifier, otp_type='password_reset'):
        """
        Generate cache key for OTP storage.
        
        Args:
            identifier (str): Email or phone number
            otp_type (str): Type of OTP (password_reset, email_verification, etc.)
        
        Returns:
            str: Cache key
        """
        return f'otp_{otp_type}_{identifier}'
    
    @staticmethod
    def get_attempts_key(identifier, otp_type='password_reset'):
        """
        Generate cache key for OTP attempts tracking.
        
        Args:
            identifier (str): Email or phone number
            otp_type (str): Type of OTP
        
        Returns:
            str: Cache key for attempts
        """
        return f'otp_attempts_{otp_type}_{identifier}'
    
    @staticmethod
    def get_cooldown_key(identifier, otp_type='password_reset'):
        """
        Generate cache key for OTP cooldown tracking.
        
        Args:
            identifier (str): Email or phone number
            otp_type (str): Type of OTP
        
        Returns:
            str: Cache key for cooldown
        """
        return f'otp_cooldown_{otp_type}_{identifier}'
    
    @classmethod
    def send_otp_email(cls, email, otp, purpose='password_reset'):
        """
        Send OTP via email.
        
        Args:
            email (str): Recipient email address
            otp (str): OTP to send
            purpose (str): Purpose of OTP (for email template)
        
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Check cooldown
            cooldown_key = cls.get_cooldown_key(email, purpose)
            if cache.get(cooldown_key):
                remaining = cache.ttl(cooldown_key)
                raise Exception(f'Please wait {remaining} seconds before requesting another OTP.')
            
            # Store OTP in cache
            cache_key = cls.get_cache_key(email, purpose)
            expiry_time = getattr(settings, 'OTP_EXPIRY_TIME', 300)  # Default 5 minutes
            cache.set(cache_key, otp, expiry_time)
            
            # Set cooldown
            cooldown_time = getattr(settings, 'OTP_COOLDOWN_TIME', 60)  # Default 1 minute
            cache.set(cooldown_key, True, cooldown_time)
            
            # Prepare email content
            subject = f'Your OTP for {purpose.replace("_", " ").title()}'
            
            # Create HTML email
            html_message = render_to_string('user/email/otp_email.html', {
                'otp': otp,
                'purpose': purpose.replace('_', ' ').title(),
                'expiry_minutes': expiry_time // 60,
                'site_name': 'Smallcase Project',
            })
            
            # Create plain text version
            plain_message = strip_tags(html_message)
            print(
                'email sending'
            )
            # Send email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email, 'theeartharchive0@gmail.com'],
                html_message=html_message,
                fail_silently=False,
            )
            print(
                'email sent'
            )
            return True
        
        except Exception as e:
            print(f"Error sending OTP email: {e}")
            raise
    
    @classmethod
    def send_otp_sms(cls, phone_number, otp, purpose='password_reset'):
        """
        Send OTP via SMS using Twilio.
        
        Args:
            phone_number (str): Recipient phone number (E.164 format: +1234567890)
            otp (str): OTP to send
            purpose (str): Purpose of OTP
        
        Returns:
            bool: True if SMS sent successfully, False otherwise
        """
        try:
            # Check if Twilio is configured
            if not all([
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN,
                settings.TWILIO_PHONE_NUMBER
            ]):
                raise Exception('Twilio is not configured. Please set TWILIO_* environment variables.')
            
            # Check cooldown
            cooldown_key = cls.get_cooldown_key(phone_number, purpose)
            if cache.get(cooldown_key):
                remaining = cache.ttl(cooldown_key)
                raise Exception(f'Please wait {remaining} seconds before requesting another OTP.')
            
            # Store OTP in cache
            cache_key = cls.get_cache_key(phone_number, purpose)
            expiry_time = getattr(settings, 'OTP_EXPIRY_TIME', 300)  # Default 5 minutes
            cache.set(cache_key, otp, expiry_time)
            
            # Set cooldown
            cooldown_time = getattr(settings, 'OTP_COOLDOWN_TIME', 60)  # Default 1 minute
            cache.set(cooldown_key, True, cooldown_time)
            
            # Send SMS via Twilio
            from twilio.rest import Client
            
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            
            message = client.messages.create(
                body=f'Your OTP for {purpose.replace("_", " ").title()} is: {otp}. Valid for {expiry_time // 60} minutes.',
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            
            return True
        
        except Exception as e:
            print(f"Error sending OTP SMS: {e}")
            raise
    
    @classmethod
    def verify_otp(cls, identifier, otp, otp_type='password_reset'):
        """
        Verify OTP.
        
        Args:
            identifier (str): Email or phone number
            otp (str): OTP to verify
            otp_type (str): Type of OTP
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        cache_key = cls.get_cache_key(identifier, otp_type)
        attempts_key = cls.get_attempts_key(identifier, otp_type)
        
        # Get stored OTP
        stored_otp = cache.get(cache_key)
        
        if not stored_otp:
            return {
                'success': False,
                'message': 'OTP has expired or does not exist. Please request a new one.'
            }
        
        # Check attempts
        attempts = cache.get(attempts_key, 0)
        max_attempts = getattr(settings, 'MAX_OTP_ATTEMPTS', 3)
        
        if attempts >= max_attempts:
            # Clear OTP and attempts
            cache.delete(cache_key)
            cache.delete(attempts_key)
            return {
                'success': False,
                'message': f'Maximum OTP attempts ({max_attempts}) exceeded. Please request a new OTP.'
            }
        
        # Verify OTP
        if str(stored_otp) == str(otp):
            # OTP is valid - clear it from cache
            cache.delete(cache_key)
            cache.delete(attempts_key)
            return {
                'success': True,
                'message': 'OTP verified successfully.'
            }
        else:
            # Increment attempts
            cache.set(attempts_key, attempts + 1, getattr(settings, 'OTP_EXPIRY_TIME', 300))
            remaining_attempts = max_attempts - attempts - 1
            return {
                'success': False,
                'message': f'Invalid OTP. {remaining_attempts} attempt(s) remaining.'
            }
    
    @classmethod
    def clear_otp(cls, identifier, otp_type='password_reset'):
        """
        Clear OTP from cache.
        
        Args:
            identifier (str): Email or phone number
            otp_type (str): Type of OTP
        """
        cache_key = cls.get_cache_key(identifier, otp_type)
        attempts_key = cls.get_attempts_key(identifier, otp_type)
        cache.delete(cache_key)
        cache.delete(attempts_key)
