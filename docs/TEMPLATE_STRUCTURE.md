# Template Structure Documentation

## Overview
The Jinja2 templates have been refactored into a modular, component-based architecture for better maintainability, reusability, and organization.

## File Structure

```
stocks/templates/stocks/
├── base.j2                 # Main base template (17 lines - clean!)
├── _header.j2             # Header navigation component
├── _footer.j2             # Footer content component
├── _theme_toggle.j2       # Theme toggle button component
├── _styles.j2             # Base CSS styles
├── _scripts.j2            # Base JavaScript
├── home.j2                # Home page template
├── login.j2               # Login page template
├── signup.j2              # Signup page template
├── basket_create.j2       # Basket creation page
├── basket_detail.j2       # Basket detail page
└── basket_performance.j2  # Basket performance page
```

## Component Files (Partial Templates)

### 1. `_header.j2` - Header Component
**Purpose**: Navigation bar with logo, menu, and authentication controls

**Contents**:
- Logo with link to home/login
- Navigation menu (Dashboard, Create Basket, Load Stocks, Update Prices)
- User info display (username, email)
- Login/Signup buttons for anonymous users
- Logout button for authenticated users

**Conditional Logic**:
- Shows different content based on `request.user.is_authenticated`

---

### 2. `_footer.j2` - Footer Component
**Purpose**: Site-wide footer with links and information

**Contents**:
- **StockBasket Section**: Branding and social media links
- **Quick Links**: Navigation shortcuts (conditional based on auth)
- **Resources**: Documentation, guides, analysis
- **Support**: Contact, privacy policy, terms
- **Copyright & Disclaimer**: Legal information

**Features**:
- Responsive grid layout
- Hover effects on links
- Social media icons

---

### 3. `_theme_toggle.j2` - Theme Toggle Button
**Purpose**: Floating button for light/dark mode switching

**Contents**:
- Fixed position button (top-right)
- Icon and text that changes with theme
- Accessible with aria-label

---

### 4. `_styles.j2` - Base Styles
**Purpose**: Global CSS for layout, theme, and components

**Contents**:
- **CSS Variables**: Theme colors for light/dark mode
- **Reset Styles**: Universal box-sizing, margins, padding
- **Body Styles**: Background gradient, font-family
- **Component Styles**:
  - Header navigation
  - Footer layout
  - Theme toggle button
  - Buttons and links
- **Responsive Design**: Mobile breakpoints
- **Block Extension**: `{% block css %}` for page-specific styles

**Theme Variables**:
```css
--bg-gradient-start
--bg-gradient-end
--container-bg
--text-primary
--text-secondary
--card-bg
--card-border
--table-hover
--shadow-color
--border-color
```

---

### 5. `_scripts.j2` - Base JavaScript
**Purpose**: Core JavaScript functionality

**Contents**:
- **Theme Toggle Logic**:
  - Load saved theme from localStorage
  - Switch theme on button click
  - Update button icon/text
  - Save preference to localStorage
- **Block Extension**: `{% block javascript %}` for page-specific scripts

---

## Updated Base Template (`base.j2`)

**Before**: 496 lines of mixed HTML, CSS, and JavaScript
**After**: 17 lines of clean, organized includes

```jinja2
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    {% block header %}
    <!-- External libraries -->
    {% endblock %}
    
    {% include 'stocks/_styles.j2' %}
    
    <title>{% block title %}StockBasket{% endblock %}</title>
</head>
<body>
    {% include 'stocks/_header.j2' %}
    
    {% include 'stocks/_theme_toggle.j2' %}

    {% block content %}
    {% endblock %}
    
    {% include 'stocks/_footer.j2' %}
    
    {% include 'stocks/_scripts.j2' %}
</body>
</html>
```

## Benefits of This Structure

### 1. **Maintainability**
- Changes to header/footer only need to be made in one place
- Easy to locate specific components
- Clear separation of concerns

