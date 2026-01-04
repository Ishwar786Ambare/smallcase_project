# Multi-Language Support (i18n) - Implementation Guide

## Overview
This Django project now supports **multiple languages** using Django's built-in internationalization (i18n) framework.

### Supported Languages
- 🇬🇧 **English** (en) - Default language
- 🇮🇳 **Hindi** (hi) - हिन्दी
- 🇮🇳 **Marathi** (mr) - मराठी

---

## How It Works

### 1. **Configuration** (Already Done ✓)

All settings have been configured in `settings.py`:

```python
# Default language
LANGUAGE_CODE = 'en'

# Supported languages
LANGUAGES = [
    ('en', 'English'),
    ('hi', 'हिन्दी (Hindi)'),
    ('mr', 'मराठी (Marathi)'),
]

# Enable internationalization
USE_I18N = True
USE_L10N = True

# Translation files location
LOCALE_PATHS = [BASE_DIR / 'locale']
```

### 2. **Middleware** (Already Done ✓)

The `LocaleMiddleware` has been added to automatically detect user's language preference:

```python
MIDDLEWARE = [
    # ... other middleware
    'django.middleware.locale.LocaleMiddleware',  # After SessionMiddleware
    # ... other middleware
]
```

### 3. **Language Switcher UI** (Already Done ✓)

A beautiful language switcher widget has been added to all pages. Users can:
- Click the language button (top-right corner)
- Select their preferred language from the dropdown
- The page will reload in the selected language

---

## How to Use i18n in Your Code

### In Jinja2 Templates

Use the `_()` function (gettext) to mark strings for translation:

```jinja2
{# Simple translation #}
<h1>{{ _('Welcome') }}</h1>

{# In attributes #}
<button aria-label="{{ _('Click here') }}">{{ _('Submit') }}</button>

{# In links #}
<a href="{{ url('home') }}">{{ _('Dashboard') }}</a>
```

### In Python Views/Models

```python
from django.utils.translation import gettext as _

def my_view(request):
    message = _('Hello, World!')
    return render(request, 'template.html', {'message': message})
```

### In JavaScript

For client-side translations, you can:
1. Pass translations from the template
2. Use Django's JavaScript catalog

```javascript
// Example: Pass from template
const translations = {
    'save': '{{ _("Save") }}',
    'cancel': '{{ _("Cancel") }}'
};
```

---

## Adding New Translations

### Step 1: Mark Strings for Translation

In your templates:
```jinja2
{{ _('New String to Translate') }}
```

In Python code:
```python
from django.utils.translation import gettext as _
message = _('New String to Translate')
```

### Step 2: Update Translation Files

Edit the `.po` files for each language:

**Hindi:** `locale/hi/LC_MESSAGES/django.po`
```po
msgid "New String to Translate"
msgstr "अनुवाद करने के लिए नया स्ट्रिंग"
```

**Marathi:** `locale/mr/LC_MESSAGES/django.po`
```po
msgid "New String to Translate"
msgstr "भाषांतर करण्यासाठी नवीन स्ट्रिंग"
```

### Step 3: Compile Translations

Run the compilation script:
```bash
python compile_messages.py
```

This converts `.po` files to `.mo` files (machine-readable).

### Step 4: Restart the Server

```bash
# Stop the server (Ctrl+C)
# Then restart:
python manage.py runserver 1234
```

---

## Translation File Structure

```
smallcase_project/
├── locale/
│   ├── hi/                    # Hindi
│   │   └── LC_MESSAGES/
│   │       ├── django.po      # Editable translation file
│   │       └── django.mo      # Compiled (auto-generated)
│   └── mr/                    # Marathi
│       └── LC_MESSAGES/
│           ├── django.po      # Editable translation file
│           └── django.mo      # Compiled (auto-generated)
```

---

## Adding More Languages

To add a new language (e.g., Gujarati):

### 1. Update settings.py
```python
LANGUAGES = [
    ('en', 'English'),
    ('hi', 'हिन्दी (Hindi)'),
    ('mr', 'मराठी (Marathi)'),
    ('gu', 'ગુજરાતી (Gujarati)'),  # Add this
]
```

