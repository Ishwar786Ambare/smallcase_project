# Railway Production Deployment Guide

This guide explains how to deploy your Django application to Railway with production settings.

## Prerequisites

1. Railway account (https://railway.app)
2. GitHub repository connected to Railway
3. PostgreSQL database provisioned on Railway

## Step-by-Step Deployment

### 1. Generate Production SECRET_KEY

Run this command locally to generate a secure secret key:

```bash
python generate_secret_key.py
```

Copy the generated key for use in Railway environment variables.

### 2. Configure Environment Variables on Railway

Go to your Railway project → Variables tab and add:

#### Required Variables:

```bash
# Core Django Settings
DEBUG=False
SECRET_KEY=<paste-your-generated-secret-key-here>

# Allowed Hosts (update with your Railway domain)
ALLOWED_HOSTS=.railway.app,.up.railway.app

# CSRF Protection (use https for Railway)
CSRF_TRUSTED_ORIGINS=https://*.railway.app,https://*.up.railway.app
```

#### AI Configuration (at least one provider):

```bash
# Using Groq (Recommended - 30 requests/min free)
AI_PROVIDER=groq
GROQ_API_KEY=<your-groq-api-key>
GROQ_MODEL=llama-3.3-70b-versatile
```

**OR**

```bash
# Using Google Gemini (15 requests/min free)
AI_PROVIDER=gemini
GEMINI_API_KEY=<your-gemini-api-key>
GEMINI_MODEL=gemini-1.5-flash
```

#### Optional Variables:

```bash
# Backblaze B2 (if using for static file storage)
BACKBLAZE_APPLICATION_KEY_ID=<your-key-id>
BACKBLAZE_APPLICATION_KEY=<your-application-key>
BACKBLAZE_BUCKET_NAME=<your-bucket-name>
BACKBLAZE_S3_ENDPOINT_URL=https://s3.us-east-005.backblazeb2.com
```

### 3. Railway Automatically Provides

Railway automatically sets these - **DO NOT** set them manually:

- `DATABASE_URL` - PostgreSQL connection string
- `PORT` - Application port
- `RAILWAY_ENVIRONMENT` - Deployment environment

### 4. Verify Dockerfile

Your `Dockerfile` should already be configured correctly. Railway uses it to build your app.

### 5. Deploy

Railway will automatically deploy when you push to your connected GitHub repository.

## Post-Deployment Steps

### Run Database Migrations

After first deployment, run migrations via Railway's shell:

```bash
python manage.py migrate
```

### Create Superuser (Admin Account)

Create an admin account to access Django admin:

```bash
python manage.py createsuperuser
```

### Collect Static Files

Static files are collected automatically during build (see Dockerfile), but you can manually run:

```bash
python manage.py collectstatic --noinput
```

## Monitoring Your Application

### Check Logs

In Railway Dashboard:
- Go to your service
- Click "Logs" tab
- Monitor for errors or issues

### Common Issues and Solutions

#### Issue: 500 Internal Server Error

**Solution**: Check logs and ensure:
- `DEBUG=False` is set
- `SECRET_KEY` is configured
- `ALLOWED_HOSTS` includes your Railway domain
- Database migrations are complete

#### Issue: Static Files Not Loading

**Solution**: 
- Verify `python manage.py collectstatic` ran during build
- Check Dockerfile includes the collectstatic command
- Ensure WhiteNoise is in MIDDLEWARE (already configured in settings.py)

#### Issue: CSRF Verification Failed

**Solution**:
- Ensure `CSRF_TRUSTED_ORIGINS` uses **https://** (not http://)
- Domain must match your Railway URL

#### Issue: Database Connection Error

**Solution**:
- Verify Railway PostgreSQL is provisioned
- Check `DATABASE_URL` is automatically set by Railway
- Run migrations: `python manage.py migrate`

## Switching Between Development and Production

### Local Development

Your `.env` file for local development:

```bash
DEBUG=True
SECRET_KEY=<your-dev-secret-key>
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
AI_PROVIDER=groq
GROQ_API_KEY=<your-groq-api-key>
```

### Railway Production

Railway environment variables (set in dashboard):

```bash
DEBUG=False
SECRET_KEY=<strong-production-secret-key>
ALLOWED_HOSTS=.railway.app,.up.railway.app
CSRF_TRUSTED_ORIGINS=https://*.railway.app,https://*.up.railway.app
AI_PROVIDER=groq
GROQ_API_KEY=<your-groq-api-key>
```

## Security Best Practices

1. ✅ **Never commit `.env` file to Git** (already in `.gitignore`)
2. ✅ **Always use DEBUG=False in production**
3. ✅ **Use strong, unique SECRET_KEY for production**
4. ✅ **Use HTTPS for CSRF_TRUSTED_ORIGINS in production**
5. ✅ **Keep API keys secure and rotate them periodically**
6. ✅ **Regularly update dependencies**: `pip install --upgrade -r requirements.txt`

## URLs and Access

After deployment:

- **Application**: `https://<your-app>.up.railway.app`
- **Admin Panel**: `https://<your-app>.up.railway.app/admin`
- **API Endpoints**: `https://<your-app>.up.railway.app/api/...`

## Need Help?

- Railway Docs: https://docs.railway.app
- Django Deployment Docs: https://docs.djangoproject.com/en/stable/howto/deployment/
- Project Issues: Create an issue in your GitHub repository

## Summary

Your Django application is **already configured** to work with both local development and Railway production. The `settings.py` file reads environment variables and adjusts accordingly:

- **Local**: Uses SQLite, DEBUG=True, local cache
- **Railway**: Uses PostgreSQL, DEBUG=False, production security

Just set the environment variables in Railway Dashboard, and you're ready to deploy! 🚀
