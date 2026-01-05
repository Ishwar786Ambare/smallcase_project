# Stock Basket Manager

A web application for managing stock baskets with equal-weighted allocation.

![Stock Basket Manager Preview](https://github.com/Ishwar786Ambare/smallcase_project/blob/main/image.jpeg)

## Features

- Create and manage stock baskets
- Add and remove stocks from baskets
- Calculate total investment and current value
- Calculate profit/loss
- View basket details

## Technologies

- Django
- Jinja2
- Bootstrap
- jQuery
- DataTables

## Setup

1. Clone the repository
2. Install dependencies
3. Run migrations
4. Start the development server

## Usage

1. Create a new basket
2. Add stocks to the basket
3. View basket details
4. Calculate profit/loss

## Deployment

### Railway Production Deployment

This application is production-ready and can be deployed to Railway with minimal configuration.

**Quick Start:**
- 📖 [Quick Start Guide](docs/RAILWAY_PRODUCTION_QUICK_START.md) - Fast track to production
- ✅ [Deployment Checklist](docs/RAILWAY_CHECKLIST.md) - Step-by-step verification
- 📚 [Detailed Guide](docs/RAILWAY_DEPLOYMENT.md) - Comprehensive deployment documentation

**Key Points:**
- ✅ Settings are **environment-aware** (automatically detects local vs. production)
- ✅ Just set environment variables in Railway Dashboard - no code changes needed
- ✅ Supports PostgreSQL (production) and SQLite (local development)
- ✅ Production security enabled (DEBUG=False, CSRF protection, etc.)

### Generate Production Secret Key

```bash
python generate_secret_key.py
```

Then set the output as `SECRET_KEY` environment variable in Railway.

## License

MIT