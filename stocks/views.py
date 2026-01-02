# stocks/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from decimal import Decimal
from .models import Stock, Basket, BasketItem
from .utils import (
    populate_indian_stocks,
    update_stock_prices,
    calculate_equal_weight_basket,
    create_basket_with_stocks
)
from django.middleware.csrf import get_token

def home(request):
    """Home page showing all stocks and baskets"""
    # Automatically update stock prices on home page load
    from .utils import update_stock_prices
    update_stock_prices()
    
    stocks = Stock.objects.all()
    baskets = Basket.objects.all().order_by('-created_at')
    
    # Calculate total invested and current value
    total_invested = baskets.aggregate(Sum('investment_amount'))['investment_amount__sum'] or 0
    total_current_value = sum(basket.get_total_value() for basket in baskets)
    total_profit_loss = total_current_value - float(total_invested)

    context = {
        'stocks': stocks,
        'baskets': baskets,
        'total_invested': total_invested,
        'total_current_value': total_current_value,
        'total_profit_loss': total_profit_loss,
    }
    return render(request, 'stocks/home.j2', context)


def populate_stocks(request):
    """Populate database with Indian stocks"""
    created_count = populate_indian_stocks()
    messages.success(request, f'Successfully added {created_count} new stocks!')
    return redirect('home')


def update_prices(request):
    """Update all stock prices"""
    count = update_stock_prices()
    messages.success(request, f'Successfully updated prices for {count} stocks!')
    return redirect('home')




def basket_create(request):
    """Create a new basket"""
    # Automatically update stock prices before creating basket
    from .utils import update_stock_prices
    update_stock_prices()
    
    stocks = Stock.objects.all()

    if request.method == 'POST':
        print('',request.POST)
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        investment_amount = request.POST.get('investment_amount')
        selected_stocks = request.POST.getlist('stocks')

        # Validation
        if not name or not investment_amount or not selected_stocks:
            messages.error(request, 'Please fill all required fields')
            return redirect('basket_create')
        
        # Validate minimum 2 stocks
        if len(selected_stocks) < 2:
            messages.error(request, 'A basket must contain at least 2 stocks')
            return redirect('basket_create')

        try:
            investment_amount = float(investment_amount)
            if investment_amount <= 0:
                messages.error(request, 'Investment amount must be positive')
                return redirect('basket_create')
        except ValueError:
            messages.error(request, 'Invalid investment amount')
            return redirect('basket_create')

        # Create basket
        basket = create_basket_with_stocks(
            name=name,
            description=description,
            investment_amount=investment_amount,
            stock_symbols=selected_stocks
        )

        if basket:
            messages.success(request, f'Basket "{name}" created successfully!')
            return redirect('basket_detail', basket_id=basket.id)
        else:
            messages.error(request, 'Failed to create basket. Please try again.')
            return redirect('basket_create')

    # Handle pre-filled values from duplication
    prefill_name = request.GET.get('name', '')
    prefill_description = request.GET.get('description', '')
    prefill_investment = request.GET.get('investment_amount', '50000')
    prefill_stocks = request.GET.get('stocks', '').split(',') if request.GET.get('stocks') else []
    
    context = {
        'stocks': stocks,
        'csrf_token': get_token(request),
        'prefill_name': prefill_name,
        'prefill_description': prefill_description,
        'prefill_investment': prefill_investment,
        'prefill_stocks': prefill_stocks,
    }
    return render(request, 'stocks/basket_create.j2', context)


def basket_detail(request, basket_id):
    """View basket details"""
    basket = get_object_or_404(Basket, id=basket_id)
    items = basket.items.select_related('stock').all()

    # Update stock prices
    for item in items:
        from .utils import fetch_stock_price
        price = fetch_stock_price(item.stock.symbol)
        if price:
            item.stock.current_price = Decimal(str(price))
            item.stock.save()

    # Calculate metrics
    total_current_value = basket.get_total_value()
    total_profit_loss = basket.get_profit_loss()
    profit_loss_percentage = basket.get_profit_loss_percentage()

    context = {
        'basket': basket,
        'items': items,
        'total_current_value': total_current_value,
        'total_profit_loss': total_profit_loss,
        'profit_loss_percentage': profit_loss_percentage,
    }
    return render(request, 'stocks/basket_detail.j2', context)


def basket_delete(request, basket_id):
    """Delete a basket"""
    basket = get_object_or_404(Basket, id=basket_id)
    basket_name = basket.name
    basket.delete()
    messages.success(request, f'Basket "{basket_name}" deleted successfully!')
    return redirect('home')


