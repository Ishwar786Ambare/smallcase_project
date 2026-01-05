# CSS Refactoring Plan

## Overview
This document outlines the CSS refactoring strategy to extract embedded styles from `.j2` templates into organized, centralized CSS files.

## Directory Structure

```
stocks/static/css/
├── base.css          # Core variables, resets, body styles
├── components.css    # Reusable components (header, footer, nav, buttons)
├── chat-widget.css   # Chat widget styles
├── pages/
│   ├── home.css      # Home page specific styles
│   ├── basket.css    # Basket related pages
│   ├── contact.css   # Contact page
│   └──i18n.css      # i18n demo page
```

## Files Status

###  Created Files
- ✅ `base.css` - Core theme variables and global styles
- ✅ `components.css` - Header, footer, navigation, buttons, theme toggle

### 🔄 To Be Created
- `chat-widget.css` - Extract 867 lines of chat widget CSS
- `pages/home.css` - Home page specific styles
- `pages/basket.css` - Basket detail, create, performance pages
- `pages/contact.css` - Contact form styles
- `pages/i18n.css` - i18n demo page styles

## CSS Extraction Map

### Current Embedded CSS Locations
1. `_styles.j2` (475 lines) → **Already organized, will reference external files**
2. `_chat_widget.j2` (Lines 112-979) → `chat-widget.css`
3. `home.j2` → `pages/home.css`
4. `basket_create.j2` → `pages/basket.css`
5. `basket_detail.j2` → `pages/basket.css`
6. `basket_performance.j2` → `pages/basket.css`
7. `contact.j2` → `pages/contact.css`
8. `i18n_demo.j2` → `pages/i18n.css`
9. `_language_switcher.j2` → Already in `components.css`

## Template Updates Required

### 1. Update `_styles.j2`
Replace embedded `<style>` tags with:
```html
{% load static %}
<link rel="stylesheet" href="{% static 'css/base.css' %}">
<link rel="stylesheet" href="{% static 'css/components.css' %}">
```

### 2. Update `_chat_widget.j2`
Replace embedded `<style>` tags with:
```html
{% load static %}
<link rel="stylesheet" href="{% static 'css/chat-widget.css' %}">
```

### 3. Update Page Templates
Each page template that has embedded CSS should include:
```html
{% load static %}
<link rel="stylesheet" href="{% static 'css/pages/page-name.css' %}">
```

## Benefits of Refactoring

1. **Reduced File Size**: Templates become cleaner and easier to read
2. **Better Caching**: CSS files are cached by browsers
3. **Easier Maintenance**: Update styles in one place
4. **Code Reusability**: Shared styles defined once
5. **Better Organization**: Logical separation of concerns
6. **Performance**: Parallel loading of CSS files
7. **Development Experience**: Easier to find and edit styles

## Implementation Steps

1. ✅ Create `static/css/` directory structure
2. ✅ Create `base.css` with variables and reset
3. ✅ Create `components.css` with reusable components
4. ⏳ Create `chat-widget.css` (extract from `_chat_widget.j2`)
5. ⏳ Create page-specific CSS files
6. ⏳ Update `_styles.j2` to reference external files
7. ⏳ Update templates to remove embedded styles
8. ⏳ Test all pages to ensure styles load correctly
9. ⏳ Run collectstatic for deployment

## Notes

- Keep CSS modular and component-based
- Use CSS custom properties (variables) for theming
- Maintain mobile-first responsive design
- Preserve all existing functionality
- Test both light and dark themes
- Ensure proper cascade order for overrides

## Next Steps

Run the automated extraction script or manually:
1. Extract chat widget CSS
2. Create page-specific CSS files
3. Update all template references
4. Test thoroughly
