# PostgreSQL Setup Guide for Smallcase Project

This guide explains how to set up PostgreSQL database for the Smallcase Project.

## Table of Contents
1. [Option 1: Use SQLite (Default - No Setup Required)](#option-1-use-sqlite-default)
2. [Option 2: Install PostgreSQL Locally](#option-2-install-postgresql-locally)
3. [Option 3: Use Railway PostgreSQL](#option-3-use-railway-postgresql)
4. [Option 4: Use Docker PostgreSQL](#option-4-use-docker-postgresql)
5. [Configuration](#configuration)
6. [Migrations](#migrations)
7. [Troubleshooting](#troubleshooting)

---

## Option 1: Use SQLite (Default)

No setup required! The project automatically uses SQLite if no `DATABASE_URL` is set.

**When to use:**
- Local development
- Quick testing
- Personal projects

**Limitations:**
- Not suitable for production
- No concurrent write support
- Limited to single server

---

## Option 2: Install PostgreSQL Locally

### Windows Installation

1. **Download PostgreSQL:**
   - Go to: https://www.postgresql.org/download/windows/
   - Download the latest installer (version 15 or 16 recommended)

2. **Run Installer:**
   - Follow the installation wizard
   - Set a password for the `postgres` user (remember this!)
   - Default port: `5432`
   - Include Stack Builder if you want additional tools

3. **Create Database:**
   Open pgAdmin or Command Prompt:
   ```bash
   # Using psql command line (run as Administrator)
   psql -U postgres
   
   # Create database
   CREATE DATABASE smallcase_db;
   
   # Optional: Create a dedicated user
   CREATE USER smallcase_user WITH PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE smallcase_db TO smallcase_user;
   
   # Exit
   \q
   ```

4. **Configure .env file:**
   ```bash
   DATABASE_URL=postgresql://postgres:your_password@localhost:5432/smallcase_db
   ```
   
   Or with dedicated user:
   ```bash
   DATABASE_URL=postgresql://smallcase_user:your_secure_password@localhost:5432/smallcase_db
   ```

### Mac Installation

```bash
# Using Homebrew
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb smallcase_db
```

### Linux (Ubuntu/Debian) Installation

```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database
sudo -u postgres psql
CREATE DATABASE smallcase_db;
CREATE USER smallcase_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE smallcase_db TO smallcase_user;
\q
```

---

## Option 3: Use Railway PostgreSQL

Railway provides a free PostgreSQL addon:

1. **Create Railway Account:**
   - Go to: https://railway.app
   - Sign up/Login

2. **Deploy Project:**
   - Connect your GitHub repo

3. **Add PostgreSQL:**
   - Click "New" → "Database" → "PostgreSQL"
   - Railway auto-provides `DATABASE_URL` environment variable

4. **No .env changes needed** - Railway handles it automatically!

---

## Option 4: Use Docker PostgreSQL

Quick local PostgreSQL using Docker:

```bash
# Run PostgreSQL container
docker run --name smallcase-postgres \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=postgres \
    -e POSTGRES_DB=smallcase_db \
    -p 5432:5432 \
    -d postgres:15

# Configure .env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/smallcase_db
```

**Docker Compose** (recommended for persistence):

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: smallcase_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

Run:
```bash
docker-compose up -d
```

---

## Configuration

### .env File Setup

Add or modify in your `.env` file:

```bash
# ============ Database Configuration ============
# Format: postgresql://username:password@host:port/database_name

# Local PostgreSQL:
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/smallcase_db

# Docker PostgreSQL:
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/smallcase_db

# Railway: Automatically set by Railway
```

### Verify Configuration

Check your database connection:
```bash
# Activate virtual environment
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Test connection
python manage.py check --database default
```

---

## Migrations

After setting up PostgreSQL, run migrations to create tables:

```bash
# Activate virtual environment
.\venv\Scripts\activate

# Apply all migrations
python manage.py migrate

# If needed, create new migrations
python manage.py makemigrations

# Re-populate stocks
python manage.py populate_all_stocks --nifty500

# Create superuser
python manage.py createsuperuser
```

### Migrate Data from SQLite to PostgreSQL

If you have existing data in SQLite:

```bash
# 1. Export data from SQLite
python manage.py dumpdata --exclude contenttypes --exclude auth.permission > backup.json

# 2. Switch to PostgreSQL (update .env)

# 3. Run migrations on PostgreSQL
python manage.py migrate

# 4. Import data
python manage.py loaddata backup.json
```

---

## Troubleshooting

### Common Issues

#### 1. "psycopg2 not installed"
```bash
pip install psycopg2-binary
```

#### 2. "Connection refused"
- Check if PostgreSQL service is running:
  - Windows: Services → PostgreSQL → Start
  - Linux: `sudo systemctl start postgresql`
  - Docker: `docker start smallcase-postgres`

#### 3. "Authentication failed"
- Verify username/password in DATABASE_URL
- Check `pg_hba.conf` for authentication settings

#### 4. "Database does not exist"
```bash
# Create database manually
psql -U postgres -c "CREATE DATABASE smallcase_db;"
```

#### 5. "Permission denied"
```bash
# Grant permissions
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE smallcase_db TO your_user;"
```

### Useful PostgreSQL Commands

```bash
# Connect to database
psql -U postgres -d smallcase_db

# List databases
\l

# List tables
\dt

# Describe table
\d stocks_stock

# Exit
\q
```

---

## Database URL Format Reference

```
postgresql://[user]:[password]@[host]:[port]/[database]
```

| Component | Example | Description |
|-----------|---------|-------------|
| user | postgres | Database username |
| password | mypassword | Database password |
| host | localhost | Database server hostname |
| port | 5432 | PostgreSQL port (default: 5432) |
| database | smallcase_db | Database name |

**Full Examples:**
```bash
# Local with default user
postgresql://postgres:password123@localhost:5432/smallcase_db

# Local with custom user
postgresql://smallcase_user:securepass@localhost:5432/smallcase_db

# Remote server
postgresql://admin:pass@db.example.com:5432/production_db

# With SSL
postgresql://user:pass@host:5432/db?sslmode=require
```

---

## Comparison: SQLite vs PostgreSQL

| Feature | SQLite | PostgreSQL |
|---------|--------|------------|
| Setup | None required | Installation needed |
| Concurrent writes | Limited | Full support |
| Performance | Good for small data | Excellent at scale |
| Production ready | No | Yes |
| Best for | Development | Production |
| Max size | ~140TB | Unlimited |

---

## Summary

1. **For local development:** SQLite works great (no setup)
2. **For production:** Use PostgreSQL (Railway provides free tier)
3. **For testing locally with PostgreSQL:** Use Docker

The project is already configured to handle both seamlessly through `dj_database_url`!