def preview_basket(request):
    """Preview basket allocation before creating"""
    if request.method == 'POST':
        investment_amount = request.POST.get('investment_amount')
        selected_stocks = request.POST.getlist('stocks')

        try:
            investment_amount = float(investment_amount)
            allocations = calculate_equal_weight_basket(selected_stocks, investment_amount)

            context = {
                'allocations': allocations,
                'investment_amount': investment_amount,
                'num_stocks': len(allocations),
            }
            return render(request, 'stocks/preview_basket.html', context)
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('basket_create')

    return redirect('basket_create')


def basket_item_edit(request, item_id):
    """Edit basket item - update weight or quantity, rebalancing other stocks to maintain 100% total"""
    from django.http import JsonResponse
    
    if request.method == 'POST':
        item = get_object_or_404(BasketItem, id=item_id)
        basket = item.basket
        
        try:
            update_type = request.POST.get('update_type')  # 'weight' or 'quantity'
            
            if update_type == 'weight':
                # Update weight, recalculate quantity
                new_weight = Decimal(request.POST.get('weight_percentage'))
                
                if new_weight <= 0 or new_weight > 100:
                    return JsonResponse({'success': False, 'error': 'Weight must be between 0 and 100'})
                
                old_weight = item.weight_percentage
                weight_change = new_weight - old_weight
                
                # Get all other items in the basket
                other_items = basket.items.exclude(id=item.id)
                
                if not other_items.exists():
                    # Only one stock in basket, just update it
                    item.weight_percentage = new_weight
                    item.allocated_amount = (new_weight / 100) * basket.investment_amount
                    # Round to whole number
                    item.quantity = int(item.allocated_amount / item.purchase_price)
                    # Adjust allocated amount based on whole quantity
                    item.allocated_amount = item.quantity * item.purchase_price
                    # Recalculate actual weight based on whole quantity
                    item.weight_percentage = (item.allocated_amount / basket.investment_amount) * 100
                    item.save()
                else:
                    # Calculate total weight of other items
                    other_total_weight = sum(other_item.weight_percentage for other_item in other_items)
                    
                    # Remaining weight for other stocks
                    remaining_weight = Decimal('100') - new_weight
                    
                    if remaining_weight < 0:
                        return JsonResponse({'success': False, 'error': 'Total weight cannot exceed 100%'})
                    
                    # Update current item
                    item.weight_percentage = new_weight
                    item.allocated_amount = (new_weight / 100) * basket.investment_amount
                    # Round to whole number
                    item.quantity = int(item.allocated_amount / item.purchase_price)
                    # Adjust allocated amount based on whole quantity
                    item.allocated_amount = item.quantity * item.purchase_price
                    # Recalculate actual weight based on whole quantity
                    item.weight_percentage = (item.allocated_amount / basket.investment_amount) * 100
                    item.save()
                    
                    # Redistribute remaining weight proportionally among other items
                    if other_total_weight > 0:
                        for other_item in other_items:
                            # Calculate proportional weight
                            proportion = other_item.weight_percentage / other_total_weight
                            other_item.weight_percentage = remaining_weight * proportion
                            other_item.allocated_amount = (other_item.weight_percentage / 100) * basket.investment_amount
                            # Round to whole number
                            other_item.quantity = int(other_item.allocated_amount / other_item.purchase_price)
                            # Adjust allocated amount based on whole quantity
                            other_item.allocated_amount = other_item.quantity * other_item.purchase_price
                            # Recalculate actual weight based on whole quantity
                            other_item.weight_percentage = (other_item.allocated_amount / basket.investment_amount) * 100
                            other_item.save()
                    else:
                        # If other items had 0 weight, distribute equally
                        equal_weight = remaining_weight / len(other_items)
                        for other_item in other_items:
                            other_item.weight_percentage = equal_weight
                            other_item.allocated_amount = (other_item.weight_percentage / 100) * basket.investment_amount
                            # Round to whole number
                            other_item.quantity = int(other_item.allocated_amount / other_item.purchase_price)
                            # Adjust allocated amount based on whole quantity
                            other_item.allocated_amount = other_item.quantity * other_item.purchase_price
                            # Recalculate actual weight based on whole quantity
                            other_item.weight_percentage = (other_item.allocated_amount / basket.investment_amount) * 100
                            other_item.save()
                
            elif update_type == 'quantity':
                # Update quantity, recalculate all weights (quantity must be whole number)
                # Other stocks keep their quantities, only weights change
                new_quantity = int(request.POST.get('quantity'))
                
                if new_quantity <= 0:
                    return JsonResponse({'success': False, 'error': 'Quantity must be positive'})
                
                # Update this item's quantity and allocated amount
                item.quantity = new_quantity
                item.allocated_amount = new_quantity * item.purchase_price
                item.save()
                
                # Calculate total allocated amount across all stocks (including updated one)
                all_items = basket.items.all()
                total_allocated = sum(Decimal(str(basket_item.quantity)) * basket_item.purchase_price 
                                     for basket_item in all_items)
                
                # Update basket investment amount to match actual holdings
                basket.investment_amount = total_allocated
                basket.save()
                
                # Recalculate weights for all items based on new total
                for basket_item in all_items:
                    # Keep quantity as is, just recalculate weight
                    basket_item.weight_percentage = (basket_item.allocated_amount / total_allocated) * 100 if total_allocated > 0 else 0
                    basket_item.save()
            
            else:
                return JsonResponse({'success': False, 'error': 'Invalid update type'})
            
            # Get all items with updated values to return
            all_items = basket.items.all()
            items_data = []
            for basket_item in all_items:
                items_data.append({
                    'id': basket_item.id,
                    'weight_percentage': float(basket_item.weight_percentage),
                    'quantity': int(basket_item.quantity),
                    'allocated_amount': float(basket_item.allocated_amount),
                    'current_value': basket_item.get_current_value(),
                    'profit_loss': basket_item.get_profit_loss(),
                })
            
            # Calculate updated portfolio metrics
            total_current_value = basket.get_total_value()
            total_profit_loss = basket.get_profit_loss()
            profit_loss_percentage = basket.get_profit_loss_percentage()
            
            # Return updated values for all items and basket
            return JsonResponse({
                'success': True,
                'items': items_data,
                'investment_amount': float(basket.investment_amount),
                'total_current_value': total_current_value,
                'total_profit_loss': total_profit_loss,
                'profit_loss_percentage': profit_loss_percentage,
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def basket_duplicate(request, basket_id):
    """Duplicate a basket - redirect to create page with pre-filled values"""
    basket = get_object_or_404(Basket, id=basket_id)
    
    # Get all stock symbols from the basket
    stock_symbols = ','.join([item.stock.symbol for item in basket.items.all()])
    
    # Redirect to create page with query parameters
    from django.http import HttpResponseRedirect
    from urllib.parse import urlencode
    
    params = {
        'duplicate': 'true',
        'name': f"{basket.name} (Copy)",
        'description': basket.description,
        'investment_amount': str(basket.investment_amount),
        'stocks': stock_symbols,
    }
    
    url = f"{request.build_absolute_uri('/basket/create/')}?{urlencode(params)}"
    return HttpResponseRedirect(url)


def basket_edit_investment(request, basket_id):
    """Edit basket investment amount - recalculates all allocations"""
    from django.http import JsonResponse
    
    if request.method == 'POST':
        basket = get_object_or_404(Basket, id=basket_id)
        
        try:
            new_investment = Decimal(request.POST.get('investment_amount'))
            
            if new_investment <= 0:
                return JsonResponse({'success': False, 'error': 'Investment amount must be positive'})
            
            old_investment = basket.investment_amount
            basket.investment_amount = new_investment
            basket.save()
            
            # Recalculate all items based on new investment amount
            items = basket.items.all()
            items_data = []
            
            for item in items:
                # Keep the same weight percentage, recalculate allocated amount
                item.allocated_amount = (item.weight_percentage / 100) * new_investment
                # Recalculate quantity based on new allocated amount (round to whole number)
                item.quantity = int(item.allocated_amount / item.purchase_price)
                
                # Adjust allocated amount to reflect whole quantity
                item.allocated_amount = item.quantity * item.purchase_price
                
                # Recalculate actual weight based on whole quantity
                item.weight_percentage = (item.allocated_amount / new_investment) * 100
                
                item.save()
                
                items_data.append({
                    'id': item.id,
                    'weight_percentage': float(item.weight_percentage),
                    'quantity': int(item.quantity),
                    'allocated_amount': float(item.allocated_amount),
                    'current_value': item.get_current_value(),
                    'profit_loss': item.get_profit_loss(),
                })
            
            # Calculate new totals
            total_current_value = basket.get_total_value()
            total_profit_loss = basket.get_profit_loss()
            
            return JsonResponse({
                'success': True,
                'investment_amount': float(new_investment),
                'items': items_data,
                'total_current_value': total_current_value,
                'total_profit_loss': total_profit_loss,
                'profit_loss_percentage': basket.get_profit_loss_percentage(),
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})