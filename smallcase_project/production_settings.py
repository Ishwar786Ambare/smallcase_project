from .settings import *

DEBUG = False
ALLOWED_HOSTS = ['ishwarambare.pythonanywhere.com']

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Static files
STATIC_ROOT = '/home/ishwarambare/smallcase_project/static'
STATIC_URL = '/static/'

# Database (SQLite is fine for free tier)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/home/ishwarambare/smallcase_project/db.sqlite3',
    }
}