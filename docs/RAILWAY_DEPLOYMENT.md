# 🚀 Railway Deployment Guide - Smallcase Project

## Prerequisites
- GitHub account
- Railway account (sign up at [railway.app](https://railway.app))
- Your project pushed to GitHub

---

## Step 1: Push Your Code to GitHub

If you haven't already, push your code to GitHub:

```powershell
# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Prepare for Railway deployment"

# Add your GitHub repo as origin (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/smallcase_project.git

# Push to GitHub
git push -u origin main
```

---

## Step 2: Create a Railway Account

1. Go to [railway.app](https://railway.app)
2. Click **"Login"** → **"Login with GitHub"**
3. Authorize Railway to access your GitHub

---

## Step 3: Create a New Project on Railway

1. Click **"New Project"** (top right)
2. Select **"Deploy from GitHub repo"**
3. Find and select your **smallcase_project** repository
4. Click **"Deploy Now"**

Railway will start building your project automatically.

---

## Step 4: Add PostgreSQL Database

1. In your Railway project dashboard, click **"New"** (or the + button)
2. Select **"Database"** → **"Add PostgreSQL"**
3. Wait for the database to provision (takes ~30 seconds)
4. The `DATABASE_URL` will be **automatically linked** to your app!

---

## Step 5: Set Environment Variables

1. Click on your **web service** (not the database)
2. Go to **"Variables"** tab
3. Add the following variables:

| Variable | Value |
|----------|-------|
| `SECRET_KEY` | Generate at: https://djecrety.ir/ |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `.railway.app,localhost` |
| `CSRF_TRUSTED_ORIGINS` | `https://*.railway.app` |

**To generate SECRET_KEY:**
- Visit https://djecrety.ir/
- Copy the generated key
- Paste it as the value for `SECRET_KEY`

---

## Step 6: Check Build Logs

1. Go to **"Deployments"** tab
2. Click on the latest deployment
3. Monitor the build logs
4. Wait for "Deployment was successful" message

---

## Step 7: Run Database Migrations

Railway should run migrations automatically (configured in `railway.json`). 

If you need to run them manually:

1. Go to project settings → **"Settings"** tab
2. Or use Railway CLI:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Run migrations
railway run python manage.py migrate
```

---

## Step 8: Create a Superuser

Use Railway CLI to create an admin user:

```bash
railway run python manage.py createsuperuser
```

Enter your email, username, and password when prompted.

---

## Step 9: Access Your Deployed App

1. In your project dashboard, click on your **web service**
2. Go to **"Settings"** tab
3. Scroll down to **"Domains"**
4. Click **"Generate Domain"** to get a free `.railway.app` URL
5. Click the generated link to open your app!

Your app will be available at: `https://your-app-name.railway.app`

---

## Step 10: Verify WebSocket Chat Works

1. Open your deployed app in **two different browsers**
2. Log in with different accounts
3. Open the chat widget (bottom right)
4. Send messages - they should appear **instantly** in the other browser!

---

## Troubleshooting

### Build Fails
- Check build logs for errors
- Ensure `requirements.txt` has all dependencies
- Verify `Procfile` exists and is correct

### Static Files Not Loading
- Make sure you ran `collectstatic`
- Check that `whitenoise` is in MIDDLEWARE
- Verify `STATIC_ROOT` is set correctly

### Database Errors
- Ensure PostgreSQL database is added
- Check that `DATABASE_URL` is linked
- Run migrations: `railway run python manage.py migrate`

### WebSocket "Offline"
- Railway supports WebSockets natively
- Make sure `daphne` is used in Procfile (not gunicorn)
- Check browser console for errors

---

## Environment Variables Summary

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `SECRET_KEY` | Django secret key | `your-generated-secret-key` |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Allowed domains | `.railway.app,localhost` |
| `CSRF_TRUSTED_ORIGINS` | CSRF origins | `https://*.railway.app` |
| `DATABASE_URL` | PostgreSQL URL | Auto-set by Railway |

---

## Files Created for Deployment

| File | Purpose |
|------|---------|
| `Procfile` | Tells Railway to run Daphne ASGI server |
| `runtime.txt` | Specifies Python version |
| `railway.json` | Railway-specific configuration |
| `.gitignore` | Excludes unnecessary files from git |

---

## Free Tier Limits

Railway's free tier includes:
- **$5/month credit** (no credit card required)
- ~500 hours of runtime
- 512 MB RAM
- 1 GB disk
- PostgreSQL database included

This is enough for development and small production apps!

---

## Need Help?

- Railway Documentation: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Django Channels Docs: https://channels.readthedocs.io

Good luck with your deployment! 🎉
