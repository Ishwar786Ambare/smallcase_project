# Email or Username Login - Implementation Summary

## Overview
This project now supports flexible user authentication allowing users to log in with either their **email address** or **username**.

## Key Components

### 1. Custom User Model (`stocks/models.py`)
- **Email as PRIMARY identifier**: `USERNAME_FIELD = 'email'`
- **Username auto-generation**: If username is not provided, it's auto-generated from email (part before @)
- **Custom UserManager**: Handles user and superuser creation with email-first approach

```python
class User(AbstractUser):
    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=150, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
```

### 2. Custom Authentication Backend (`stocks/backends.py`)
- **EmailOrUsernameBackend**: Allows login with either email or username
- **Case-insensitive matching**: Both email and username are matched case-insensitively
- **Fallback to default**: Django's ModelBackend is used as a fallback

```python
class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Tries to find user by email OR username
        user = User.objects.get(
            Q(email__iexact=username) | Q(username__iexact=username)
        )
```

### 3. Settings Configuration (`smallcase_project/settings.py`)
```python
AUTH_USER_MODEL = 'stocks.User'
AUTHENTICATION_BACKENDS = [
    'stocks.backends.EmailOrUsernameBackend',  # Custom backend
    'django.contrib.auth.backends.ModelBackend',  # Fallback
]
```

### 4. Updated Login Template (`stocks/templates/stocks/login.j2`)
- Label: "Email or Username"
- Placeholder: "your.email@example.com or username"
- Input type: `text` (instead of `email`) to allow username entry

## How It Works

### User Registration (Signup)
1. User provides: email, username (optional), password
2. If username not provided → auto-generated from email
3. User is created with both email and username

### User Login
Users can log in using ANY of:
- ✅ Email: `admin@admin.com`
- ✅ Username: `admin`
- ✅ Auto-generated username: `admin` (from `admin@admin.com`)

The `EmailOrUsernameBackend`:
1. Receives the login input (could be email or username)
2. Queries User model for matching email OR username
3. Verifies password
4. Returns authenticated user or None

### Creating Superuser
```bash
python manage.py createsuperuser
Email: admin@admin.com
Password: ********
Password (again): ********
```

The superuser is created with:
- Email: `admin@admin.com`
- Username: `admin` (auto-generated)
- Password: as provided

## Migration History
- Initial migration: User model with email as USERNAME_FIELD
- Migration 0002: Made username non-unique and blank=True, added custom UserManager

## Benefits
1. **Flexibility**: Users can choose their preferred login method
2. **User-friendly**: No confusion about whether to use email or username
3. **Backward compatible**: Existing users can still log in
4. **Auto-generation**: Username is automatically created if not provided
5. **Case-insensitive**: Login works regardless of email/username casing

## Testing

### Test Cases
1. ✅ Create superuser with email only
2. ✅ Login with email
3. ✅ Login with username
4. ✅ Login with case-insensitive email/username
5. ✅ Signup with email and custom username
6. ✅ Signup with email only (username auto-generated)

## Error Handling
- Invalid email format: Validation error during signup
- Missing email: "The Email field must be set"
- Duplicate email: "Email already registered"
- Invalid credentials: "Invalid email or password"
- Multiple users with same username: Tries email first, then username
