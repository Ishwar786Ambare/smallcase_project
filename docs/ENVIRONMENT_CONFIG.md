# Environment Configuration Summary

## Question: Can I use production settings for Railway?

**Answer: YES! ✅ Your application is already configured to do this automatically!**

## How It Works

Your `settings.py` file uses **environment variables** to automatically detect whether it's running locally or on Railway:

```python
# Automatically uses different values based on environment:

DEBUG = os.environ.get('DEBUG', 'True')  
# Railway: Set to 'False' → Production mode
# Local: Defaults to 'True' → Development mode

SECRET_KEY = os.environ.get('SECRET_KEY', 'default-dev-key')
# Railway: Use strong generated key → Secure
# Local: Uses default → Convenient for development

DATABASES = dj_database_url.config(
    default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
)
# Railway: DATABASE_URL exists → Uses PostgreSQL
# Local: No DATABASE_URL → Uses SQLite
```

## Two Configuration Methods

### Method 1: Local Development (`.env` file)

Create a `.env` file in your project root:

```env
DEBUG=True
SECRET_KEY=django-insecure-dev-key-ok-for-local
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000
AI_PROVIDER=groq
GROQ_API_KEY=your-api-key
```

**Django automatically loads this file** via `python-dotenv` (lines 16-18 in settings.py)

### Method 2: Railway Production (Environment Variables)

Set these in **Railway Dashboard → Variables Tab**:

```env
DEBUG=False
SECRET_KEY=<strong-generated-key>
ALLOWED_HOSTS=.railway.app,.up.railway.app
CSRF_TRUSTED_ORIGINS=https://*.railway.app,https://*.up.railway.app
AI_PROVIDER=groq
GROQ_API_KEY=your-api-key
```

**Railway automatically injects these** as environment variables into your application.

## What Changes Automatically?

| Feature | Local (DEBUG=True) | Railway (DEBUG=False) |
|---------|-------------------|----------------------|
| **Error Pages** | Detailed debug info | Generic error pages (secure) |
| **Static Files** | Dev server serves them | WhiteNoise serves them |
| **Database** | SQLite | PostgreSQL |
| **Security** | Relaxed (for convenience) | Strict (HTTPS, CSRF, etc.) |
| **Logging** | Console output | Production logging |
| **Caching** | In-memory (local) | In-memory (can upgrade to Redis) |

## Benefits of This Approach

1. ✅ **Single Codebase**: Same code works for both local and production
2. ✅ **No Duplication**: No need for separate `settings_dev.py` and `settings_prod.py`
3. ✅ **Environment-Specific**: Each environment gets appropriate configuration
4. ✅ **Secure**: Production secrets stay in Railway, never committed to Git
5. ✅ **Flexible**: Easy to add new environment variables as needed

## What You Need to Do

### For Local Development:
1. Copy `.env.template` to `.env`
2. Fill in your values
3. Run `python manage.py runserver`

### For Railway Production:
1. Run `python generate_secret_key.py` to generate a strong key
2. Set environment variables in Railway Dashboard
3. Deploy to Railway (push to GitHub)

**That's it!** No code changes needed. The same application code automatically adapts to each environment.

## Documentation

- 📖 **[RAILWAY_PRODUCTION_QUICK_START.md](./RAILWAY_PRODUCTION_QUICK_START.md)**  
  Fast-track guide to get deployed quickly

- ✅ **[RAILWAY_CHECKLIST.md](./RAILWAY_CHECKLIST.md)**  
  Interactive checklist to ensure everything is configured correctly

- 📚 **[RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md)**  
  Comprehensive guide with troubleshooting and best practices

## Quick Reference Commands

```bash
# Generate production secret key
python generate_secret_key.py

# Run locally
python manage.py runserver

# Run migrations (Railway Shell)
python manage.py migrate

# Create admin user (Railway Shell)
python manage.py createsuperuser

# Collect static files (Railway Shell, or automatic in Dockerfile)
python manage.py collectstatic --noinput
```

## Key Files

- `settings.py` - Environment-aware configuration (already configured ✅)
- `.env` - Local development variables (Git-ignored)
- `.env.template` - Template showing all available variables
- `Dockerfile` - Production build configuration (already configured ✅)
- `railway.json` - Railway deployment settings (already configured ✅)

## Summary

Your Django application is **already production-ready**! 🚀

The settings file intelligently reads from:
- **`.env` file** when running locally
- **Environment variables** when running on Railway

Just configure the environment variables appropriately for each environment, and you're good to go!

No duplicate settings files. No complex configuration. Just simple, clean, environment-aware settings. ✨
