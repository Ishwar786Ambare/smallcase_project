# 🚀 PythonAnywhere Deployment Guide

## Complete Step-by-Step Instructions for Deploying Your Stock Portfolio App

---

## ✅ Prerequisites Checklist

Before starting, ensure you have:
- [x] Django project working locally
- [x] All features tested
- [x] `requirements.txt` file created
- [ ] GitHub account (optional but recommended)
- [ ] Email for PythonAnywhere signup

---

## 📋 Step-by-Step Deployment

### **STEP 1: Create PythonAnywhere Account** (5 minutes)

1. Go to **https://www.pythonanywhere.com**
2. Click **"Start running Python online in less than a minute!"**
3. Click **"Create a Beginner account"**
4. Fill in:
   - Username: `your_username` (this will be in your URL!)
   - Email: your email
   - Password: secure password
5. Click **"Register"**
6. **Verify email** (check inbox/spam)
7. **Login** to PythonAnywhere

✅ **You now have a free account! No credit card needed.**

---

### **STEP 2: Upload Your Code** (10 minutes)

**Option A: Using Git (Recommended)**

1. **Push code to GitHub first** (if not already):
   ```bash
   # On your local computer
   cd c:\Users\ishwa\PycharmProjects\smallcase_project
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/smallcase_project.git
   git push -u origin main
   ```

2. **On PythonAnywhere**:
   - Click **"Consoles"** tab
   - Click **"Bash"**
   - In the console, run:
   ```bash
   git clone https://github.com/YOUR_USERNAME/smallcase_project.git
   cd smallcase_project
   ls  # Verify files are there
   ```

**Option B: Manual Upload (If no Git)**

1. **Zip your project** on Windows:
   - Right-click `smallcase_project` folder
   - Send to → Compressed (zipped) folder

2. **On PythonAnywhere**:
   - Click **"Files"** tab
   - Click **"Upload a file"**
   - Upload the zip file
   - In Bash console:
   ```bash
   cd ~
   unzip smallcase_project.zip
   cd smallcase_project
   ```

---

### **STEP 3: Create Virtual Environment** (5 minutes)

In the **Bash console**:

```bash
mkvirtualenv --python=/usr/bin/python3.10 myenv
```

You'll see: `(myenv)` at the start of your prompt.

Install dependencies:
```bash
pip install -r requirements.txt
```

**This will take 2-3 minutes.** Wait for it to complete.

---

### **STEP 4: Configure Django Settings** (10 minutes)

1. **Edit settings.py**:
   ```bash
   nano smallcase_project/settings.py
   ```

2. **Make these changes**:

Find `DEBUG` and change:
```python
DEBUG = False
```

Find `ALLOWED_HOSTS` and change:
```python
ALLOWED_HOSTS = ['your_username.pythonanywhere.com']
```

Add at the bottom:
```python
# Static files
STATIC_ROOT = '/home/your_username/smallcase_project/static'
```

3. **Save and exit**:
   - Press `Ctrl + X`
   - Press `Y`
   - Press `Enter`

---

### **STEP 5: Set Up Database** (5 minutes)

In Bash console:

```bash
python manage.py migrate
```

Create admin user:
```bash
python manage.py createsuperuser
```

