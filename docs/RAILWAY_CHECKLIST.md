# Railway Production Deployment Checklist

Use this checklist to ensure your Railway deployment is properly configured for production.

## Pre-Deployment Checklist

### Local Preparation

- [ ] Run `python generate_secret_key.py` and save the output
- [ ] Get your Groq API key from https://console.groq.com/keys
  - OR get Gemini API key from https://makersuite.google.com/app/apikey
- [ ] Commit and push all latest changes to GitHub
- [ ] Test locally with `python manage.py runserver`

### Railway Project Setup

- [ ] Create Railway project (if not already created)
- [ ] Provision PostgreSQL database (Railway → Add Service → PostgreSQL)
- [ ] Connect GitHub repository to Railway
- [ ] Configure Dockerfile deployment (already set in `railway.json`)

## Environment Variables Configuration

Go to: **Railway Dashboard → Your Service → Variables Tab**

### Required Variables (Copy-Paste Ready)

```env
DEBUG=False
SECRET_KEY=<PASTE_YOUR_GENERATED_KEY_HERE>
ALLOWED_HOSTS=.railway.app,.up.railway.app
CSRF_TRUSTED_ORIGINS=https://*.railway.app,https://*.up.railway.app
```

### AI Configuration (Choose One Provider)

**Option A: Using Groq (Recommended)**
```env
AI_PROVIDER=groq
GROQ_API_KEY=<YOUR_GROQ_API_KEY>
GROQ_MODEL=llama-3.3-70b-versatile
```

**Option B: Using Gemini**
```env
AI_PROVIDER=gemini
GEMINI_API_KEY=<YOUR_GEMINI_API_KEY>
GEMINI_MODEL=gemini-1.5-flash
```

### Optional Variables

**Only if using Backblaze B2 for static files:**
```env
BACKBLAZE_APPLICATION_KEY_ID=<YOUR_KEY_ID>
BACKBLAZE_APPLICATION_KEY=<YOUR_APPLICATION_KEY>
BACKBLAZE_BUCKET_NAME=<YOUR_BUCKET_NAME>
BACKBLAZE_S3_ENDPOINT_URL=https://s3.us-east-005.backblazeb2.com
```

## Deployment Steps

- [ ] Push code to GitHub (triggers auto-deployment if enabled)
- [ ] Wait for Railway build to complete (check "Deployments" tab)
- [ ] Check build logs for errors
- [ ] Verify deployment status is "Active"

## Post-Deployment Verification

### Access Your Application

- [ ] Visit your Railway URL: `https://<your-app>.up.railway.app`
- [ ] Verify the homepage loads without errors
- [ ] Check browser console for JavaScript errors (F12)

### Check Application Logs

In Railway Dashboard → Logs tab, look for:

- [ ] ✅ "Starting server at tcp:0.0.0.0:<PORT> (application at smallcase_project.asgi:application)"
- [ ] ✅ No errors about missing environment variables
- [ ] ✅ No database connection errors
- [ ] ⚠️ Ensure **NO** "DEBUG is True" warnings

### Test Core Features

- [ ] User signup works
- [ ] User login works
- [ ] Creating a basket works
- [ ] AI chat widget loads
- [ ] Static files (CSS/JS) are loading correctly

### Database Management

Run these commands in Railway Shell (Dashboard → Shell tab):

- [ ] `python manage.py migrate` (run database migrations)
- [ ] `python manage.py createsuperuser` (create admin account)
- [ ] Access admin panel: `https://<your-app>.up.railway.app/admin`

## Security Verification

- [ ] `DEBUG=False` is confirmed in environment variables
- [ ] Using strong, unique SECRET_KEY (not the default dev key)
- [ ] CSRF_TRUSTED_ORIGINS uses `https://` (not `http://`)
- [ ] ALLOWED_HOSTS includes your Railway domain
- [ ] `.env` file is in `.gitignore` (never committed to Git)

## Performance Optimization

- [ ] Static files are being served by WhiteNoise (check network tab in browser DevTools)
- [ ] Database query optimization enabled (`conn_max_age=600` in settings)
- [ ] GZIP compression enabled (WhiteNoise handles this)

## Monitoring & Maintenance

- [ ] Set up Railway alerts for deployment failures
- [ ] Monitor Railway logs regularly for errors
- [ ] Check PostgreSQL storage usage (Railway dashboard)
- [ ] Plan for database backups (Railway provides automatic backups)

## Common Issues Troubleshooting

### Issue: 500 Internal Server Error

**Check:**
- [ ] `DEBUG=False` is set (even though this causes 500 without other configs)
- [ ] `SECRET_KEY` is configured
- [ ] `ALLOWED_HOSTS` includes `.railway.app`
- [ ] Database migrations are complete (`python manage.py migrate`)

**Quick Fix:**
```bash
# In Railway Shell
python manage.py migrate
python manage.py collectstatic --noinput
```

### Issue: CSRF Verification Failed

**Check:**
- [ ] `CSRF_TRUSTED_ORIGINS` uses `https://` (not `http://`)
- [ ] Domain matches your Railway URL

**Quick Fix:**
```env
CSRF_TRUSTED_ORIGINS=https://*.railway.app,https://*.up.railway.app
```

### Issue: Static Files Not Loading (404 errors)

**Check:**
- [ ] `python manage.py collectstatic --noinput` ran during build
- [ ] Check Dockerfile line 25 includes collectstatic command
- [ ] WhiteNoise is in MIDDLEWARE (line 64 in settings.py)

**Quick Fix:**
```bash
# In Railway Shell
python manage.py collectstatic --noinput
```

### Issue: Database Connection Error

**Check:**
- [ ] PostgreSQL service is provisioned on Railway
- [ ] `DATABASE_URL` is automatically set (Railway provides this)
- [ ] Database migrations are complete

**Quick Fix:**
```bash
# In Railway Shell
python manage.py migrate
```

## Rollback Plan

If deployment fails:

1. [ ] Check Railway logs for error messages
2. [ ] Compare environment variables with `.env.template`
3. [ ] Revert to previous deployment (Railway → Deployments → Redeploy)
4. [ ] Fix issues locally and redeploy

## Success Criteria

Your deployment is successful when:

- [✅] Application loads at Railway URL
- [✅] No errors in Railway logs
- [✅] Users can signup/login
- [✅] AI chat is responding
- [✅] Static files load correctly
- [✅] Admin panel is accessible
- [✅] DEBUG is off (production mode)
- [✅] HTTPS is enforced

## Next Steps After Successful Deployment

- [ ] Add custom domain (optional) in Railway settings
- [ ] Set up monitoring/logging (Railway provides basic logs)
- [ ] Configure environment-specific feature flags
- [ ] Document your Railway URL for team/users
- [ ] Plan for scaling (Railway handles this automatically)

---

## Quick Command Reference

```bash
# Generate production SECRET_KEY (run locally)
python generate_secret_key.py

# Run database migrations (Railway Shell)
python manage.py migrate

# Create admin user (Railway Shell)
python manage.py createsuperuser

# Collect static files (Railway Shell or runs automatically in Dockerfile)
python manage.py collectstatic --noinput

# Check Django configuration (Railway Shell)
python manage.py check --deploy
```

---

**🎉 Congratulations!** Once all checkboxes are complete, your application is production-ready on Railway!

For detailed explanations, see:
- [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md) - Comprehensive guide
- [RAILWAY_PRODUCTION_QUICK_START.md](./RAILWAY_PRODUCTION_QUICK_START.md) - Quick reference
