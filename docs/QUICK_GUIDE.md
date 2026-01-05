# Quick Access Guide - Refactored Code Structure

## 📂 Where Everything Is

### CSS Files
```
stocks/static/css/
├── base.css                    ← Theme variables, resets
├── components.css              ← Header, footer, nav, buttons
├── chat-widget.css             ← Chat widget styles
└── pages/
    ├── home.css               ← (To be created)
    ├── basket-detail.css      ← (To be created)  
    └── contact.css            ← (To be created)
```

### JavaScript Files
```
stocks/static/js/
├── common.js                   ← Theme toggle, alerts
├── chat-widget.js              ← Chat functionality
├── language-switcher.js        ← Language dropdown
└── pages/
    ├── home.js                ← DataTable initialization
    ├── basket-detail.js       ← Chart, editing, share
    └── basket-create.js       ← Form validation
```

## 🎨 How to Add/Edit Styles

### Option 1: Edit Existing CSS File
```bash
# For global styles (colors, buttons, etc.)
code stocks/static/css/components.css

# For theme variables
code stocks/static/css/base.css

# For chat widget
code stocks/static/css/chat-widget.css
```

### Option 2: Create New Page CSS
1. Create file: `stocks/static/css/pages/your-page.css`
2. Add to template:
```html
{% block css %}
<link rel="stylesheet" href="{{ static('css/pages/your-page.css') }}">
{% endblock %}
```

## 💻 How to Add/Edit JavaScript

### Option 1: Edit Existing JS File
```bash
# For global utilities (theme, alerts)
code stocks/static/js/common.js

# For chat
code stocks/static/js/chat-widget.js

# For page-specific logic
code stocks/static/js/pages/home.js
code stocks/static/js/pages/basket-detail.js
```

### Option 2: Create New Page JS
1. Create file: `stocks/static/js/pages/your-page.js`
2. Add to template:
```html
{% block javascript %}
<script src="{{ static('js/pages/your-page.js') }}"></script>
{% endblock %}
```

## 🔍 Find What You Need

### "Where is the theme toggle code?"
→ `stocks/static/js/common.js`

### "Where are button styles?"
→ `stocks/static/css/components.css`

### "Where is the chat widget styled?"
→ `stocks/static/css/chat-widget.css`

### "Where is the chat logic?"
→ `stocks/static/js/chat-widget.js`

### "Where is the DataTable initialization?"
→ `stocks/static/js/pages/home.js`

### "Where is the basket chart code?"
→ `stocks/static/js/pages/basket-detail.js`

### "Where are theme colors defined?"
→ `stocks/static/css/base.css` (CSS variables at top)

## 🚀 Common Tasks

### Change Theme Colors
```css
/* Edit: stocks/static/css/base.css */

:root[data-theme="light"] {
    --bg-gradient-start: #667eea;  /* Change this */
    --bg-gradient-end: #764ba2;    /* And this */
    --text-primary: #333333;
    /* ...more variables... */
}
```

### Add New Button Style
```css
/* Edit: stocks/static/css/components.css */

.btn-yourname {
    background: #your-color;
    color: white;
    /* ...styles... */
}
```

### Add New Utility Function
```javascript
// Edit: stocks/static/js/common.js

function yourUtilityFunction() {
    // Your code here
}
```

### Modify Chat Widget Behavior
```javascript
// Edit: stocks/static/js/chat-widget.js

// Find the function you want to modify
// For example, sendMessage(), getAIResponse(), etc.
```

## 📝 Template Syntax

### Load CSS
```html
<!-- In any .j2 template -->
{% block css %}
<link rel="stylesheet" href="{{ static('css/yourfile.css') }}">
{% endblock %}
```

### Load JavaScript
```html
<!-- In any .j2 template -->
{% block javascript %}
<script src="{{ static('js/yourfile.js') }}"></script>
{% endblock %}
```

## 🧪 Testing Your Changes

### 1. Edit CSS/JS file
### 2. Refresh browser (Ctrl + Shift + R to bypass cache)
### 3. Check browser console for errors (F12)
### 4. Verify functionality works

## 📦 Before Deploying

```bash
# Collect all static files for production
python manage.py collectstatic --no-input
```

## 🔄 Restoring Backups (If Needed)

All modified templates have backups:
```bash
# List backups
ls stocks/templates/stocks/*_backup.j2
ls stocks/templates/stocks/*_js_backup.j2

# Restore a file
cp stocks/templates/stocks/home_js_backup.j2 stocks/templates/stocks/home.j2
```

## 📚 Full Documentation

For complete details, see:
- `docs/CSS_REFACTORING_SUMMARY.md`
- `docs/JS_REFACTORING_SUMMARY.md`
- `docs/COMPLETE_REFACTORING_SUMMARY.md`

## ✨ Quick Tips

1. **CSS Changes**: Edit the CSS file and refresh browser
2. **JS Changes**: Edit the JS file and hard refresh (Ctrl + Shift + R)
3. **New Page**: Create CSS/JS in `pages/` folder
4. **Global Utility**: Add to `common.js` or `components.css`
5. **Testing**: Always check browser console (F12)

---

**Need Help?**
- Check the docs folder
- Look at exist files as examples
- Browser DevTools is your friend (F12)
