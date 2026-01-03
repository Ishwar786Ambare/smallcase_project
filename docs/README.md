# StockBasket Documentation

Welcome to the StockBasket project documentation! This directory contains comprehensive guides for understanding and working with the codebase.

## 📚 Documentation Files

### 1. **TEMPLATE_STRUCTURE.md** 📄
**Complete template system guide**

Learn about the modular Jinja2 template architecture:
- Component descriptions (_header, _footer, _styles, _scripts)
- Usage examples and patterns
- Best practices for template development
- Migration guide for creating new components
- Troubleshooting common issues

**Read this if**: You're working with templates or creating new pages

---

### 2. **TEMPLATE_ARCHITECTURE.md** 🏗️
**Visual architecture diagrams**

Visual representations of the template system:
- Component architecture diagrams
- Template inheritance flow charts
- Request flow examples
- Theme system architecture
- File size comparisons
- Responsive design flows

**Read this if**: You want to understand how templates work together visually

---

### 3. **REFACTORING_SUMMARY.md** ✨
**Template refactoring overview**

Executive summary of the template refactoring:
- What changed and why
- Benefits achieved
- Metrics and improvements
- Testing performed
- Quick reference guide

**Read this if**: You want a high-level overview of the template system

---

### 4. **EMAIL_USERNAME_LOGIN.md** 🔐
**Authentication system documentation**

Details about the flexible login system:
- Custom User model implementation
- Email or Username authentication
- Custom authentication backend
- UserManager details
- Migration history
- Testing guidelines

**Read this if**: You're working with authentication or user management

---

## 🚀 Quick Start

### For New Developers

1. **Start with**: `REFACTORING_SUMMARY.md`
   - Get the big picture
   - Understand the benefits
   - See what changed

2. **Then read**: `TEMPLATE_STRUCTURE.md`
   - Learn how to use components
   - Understand the file organization
   - Follow best practices

3. **Optionally**: `TEMPLATE_ARCHITECTURE.md`
   - Dive deeper into architecture
   - Understand component relationships
   - See visual diagrams

### For Authentication Work

Read `EMAIL_USERNAME_LOGIN.md` to understand:
- How users can log in with email or username
- Custom User model setup
- Backend authentication flow

---

## 📖 Documentation Quick Reference

### Template Components

```
stocks/templates/stocks/
├── base.j2              - Main template
├── _header.j2           - Navigation
├── _footer.j2           - Footer
├── _theme_toggle.j2     - Theme switcher
├── _styles.j2           - Global CSS
└── _scripts.j2          - Global JS
```

### Creating a New Page

```jinja2
{% extends 'stocks/base.j2' %}

{% block title %}My Page{% endblock %}

{% block content %}
    <div class="container">
        <!-- Your content -->
    </div>
{% endblock %}
```

### Extending Styles

```jinja2
{% block css %}
{{ super() }}  <!-- Include parent styles -->
.custom-class {
    /* Your styles */
}
{% endblock %}
```

---

## 🎯 Common Tasks

### Adding a New Component
See `TEMPLATE_STRUCTURE.md` → "Migration Guide"

### Modifying Header/Footer
Edit `_header.j2` or `_footer.j2` directly

### Changing Theme Colors
Modify CSS variables in `_styles.j2`

### Adding Page-Specific Scripts
Use `{% block javascript %}` in your template

---

## 🔍 Finding Information

| I want to... | Read this |
|--------------|-----------|
| Understand template structure | TEMPLATE_STRUCTURE.md |
| See visual diagrams | TEMPLATE_ARCHITECTURE.md |
| Get a quick overview | REFACTORING_SUMMARY.md |
| Learn about authentication | EMAIL_USERNAME_LOGIN.md |
| Create a new component | TEMPLATE_STRUCTURE.md (Migration Guide) |
| Modify header/footer | TEMPLATE_STRUCTURE.md (Components) |
| Add custom styles | TEMPLATE_STRUCTURE.md (Usage Examples) |
| Troubleshoot templates | TEMPLATE_STRUCTURE.md (Common Issues) |

---

## 📝 Contributing to Documentation

When adding new features:

1. Update relevant documentation files
2. Add examples if introducing new patterns
3. Update diagrams in TEMPLATE_ARCHITECTURE.md if architecture changes
4. Keep this README.md updated with new docs

---

## 🏗️ Project Structure Overview

```
smallcase_project/
├── docs/                        # ← You are here
│   ├── README.md               # This file
│   ├── TEMPLATE_STRUCTURE.md   # Template guide
│   ├── TEMPLATE_ARCHITECTURE.md # Architecture diagrams
│   ├── REFACTORING_SUMMARY.md  # Refactoring overview
│   └── EMAIL_USERNAME_LOGIN.md # Auth documentation
├── stocks/
│   ├── templates/stocks/       # Template files
│   │   ├── base.j2
│   │   ├── _header.j2
│   │   ├── _footer.j2
│   │   ├── _theme_toggle.j2
│   │   ├── _styles.j2
│   │   ├── _scripts.j2
│   │   └── [page templates]
│   ├── models.py              # User, Stock, Basket models
│   ├── views.py               # View functions
│   ├── urls.py                # URL routing
│   ├── backends.py            # Custom auth backend
│   └── utils.py               # Helper functions
└── smallcase_project/
    └── settings.py            # Project settings
```

---

## 🎓 Best Practices

### Templates
- Use `{{ super() }}` when extending blocks
- Prefix component files with `_`
- Keep components focused and single-purpose
- Document new components

### Documentation
- Keep docs updated with code changes
- Use clear examples
- Include visual aids when helpful
- Link between related docs

### Code Organization
- Follow the modular structure
- Separate concerns (HTML, CSS, JS)
- Use meaningful file names
- Comment complex logic

---

## 🔗 Related Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [Django Best Practices](https://docs.djangoproject.com/en/stable/misc/design-philosophies/)

---

## 📧 Need Help?

- Check the relevant documentation file
- Look for examples in existing templates
- Review the troubleshooting sections
- Consult the diagrams in TEMPLATE_ARCHITECTURE.md

---

## 📊 Documentation Statistics

| File | Size | Lines | Purpose |
|------|------|-------|---------|
| TEMPLATE_STRUCTURE.md | 8.6 KB | ~250 | Component guide |
| TEMPLATE_ARCHITECTURE.md | 15.8 KB | ~450 | Visual diagrams |
| REFACTORING_SUMMARY.md | 8.4 KB | ~280 | Quick reference |
| EMAIL_USERNAME_LOGIN.md | 3.8 KB | ~130 | Auth system |
| **Total** | **36.6 KB** | **~1,110** | **Complete docs** |

---

**Last Updated**: January 3, 2026  
**Maintained By**: StockBasket Development Team  
**Status**: ✅ Up to date
