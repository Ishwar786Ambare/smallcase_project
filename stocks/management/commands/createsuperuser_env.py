"""
Custom management command to create a superuser from environment variables.
Usage: python manage.py createsuperuser_env
"""

import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a superuser from environment variables DJANGO_SUPERUSER_EMAIL and DJANGO_SUPERUSER_PASSWORD'

    def handle(self, *args, **options):
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        
        if not email or not password:
            self.stderr.write(
                self.style.ERROR(
                    'Please set DJANGO_SUPERUSER_EMAIL and DJANGO_SUPERUSER_PASSWORD environment variables'
                )
            )
            return
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f'Superuser with email {email} already exists. Skipping.')
            )
            return
        
        # Create the superuser
        user = User.objects.create_superuser(
            email=email,
            password=password
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Superuser {email} created successfully!')
        )