### 2. **Reusability**
- Components can be reused across different templates
- Consistent UI across all pages
- DRY (Don't Repeat Yourself) principle

### 3. **Readability**
- Base template is now ~17 lines instead of 496
- Clear component hierarchy
- Easy to understand page structure

### 4. **Testing & Debugging**
- Isolate issues to specific component files
- Test components independently
- Easier to modify without breaking other parts

### 5. **Performance**
- No performance impact (includes are processed server-side)
- Smaller file sizes per template
- Easier for developers to work with

### 6. **Extensibility**
- Easy to add new components
- Simple to override specific sections in child templates
- Supports theme customization

## How to Use in Child Templates

### Basic Usage
```jinja2
{% extends 'stocks/base.j2' %}

{% block title %}My Page Title{% endblock %}

{% block content %}
    <div class="container">
        <h1>My Content</h1>
    </div>
{% endblock %}
```

### With Custom Styles
```jinja2
{% extends 'stocks/base.j2' %}

{% block css %}
{{ super() }}  <!-- Include parent styles -->
.my-custom-class {
    color: red;
}
{% endblock %}

{% block content %}
    <div class="my-custom-class">Content</div>
{% endblock %}
```

### With Custom Scripts
```jinja2
{% extends 'stocks/base.j2' %}

{% block javascript %}
{{ super() }}  <!-- Include parent scripts -->
<script>
    console.log('My custom script');
</script>
{% endblock %}
```

## Component Naming Convention

All partial/component templates start with underscore `_`:
- `_header.j2`
- `_footer.j2`
- `_theme_toggle.j2`
- `_styles.j2`
- `_scripts.j2`

This indicates they are **not** standalone pages but **components** to be included.

## File Organization Best Practices

1. **Keep components focused**: Each file should have a single responsibility
2. **Use meaningful names**: File names should clearly indicate their purpose
3. **Document dependencies**: Note if a component relies on specific CSS/JS
4. **Maintain consistency**: Follow the same structure across all components
5. **Version control**: Track changes to components separately

## Migration Guide

If you need to create a new component:

1. Create a new file with `_` prefix: `_mycomponent.j2`
2. Add only the HTML/logic for that component
3. Include it in `base.j2` or other templates: `{% include 'stocks/_mycomponent.j2' %}`
4. Add any styles to `_styles.j2` or create `_mycomponent_styles.j2`
5. Document the component in this file

## Testing Checklist

After making changes to components:

- [ ] Home page loads correctly
- [ ] Login page displays properly
- [ ] Header shows correct menu items (authenticated/unauthenticated)
- [ ] Footer displays all sections
- [ ] Theme toggle works (light ↔ dark)
- [ ] Mobile responsive layout works
- [ ] All links are functional
- [ ] No console errors
- [ ] Styles apply correctly
- [ ] Page-specific styles don't conflict with base styles

## Common Issues & Solutions

### Issue: Custom styles not applying
**Solution**: Make sure to use `{{ super() }}` in your CSS block to include parent styles

### Issue: JavaScript not working
**Solution**: Check if you're including the base scripts with `{{ super() }}` in your javascript block

### Issue: Component not displaying
**Solution**: Verify the include path is correct and the file exists in `stocks/templates/stocks/`

### Issue: Theme not persisting
**Solution**: Check browser localStorage and ensure theme toggle script is loaded

## Future Enhancements

Potential improvements to the template structure:

1. **Message Components**: Extract alert/message display to `_messages.j2`
2. **Form Components**: Create reusable form field templates
3. **Card Components**: Extract card layouts to separate files
4. **Button Components**: Standardize button styles and variants
5. **Modal Components**: Create reusable modal dialogs
6. **Loading Components**: Add loading spinners/skeletons

## Conclusion

This modular template structure provides a solid foundation for building and maintaining the StockBasket application. It follows Django/Jinja2 best practices and makes the codebase more professional and scalable.
