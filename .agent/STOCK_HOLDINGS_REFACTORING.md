# Stock Holdings Table Refactoring

## Overview
Refactored the "Stock Holdings" table in the basket detail page to use Django's template loader pattern for better code organization and reusability.

## Changes Made

### 1. Created Separate Template Partial
**File:** `stocks/templates/stocks/_stock_holdings_table.j2`

- Extracted the entire Stock Holdings table HTML into a separate template file
- Includes the table header, body with all stock items, totals row, and note box
- Follows Django naming convention with underscore prefix for partial templates

### 2. Updated `basket_detail` View
**File:** `stocks/views.py`

Modified the `basket_detail` function to:
- Import `get_template` from `django.template.loader`
- Load the partial template using `get_template("stocks/_stock_holdings_table.j2")`
- Prepare a context dictionary with required data (basket, items, metrics)
- Render the template partial to HTML string using `template.render(context)`
- Pass the rendered HTML to the main template via context

**Code Pattern Used:**
```python
from django.template.loader import get_template

# Load the template partial
stock_holdings_template = get_template("stocks/_stock_holdings_table.j2")

# Prepare context
holdings_context = {
    'basket': basket,
    'items': items,
    'total_current_value': metrics['total_current_value'],
    'total_profit_loss': metrics['total_profit_loss'],
}

# Render to HTML string
stock_holdings_html = stock_holdings_template.render(holdings_context)
```

### 3. Updated Main Template
**File:** `stocks/templates/stocks/basket_detail.j2`

- Replaced the inline table HTML (93 lines) with a single line
- Used `{{ stock_holdings_html|safe }}` to render the pre-rendered HTML
- The `|safe` filter prevents Django from escaping the HTML

## Benefits

1. **Separation of Concerns**: Table HTML is now in its own file, making it easier to maintain
2. **Reusability**: The partial template can be reused in other views if needed
3. **Cleaner Code**: Main template is now ~90 lines shorter and more readable
4. **Follows Django Best Practices**: Uses the recommended `get_template()` pattern from Django 6.0 documentation
5. **Server-Side Rendering**: Template is rendered on the server, maintaining all Django template features

## Testing

The implementation maintains all existing functionality:
- ✅ Table displays all stock holdings correctly
- ✅ Editable weight and quantity fields work as before
- ✅ JavaScript functions (enableEdit, saveEdit, cancelEdit) continue to work
- ✅ All styling and CSS classes are preserved
- ✅ Dynamic data binding remains functional

## Django Documentation Reference

This implementation follows the pattern described in:
https://docs.djangoproject.com/en/6.0/topics/templates/#django.template.loader.get_template

```python
from django.template.loader import get_template

# Load an entire template
template = get_template("template.html")

# Render with context
html = template.render(context)
```

## Future Enhancements

This pattern can be extended to:
- Load specific template fragments using `template.html#partial_name` syntax
- Create more reusable components for other sections
- Implement AJAX partial updates for better performance