### 2. Create Directory Structure
```bash
mkdir locale\gu\LC_MESSAGES
```

### 3. Create django.po File
Copy `django.po` from Hindi or Marathi folder and translate the `msgstr` values.

### 4. Compile
```bash
python compile_messages.py
```

---

## Common Translation Strings

The following strings are already translated in Hindi and Marathi:

**Navigation:**
- Dashboard, Create Basket, Load Stocks, Update Prices
- Login, Logout, Sign Up

**Common Actions:**
- Save, Cancel, Submit, Edit, Delete, View
- Search, Filter, Sort

**UI Elements:**
- Name, Symbol, Price, Quantity, Total Value
- Date, Description, Actions

**Messages:**
- Loading..., Error, Success, Warning
- Yes, No, Confirm, Close

---

## Best Practices

### 1. **Mark All User-Facing Text**
Wrap ALL user-visible text in `_()`:
```jinja2
✓ Good: {{ _('Click here') }}
✗ Bad:  Click here
```

### 2. **Use Contexts for Ambiguous Words**
For words with multiple meanings:
```python
from django.utils.translation import pgettext

# Different contexts
pgettext('verb', 'Save')      # Save button
pgettext('noun', 'Save')      # Saved item
```

### 3. **Use Variables Properly**
```python
# Python
_('Hello, %(name)s!') % {'name': user.name}

# Jinja2
{{ _('Hello, %(name)s!') % {'name': user.name} }}
```

### 4. **Pluralization**
```python
from django.utils.translation import ngettext

ngettext(
    '%(count)d item',
    '%(count)d items',
    count
) % {'count': count}
```

---

## Testing Translations

### 1. **Switch Language**
- Click the language switcher (top-right)
- Select Hindi or Marathi
- Verify text changes

### 2. **Force Language in URL**
```
http://localhost:1234/en/    # English
http://localhost:1234/hi/    # Hindi
http://localhost:1234/mr/    # Marathi
```

### 3. **Test in Code**
```python
from django.utils import translation

with translation.override('hi'):
    print(_('Dashboard'))  # Will print: डैशबोर्ड
```

---

## Troubleshooting

### Translations Not Showing?

1. **Check .mo files exist:**
   ```bash
   dir locale\hi\LC_MESSAGES\
   dir locale\mr\LC_MESSAGES\
   ```
   You should see both `.po` and `.mo` files.

2. **Recompile:**
   ```bash
   python compile_messages.py
   ```

3. **Restart server:**
   Press Ctrl+C and run again:
   ```bash
   python manage.py runserver 1234
   ```

4. **Clear cache:**
   ```bash
   python manage.py shell
   >>> from django.core.cache import cache
   >>> cache.clear()
   ```

### Language Not Switching?

1. Check browser language settings
2. Clear browser cookies
3. Check LocaleMiddleware is in MIDDLEWARE list
4. Verify i18n_patterns in urls.py

---

## Production Deployment

### 1. **Always Compile Before Deploy**
```bash
python compile_messages.py
```

### 2. **Include .mo Files in Git**
While `.po` files are the source, `.mo` files should also be committed for production.

### 3. **Set Default Language**
In production settings, ensure:
```python
LANGUAGE_CODE = 'en'  # Or your preferred default
```

---

## Resources

- **Django i18n Documentation:** https://docs.djangoproject.com/en/stable/topics/i18n/
- **Jinja2 i18n Extension:** https://jinja.palletsprojects.com/en/stable/extensions/#i18n-extension
- **Translation Best Practices:** https://docs.djangoproject.com/en/stable/topics/i18n/translation/

---

## Quick Reference

| Task | Command |
|------|---------|
| Compile translations | `python compile_messages.py` |
| Test specific language | Visit `/hi/` or `/mr/` URL |
| Add new string | Edit `django.po` files |
| Add new language | Update `LANGUAGES` in settings |

---

**✅ Your project now supports English, Hindi, and Marathi!**

Users can switch languages anytime using the language switcher in the top-right corner of the page.
