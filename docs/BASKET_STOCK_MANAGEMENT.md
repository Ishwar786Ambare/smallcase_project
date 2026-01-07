# Basket Stock Management Utility Functions

This document explains how to use the utility functions for managing stocks in baskets.

## Available Functions

### 1. `remove_stock_from_basket(basket_id, stock_id)`

**⚠️ IMPORTANT:** This function only removes the stock from the basket (removes the BasketItem relationship). The Stock object itself remains in the database and can still be used by other baskets.

Removes a stock from a basket and automatically recalculates all values.

**What it does:**
- Removes the stock (BasketItem) from the basket
- Recalculates the total investment amount
- Redistributes weight percentages among remaining stocks
- Updates allocated amounts for remaining stocks

**Parameters:**
- `basket_id` (int): The ID of the basket
- `stock_id` (int): The ID of the stock to remove

**Returns:**
A dictionary containing:
- `success` (bool): Whether the operation was successful
- `message` (str): Success or error message
- `basket` (Basket object or None): Updated basket object
- `deleted_amount` (float): Amount that was removed from basket
- `remaining_stocks` (int): Number of stocks remaining (only on success)
- `new_investment_amount` (float): New total investment amount (only on success)

**Example Usage:**

```python
from stocks.utils import remove_stock_from_basket

# Remove stock with ID 5 from basket with ID 7
result = remove_stock_from_basket(basket_id=7, stock_id=5)

if result['success']:
    print(result['message'])
    print(f"Deleted amount: ₹{result['deleted_amount']}")
    print(f"Remaining stocks: {result['remaining_stocks']}")
    print(f"New investment amount: ₹{result['new_investment_amount']}")
else:
    print(f"Error: {result['message']}")
```

**In a Django View:**

```python
from django.http import JsonResponse
from stocks.utils import remove_stock_from_basket

def delete_basket_stock(request, basket_id, stock_id):
    result = remove_stock_from_basket(basket_id, stock_id)
    
    if result['success']:
        return JsonResponse({
            'status': 'success',
            'message': result['message'],
            'deleted_amount': result['deleted_amount'],
            'remaining_stocks': result.get('remaining_stocks', 0),
            'new_investment_amount': result.get('new_investment_amount', 0)
        })
    else:
        return JsonResponse({
            'status': 'error',
            'message': result['message']
        }, status=400)
```

---

### 2. `recalculate_basket_weights(basket_id)`

Recalculates weight percentages for all stocks in a basket based on current allocated amounts.

**What it does:**
- Ensures all weight percentages sum to 100%
- Updates basket investment amount to match total allocated amounts
- Useful after manual adjustments to basket items

**Parameters:**
- `basket_id` (int): The ID of the basket to recalculate

**Returns:**
A dictionary containing:
- `success` (bool): Whether the operation was successful
- `message` (str): Success or error message
- `total_investment` (float): Total investment amount (only on success)

**Example Usage:**

```python
from stocks.utils import recalculate_basket_weights

# Recalculate weights for basket with ID 7
result = recalculate_basket_weights(basket_id=7)

if result['success']:
    print(result['message'])
    print(f"Total investment: ₹{result['total_investment']}")
else:
    print(f"Error: {result['message']}")
```

---

## Complete Example: Delete Stock and Show Updated Basket

```python
from stocks.utils import remove_stock_from_basket
from stocks.models import Basket

# Delete a stock
basket_id = 7
stock_id = 5

result = remove_stock_from_basket(basket_id, stock_id)

if result['success']:
    basket = result['basket']
    
    print(f"✓ {result['message']}")
    print(f"\nBasket Details:")
    print(f"  Name: {basket.name}")
    print(f"  Investment Amount: ₹{basket.investment_amount}")
    print(f"  Remaining Stocks: {result['remaining_stocks']}")
    
    # Show remaining stocks
    if result['remaining_stocks'] > 0:
        print(f"\nRemaining Stocks:")
        for item in basket.items.all():
            print(f"  - {item.stock.name}")
            print(f"    Weight: {item.weight_percentage:.2f}%")
            print(f"    Allocated: ₹{item.allocated_amount}")
            print(f"    Quantity: {item.quantity}")
else:
    print(f"✗ Error: {result['message']}")
```

---

## Integration with Views

Here's how you might integrate this into your existing views:

```python
# In stocks/views.py
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .utils import remove_stock_from_basket
from .models import Basket

@require_http_methods(["DELETE", "POST"])
def basket_stock_delete(request, basket_id, stock_id):
    """Delete a stock from a basket"""
    
    # Optional: Check user permissions
    basket = get_object_or_404(Basket, id=basket_id)
    if basket.user and basket.user != request.user:
        return JsonResponse({
            'status': 'error',
            'message': 'You do not have permission to modify this basket.'
        }, status=403)
    
    # Delete the stock
    result = remove_stock_from_basket(basket_id, stock_id)
    
    if result['success']:
        return JsonResponse({
            'status': 'success',
            'message': result['message'],
            'data': {
                'deleted_amount': result['deleted_amount'],
                'remaining_stocks': result.get('remaining_stocks', 0),
                'new_investment_amount': result.get('new_investment_amount', 0)
            }
        })
    else:
        return JsonResponse({
            'status': 'error',
            'message': result['message']
        }, status=400)
```

---

## URL Pattern Example

```python
# In stocks/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # ... other patterns ...
    path('basket/<int:basket_id>/stock/<int:stock_id>/delete/', 
         views.basket_stock_delete, 
         name='basket_stock_delete'),
]
```

---

## Notes

1. **Automatic Recalculation**: The `remove_stock_from_basket` function automatically recalculates all values, so you don't need to call `recalculate_basket_weights` separately.

2. **Empty Baskets**: If you delete the last stock from a basket, the investment amount will be set to 0, but the basket itself will not be deleted.

3. **Error Handling**: Both functions return detailed error messages if something goes wrong, making it easy to provide feedback to users.

4. **Transaction Safety**: Consider wrapping these operations in database transactions for production use:

```python
from django.db import transaction

@transaction.atomic
def delete_stock_safely(basket_id, stock_id):
    return remove_stock_from_basket(basket_id, stock_id)
```