Enter:
- Username: `admin`
- Email: your email
- Password: (type password, won't show)
- Password (again): (retype)

Populate stocks:
```bash
python manage.py shell
```

In Python shell:
```python
from stocks.utils import populate_indian_stocks
populate_indian_stocks()
exit()
```

---

### **STEP 6: Collect Static Files** (2 minutes)

```bash
python manage.py collectstatic
```

Type `yes` when asked.

---

### **STEP 7: Create Web App** (10 minutes)

1. Go to **"Web"** tab in PythonAnywhere

2. Click **"Add a new web app"**

3. Click **"Next"** on the domain screen

4. Select **"Manual configuration"**

5. Select **"Python 3.10"**

6. Click **"Next"**

7. **Web app created!** ✅

---

### **STEP 8: Configure Virtual Environment** (2 minutes)

On the **Web** tab:

1. Scroll to **"Virtualenv"** section

2. In the input box, enter:
   ```
   /home/your_username/.virtualenvs/myenv
   ```

3. Click the checkmark ✓

4. Should show: ✅ (green checkmark)

---

### **STEP 9: Configure WSGI File** (10 minutes)

1. On **Web** tab, find **"Code"** section

2. Click on **WSGI configuration file** link:
   `/var/www/your_username_pythonanywhere_com_wsgi.py`

3. **Delete everything** in the file

4. **Paste this** (replace `your_username` with YOUR username):

```python
import os
import sys

# Add your project directory to the sys.path
path = '/home/your_username/smallcase_project'
if path not in sys.path:
    sys.path.insert(0, path)

# Set environment variable for Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'smallcase_project.settings'

# Activate your virtual env
activate_this = '/home/your_username/.virtualenvs/myenv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Import Django's WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

5. Click **"Save"** button

---

### **STEP 10: Configure Static Files** (3 minutes)

On **Web** tab:

1. Scroll to **"Static files"** section

2. Click **"Enter URL"**

3. Enter:
   - **URL**: `/static/`
   - **Directory**: `/home/your_username/smallcase_project/static`

4. Click the checkmark ✓

---

### **STEP 11: Reload Web App** (1 minute)

1. Scroll to top of **Web** tab

2. Click the big green **"Reload your_username.pythonanywhere.com"** button

3. Wait for "Reload complete" message

---

### **STEP 12: Test Your App!** (5 minutes)

1. Click the link at the top: `https://your_username.pythonanywhere.com`

2. **Your app should load!** 🎉

3. Test:
   - ✅ Home page loads
   - ✅ Create basket works
   - ✅ Stock data displays
   - ✅ Charts work
   - ✅ Performance analysis works

---

## 🐛 Troubleshooting

### **Error: "Something went wrong :("**

**Check Error Log:**
1. Go to **Web** tab
2. Click **"Error log"** link
3. Look at the last error

**Common fixes:**

**Import Error:**
```bash
# In Bash console
workon myenv
pip install -r requirements.txt
```

**Static Files Not Loading:**
```bash
python manage.py collectstatic --noinput
```
Then reload web app.

**Database Error:**
```bash
python manage.py migrate
```

---

### **Error: "DisallowedHost"**

Edit `settings.py`:
```python
ALLOWED_HOSTS = ['your_username.pythonanywhere.com', 'localhost']
```

Reload web app.

---

### **Charts Not Working:**

1. Check browser console (F12)
2. Ensure Chart.js CDN loads
3. Check static files are collected
4. Reload web app

---

## 🔄 Updating Your App

**When you make changes:**

1. **Option A: Git (Recommended)**
   ```bash
   # On local computer
   git add .
   git commit -m "Update message"
   git push origin main
   
   # On PythonAnywhere Bash
   cd ~/smallcase_project
   git pull origin main
   python manage.py collectstatic --noinput
   # Reload web app from Web tab
   ```

2. **Option B: Manual**
   - Upload changed files via Files tab
   - Run collectstatic if needed
   - Reload web app

---

## 📊 Your Live URLs

After deployment:

- **Website**: `https://your_username.pythonanywhere.com`
- **Admin**: `https://your_username.pythonanywhere.com/admin/`
- **API**: All your URLs will work!

---

## 💡 Pro Tips

1. **Bookmark** your error log page for quick debugging

2. **Always reload** web app after making changes

3. **Use Git** for easier updates

4. **Check CPU usage** (Web tab) to stay within free tier

5. **Backup database** regularly:
   ```bash
   cp db.sqlite3 db.sqlite3.backup-$(date +%F)
   ```

---

## 🎯 Next Steps After Deployment

1. **Share your URL** with friends!

2. **Test all features** thoroughly

3. **Monitor error logs** first few days

4. **Set up auto-update** with GitHub webhook (optional)

5. **Consider upgrade** if you need:
   - Custom domain
   - More CPU time
   - Always-on tasks

---

## 📞 Need Help?

- **PythonAnywhere Docs**: https://help.pythonanywhere.com/
- **Django Deployment**: https://docs.djangoproject.com/
- **Forum**: https://www.pythonanywhere.com/forums/

---

## ✅ Final Checklist

Before considering deployment complete:

- [ ] App loads at `your_username.pythonanywhere.com`
- [ ] Admin panel accessible
- [ ] Can create baskets
- [ ] Stock prices update
- [ ] Charts display correctly
- [ ] Performance analysis works
- [ ] No errors in error log
- [ ] Tested on mobile browser
- [ ] Shared URL with friends
- [ ] Documented how to update

---

## 🎉 Congratulations!

Your stock portfolio app is now **LIVE** and accessible to anyone on the internet!

**Your URL**: `https://your_username.pythonanywhere.com`

**Total Cost**: ₹0 (FREE!) 💰

**Time to Deploy**: ~30-45 minutes

**Share with pride!** 🚀
