# Quick Railway Production Setup

## TL;DR - Fast Track to Production

### 1. Generate Production Secret Key

```bash
python generate_secret_key.py
```

Copy the output.

### 2. Set These Variables in Railway Dashboard

Go to: **Railway Project → Your Service → Variables Tab**

Add these variables:

```env
DEBUG=False
SECRET_KEY=<paste-generated-key-here>
ALLOWED_HOSTS=.railway.app,.up.railway.app
CSRF_TRUSTED_ORIGINS=https://*.railway.app,https://*.up.railway.app
AI_PROVIDER=groq
GROQ_API_KEY=<your-groq-api-key>
```

### 3. Deploy

Push to GitHub (if auto-deploy is enabled) or manually trigger deployment in Railway.

### 4. Done! ✅

Your app is now running in production mode on Railway.

---

## What's Different Between Local and Production?

| Setting | Local (.env file) | Railway (Environment Variables) |
|---------|-------------------|--------------------------------|
| **DEBUG** | `True` | `False` ⚠️ **Critical** |
| **SECRET_KEY** | Dev key (weak is OK) | Strong generated key 🔐 |
| **ALLOWED_HOSTS** | `localhost,127.0.0.1` | `.railway.app,.up.railway.app` |
| **CSRF_TRUSTED_ORIGINS** | `http://localhost:8000` | `https://*.railway.app` 🔒 |
| **Database** | SQLite (automatic) | PostgreSQL (Railway provides) |
| **Static Files** | Django dev server | WhiteNoise (production) |

---

## Answer to Your Question

**Q: Is there any way to use production settings for Railway development server?**

**A: Yes! Your app already does this automatically!** ✅

Your `settings.py` is **environment-aware**:

- It reads from **environment variables** (Railway)
- Falls back to **`.env` file** (Local)
- Uses **different defaults** for different environments

### How It Works:

```python
# settings.py automatically detects environment:

DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')
# Railway sets DEBUG=False → Production Mode ✅
# Local uses .env DEBUG=True → Development Mode ✅

SECRET_KEY = os.environ.get('SECRET_KEY', 'insecure-dev-key')
# Railway uses strong key → Secure ✅
# Local uses default → Development ✅

DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        ...
    )
}
# Railway has DATABASE_URL → Uses PostgreSQL ✅
# Local doesn't → Uses SQLite ✅
```

**No code changes needed!** Just set environment variables in Railway, and it automatically uses production settings! 🚀

---

## Verifying Production Mode

After deployment, check your Railway logs. You should see:

```
✅ DEBUG is off (production mode)
✅ Using PostgreSQL database
✅ Static files served via WhiteNoise
✅ HTTPS security enforced
```

If you see warnings about DEBUG=True on Railway, you forgot to set `DEBUG=False` in environment variables.

---

## Key Takeaway

**Your Django project is already production-ready!** 

The same codebase works for both:
- **Local Development** (reads `.env` file)
- **Railway Production** (reads Railway environment variables)

Just configure the environment variables differently for each environment. No duplicate settings files needed! 🎉

---

For detailed guide, see: [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md)
