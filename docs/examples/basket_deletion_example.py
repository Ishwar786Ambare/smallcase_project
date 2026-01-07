"""
Example: Deleting a Stock from a Basket
========================================

This example demonstrates how the remove_stock_from_basket utility function works.
"""

from stocks.utils import remove_stock_from_basket
from stocks.models import Basket, BasketItem

# ============================================================================
# SCENARIO: Delete "HDFC Bank" from "Blue Chip" basket
# ============================================================================

# BEFORE DELETION:
# ----------------
# Basket: Blue Chip
# Investment Amount: ₹100,000
# Number of Stocks: 5
#
# Stock Holdings:
# 1. Reliance Industries    - Weight: 20% - Allocated: ₹20,000 - Qty: 8
# 2. TCS                     - Weight: 20% - Allocated: ₹20,000 - Qty: 6
# 3. HDFC Bank              - Weight: 20% - Allocated: ₹20,000 - Qty: 12  ← TO DELETE
# 4. Infosys                - Weight: 20% - Allocated: ₹20,000 - Qty: 9
# 5. ICICI Bank             - Weight: 20% - Allocated: ₹20,000 - Qty: 11

# Execute deletion
basket_id = 7  # Blue Chip basket
stock_id = 3   # HDFC Bank

result = remove_stock_from_basket(basket_id, stock_id)

# AFTER DELETION:
# ---------------
# Basket: Blue Chip
# Investment Amount: ₹80,000  ← Reduced by ₹20,000
# Number of Stocks: 4         ← Reduced by 1
#
# Stock Holdings:
# 1. Reliance Industries    - Weight: 25% - Allocated: ₹20,000 - Qty: 8  ← Weight increased
# 2. TCS                     - Weight: 25% - Allocated: ₹20,000 - Qty: 6  ← Weight increased
# 3. Infosys                - Weight: 25% - Allocated: ₹20,000 - Qty: 9  ← Weight increased
# 4. ICICI Bank             - Weight: 25% - Allocated: ₹20,000 - Qty: 11 ← Weight increased
#
# HDFC Bank has been removed!

# Result object:
print(result)
# {
#     'success': True,
#     'message': 'Successfully deleted HDFC Bank from basket. Investment amount reduced by ₹20,000.00.',
#     'basket': <Basket: Blue Chip>,
#     'deleted_amount': 20000.0,
#     'remaining_stocks': 4,
#     'new_investment_amount': 80000.0
# }

# ============================================================================
# WHAT HAPPENED AUTOMATICALLY:
# ============================================================================
# 
# 1. ✅ BasketItem for HDFC Bank was deleted from database
# 2. ✅ Basket investment_amount updated: ₹100,000 → ₹80,000
# 3. ✅ Weights recalculated for remaining stocks: 20% → 25% each
# 4. ✅ All weights still sum to 100%
# 5. ✅ Allocated amounts remain unchanged (only weights adjusted)
# 6. ✅ Quantities remain unchanged
#
# ============================================================================


# ============================================================================
# EXAMPLE 2: Delete last stock from basket
# ============================================================================

# BEFORE:
# Basket: Tech Stocks
# Investment Amount: ₹50,000
# Number of Stocks: 1
# - TCS - Weight: 100% - Allocated: ₹50,000 - Qty: 15

result = remove_stock_from_basket(basket_id=8, stock_id=2)

# AFTER:
# Basket: Tech Stocks
# Investment Amount: ₹0
# Number of Stocks: 0
# (Empty basket)

print(result)
# {
#     'success': True,
#     'message': 'Successfully deleted TCS. Basket is now empty.',
#     'basket': <Basket: Tech Stocks>,
#     'deleted_amount': 50000.0,
#     'remaining_stocks': 0
# }


# ============================================================================
# EXAMPLE 3: Error handling - Stock not in basket
# ============================================================================

result = remove_stock_from_basket(basket_id=7, stock_id=999)

print(result)
# {
#     'success': False,
#     'message': 'Stock not found in this basket.',
#     'basket': None,
#     'deleted_amount': 0
# }


# ============================================================================
# EXAMPLE 4: Error handling - Basket not found
# ============================================================================

result = remove_stock_from_basket(basket_id=999, stock_id=5)

print(result)
# {
#     'success': False,
#     'message': 'Basket with ID 999 not found.',
#     'basket': None,
#     'deleted_amount': 0
# }


# ============================================================================
# PRACTICAL USAGE IN VIEW
# ============================================================================

def delete_basket_stock_view(request, basket_id, stock_id):
    """
    View to handle stock deletion from basket
    """
    from django.http import JsonResponse
    from django.views.decorators.http import require_http_methods
    
    # Delete the stock
    result = remove_stock_from_basket(basket_id, stock_id)
    
    if result['success']:
        # Success response
        return JsonResponse({
            'status': 'success',
            'message': result['message'],
            'data': {
                'deleted_amount': result['deleted_amount'],
                'remaining_stocks': result.get('remaining_stocks', 0),
                'new_investment_amount': result.get('new_investment_amount', 0),
                'basket_id': basket_id
            }
        })
    else:
        # Error response
        return JsonResponse({
            'status': 'error',
            'message': result['message']
        }, status=400)


# ============================================================================
# JAVASCRIPT FRONTEND EXAMPLE
# ============================================================================

"""
// Delete stock button click handler
document.querySelectorAll('.delete-stock-btn').forEach(btn => {
    btn.addEventListener('click', async function() {
        const basketId = this.dataset.basketId;
        const stockId = this.dataset.stockId;
        const stockName = this.dataset.stockName;
        
        if (!confirm(`Delete ${stockName} from basket?`)) {
            return;
        }
        
        try {
            const response = await fetch(`/basket/${basketId}/stock/${stockId}/delete/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                // Show success message
                showNotification(data.message, 'success');
                
                // Update UI
                document.querySelector(`#stock-${stockId}`).remove();
                document.querySelector('#investment-amount').textContent = 
                    `₹${data.data.new_investment_amount.toLocaleString()}`;
                document.querySelector('#stock-count').textContent = 
                    data.data.remaining_stocks;
                
                // Reload basket details to show updated weights
                location.reload();
            } else {
                showNotification(data.message, 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showNotification('Failed to delete stock', 'error');
        }
    });
});
"""

