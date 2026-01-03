# stocks/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Prefetch
from django.core.cache import cache
from decimal import Decimal
from .models import Stock, Basket, BasketItem
from .utils import (
    populate_indian_stocks,
    update_stock_prices,
    calculate_equal_weight_basket,
    create_basket_with_stocks
)
from django.middleware.csrf import get_token

User = get_user_model()  # Get the custom User model


# ============ Stock and Basket Views ============

# @login_required
def home(request):
    """Home page showing all stocks and baskets"""
    # OPTIMIZATION: Remove automatic price updates on page load
    # Users can manually trigger updates with the "Update Prices" button
    
    # OPTIMIZATION: Use select_related and prefetch_related to reduce queries
    stocks = Stock.objects.all().order_by('symbol')
    
    baskets = []
    total_invested = 0
    total_current_value = 0
    total_profit_loss = 0
    
    if request.user.is_authenticated:
        # Filter baskets to show only user's baskets
        baskets = Basket.objects.filter(user=request.user).prefetch_related(
            Prefetch('items', queryset=BasketItem.objects.select_related('stock'))
        ).order_by('-created_at')
        
        # Calculate total invested using database aggregation
        total_invested = baskets.aggregate(Sum('investment_amount'))['investment_amount__sum'] or 0
        
        # OPTIMIZATION: Cache basket calculations
        for basket in baskets:
            cache_key = f'basket_value_{basket.id}_{basket.updated_at.timestamp()}'
            basket_value = cache.get(cache_key)
            if basket_value is None:
                basket_value = basket.get_total_value()
                cache.set(cache_key, basket_value, 300)  # Cache for 5 minutes
            total_current_value += basket_value
        
        total_profit_loss = total_current_value - float(total_invested)

    context = {
        'stocks': stocks,
        'baskets': baskets,
        'total_invested': total_invested,
        'total_current_value': total_current_value,
        'total_profit_loss': total_profit_loss,
    }
    return render(request, 'stocks/home.j2', context)


@login_required
def populate_stocks(request):
    """Populate database with Indian stocks"""
    created_count = populate_indian_stocks()
    messages.success(request, f'Successfully added {created_count} new stocks!')
    return redirect('home')


@login_required
def update_prices(request):
    """Update all stock prices"""
    count = update_stock_prices()
    messages.success(request, f'Successfully updated prices for {count} stocks!')
    # Clear basket value cache after price update
    cache.clear()
    return redirect('home')




@login_required
def basket_create(request):
    """Create a new basket"""
    # OPTIMIZATION: Don't auto-update prices, let users trigger manually
    
    stocks = Stock.objects.all().order_by('symbol')

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
            stock_symbols=selected_stocks,
            user=request.user
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


@login_required
def basket_detail(request, basket_id):
    """View basket details"""
    basket = get_object_or_404(Basket, id=basket_id, user=request.user)
    # OPTIMIZATION: Use select_related to avoid N+1 queries
    items = basket.items.select_related('stock').all()

    # OPTIMIZATION: Update prices in bulk only if they're stale (>5 mins old)
    from datetime import timedelta
    from django.utils import timezone
    from .utils import update_stock_prices_bulk
    
    stale_stocks = [
        item.stock for item in items
        if not item.stock.current_price or 
        item.stock.last_updated < timezone.now() - timedelta(minutes=5)
    ]
    
    if stale_stocks:
        symbols = [stock.symbol for stock in stale_stocks]
        update_stock_prices_bulk(symbols)
        # Refresh items from database to get updated prices
        items = basket.items.select_related('stock').all()

    # Calculate metrics with caching
    cache_key = f'basket_metrics_{basket.id}_{basket.updated_at.timestamp()}'
    metrics = cache.get(cache_key)
    
    if metrics is None:
        total_current_value = basket.get_total_value()
        total_profit_loss = basket.get_profit_loss()
        profit_loss_percentage = basket.get_profit_loss_percentage()
        metrics = {
            'total_current_value': total_current_value,
            'total_profit_loss': total_profit_loss,
            'profit_loss_percentage': profit_loss_percentage,
        }
        cache.set(cache_key, metrics, 300)  # Cache for 5 minutes
    
    context = {
        'basket': basket,
        'items': items,
        **metrics
    }
    return render(request, 'stocks/basket_detail.j2', context)


@login_required
def basket_chart_data(request, basket_id):
    """API endpoint to get basket performance vs indices data for chart"""
    from django.http import JsonResponse
    from .utils import fetch_index_historical_data, calculate_basket_historical_performance, INDIAN_INDICES
    
    basket = get_object_or_404(Basket, id=basket_id, user=request.user)
    
    # Get period from request, default to 1 month
    period = request.GET.get('period', '1m')
    
    # Validate period
    valid_periods = ['1d', '7d', '1m', '3m', '6m', '1y', '3y', '5y']
    if period not in valid_periods:
        period = '1m'
    
    # OPTIMIZATION: Cache chart data for 1 hour
    cache_key = f'chart_data_{basket.id}_{period}'
    cached_data = cache.get(cache_key)
    if cached_data:
        return JsonResponse(cached_data)
    
    # Fetch Nifty 50 historical data
    nifty_data = fetch_index_historical_data('^NSEI', period)
    
    # Fetch basket historical performance
    basket_data = calculate_basket_historical_performance(basket, period)
    
    if not nifty_data or not basket_data:
        return JsonResponse({
            'success': False,
            'error': 'Unable to fetch historical data'
        })
    
    # Normalize both to indexed values starting at 100
    # This shows: "If I invested ₹100, what would it be worth now?"
    if nifty_data:
        nifty_start_value = nifty_data[0]['value']
        nifty_indexed = [
            {
                'date': item['date'],
                'value': (item['value'] / nifty_start_value) * 100  # Index to 100
            }
            for item in nifty_data
        ]
    else:
        nifty_indexed = []
    
    if basket_data:
        basket_start_value = basket_data[0]['value']
        basket_indexed = [
            {
                'date': item['date'],
                'value': (item['value'] / basket_start_value) * 100  # Index to 100
            }
            for item in basket_data
        ]
    else:
        basket_indexed = []
    
    # Align dates (use dates where both have data)
    nifty_dates = {item['date']: item['value'] for item in nifty_indexed}
    basket_dates = {item['date']: item['value'] for item in basket_indexed}
    common_dates = sorted(set(nifty_dates.keys()) & set(basket_dates.keys()))
    
    # Build aligned datasets
    aligned_nifty = [nifty_dates[date] for date in common_dates]
    aligned_basket = [basket_dates[date] for date in common_dates]
    
    # Ensure both start at exactly 100 (re-normalize to first common date)
    if aligned_basket and aligned_nifty:
        first_basket = aligned_basket[0]
        first_nifty = aligned_nifty[0]
        
        # Re-index both to start at exactly 100
        aligned_basket = [(val / first_basket) * 100 for val in aligned_basket]
        aligned_nifty = [(val / first_nifty) * 100 for val in aligned_nifty]
    
    # Calculate final values for summary
    final_basket_value = aligned_basket[-1] if aligned_basket else 100
    final_nifty_value = aligned_nifty[-1] if aligned_nifty else 100
    
    response_data = {
        'success': True,
        'period': period,
        'labels': common_dates,
        'datasets': {
            'basket': {
                'label': basket.name,
                'data': aligned_basket,
                'color': 'rgb(102, 126, 234)',
                'final_value': round(final_basket_value, 2)
            },
            'nifty': {
                'label': 'Nifty 50',
                'data': aligned_nifty,
                'color': 'rgb(255, 99, 132)',
                'final_value': round(final_nifty_value, 2)
            }
        },
        'summary': {
            'basket_final': round(final_basket_value, 2),
            'nifty_final': round(final_nifty_value, 2),
            'basket_return_pct': round(final_basket_value - 100, 2),
            'nifty_return_pct': round(final_nifty_value - 100, 2)
        }
    }
    
    # Cache for 1 hour
    cache.set(cache_key, response_data, 3600)
    
    return JsonResponse(response_data)


@login_required
def basket_performance(request, basket_id):
    """Performance analysis page showing historical returns"""
    from datetime import datetime, timedelta
    from .utils import fetch_index_historical_data, calculate_basket_historical_performance
    
    basket = get_object_or_404(Basket, id=basket_id, user=request.user)
    
    # OPTIMIZATION: Cache performance data for 1 hour
    cache_key = f'performance_{basket.id}'
    performance_data = cache.get(cache_key)
    
    if performance_data is None:
        # Define time periods to analyze
        periods = [
            {'code': '1m', 'label': '1 Month', 'days': 30},
            {'code': '3m', 'label': '3 Months', 'days': 90},
            {'code': '6m', 'label': '6 Months', 'days': 180},
            {'code': '1y', 'label': '1 Year', 'days': 365},
            {'code': '2y', 'label': '2 Years', 'days': 730},
            {'code': '3y', 'label': '3 Years', 'days': 1095},
            {'code': '5y', 'label': '5 Years', 'days': 1825},
        ]
        
        performance_data = []
        
        for period in periods:
            # Fetch historical data for this period
            basket_hist = calculate_basket_historical_performance(basket, period['code'])
            nifty_hist = fetch_index_historical_data('^NSEI', period['code'])
            
            if basket_hist and nifty_hist:
                # Create date dictionaries for alignment
                basket_dates = {item['date']: item['value'] for item in basket_hist}
                nifty_dates = {item['date']: item['value'] for item in nifty_hist}
                
                # Find common dates
                common_dates = sorted(set(basket_dates.keys()) & set(nifty_dates.keys()))
                
                if common_dates:
                    # Get aligned values
                    basket_values = [basket_dates[date] for date in common_dates]
                    nifty_values = [nifty_dates[date] for date in common_dates]
                    
                    # Use first and last from common dates
                    basket_start = basket_values[0]
                    basket_end = basket_values[-1]
                    nifty_start = nifty_values[0]
                    nifty_end = nifty_values[-1]
                    
                    # Calculate indexed values (₹100 invested then → ₹X today)
                    # Both start from the same date, ensuring fair comparison
                    basket_value = (basket_end / basket_start) * 100
                    nifty_value = (nifty_end / nifty_start) * 100
                    
                    # Calculate returns
                    basket_return = basket_value - 100
                    nifty_return = nifty_value - 100
                    
                    # Determine who performed better
                    outperformance = basket_value - nifty_value
                    
                    performance_data.append({
                        'period': period['label'],
                        'code': period['code'],
                        'basket_value': round(basket_value, 2),
                        'nifty_value': round(nifty_value, 2),
                        'basket_return': round(basket_return, 2),
                        'nifty_return': round(nifty_return, 2),
                        'outperformance': round(outperformance, 2),
                        'basket_wins': basket_value > nifty_value
                    })
        
        # Cache for 1 hour
        cache.set(cache_key, performance_data, 3600)
    
    context = {
        'basket': basket,
        'performance_data': performance_data,
    }
    
    return render(request, 'stocks/basket_performance.j2', context)


@login_required
def basket_delete(request, basket_id):
    """Delete a basket"""
    basket = get_object_or_404(Basket, id=basket_id, user=request.user)
    basket_name = basket.name
    basket.delete()
    
    # Clear caches related to this basket
    cache.delete_many([
        f'basket_value_{basket_id}*',
        f'basket_metrics_{basket_id}*',
        f'chart_data_{basket_id}*',
        f'performance_{basket_id}'
    ])
    
    messages.success(request, f'Basket "{basket_name}" deleted successfully!')
    return redirect('home')


@login_required
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


@login_required
def basket_item_edit(request, item_id):
    """Edit basket item - update weight or quantity, rebalancing other stocks to maintain 100% total"""
    from django.http import JsonResponse
    
    if request.method == 'POST':
        item = get_object_or_404(BasketItem, id=item_id)
        basket = item.basket
        
        # Verify basket belongs to user
        if basket.user != request.user:
            return JsonResponse({'success': False, 'error': 'Unauthorized'})
        
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
            
            # Clear caches
            cache.delete_many([
                f'basket_value_{basket.id}*',
                f'basket_metrics_{basket.id}*',
            ])
            
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


@login_required
def basket_duplicate(request, basket_id):
    """Duplicate a basket - redirect to create page with pre-filled values"""
    basket = get_object_or_404(Basket, id=basket_id, user=request.user)
    
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


@login_required
def basket_edit_investment(request, basket_id):
    """Edit basket investment amount - recalculates all allocations"""
    from django.http import JsonResponse
    
    if request.method == 'POST':
        basket = get_object_or_404(Basket, id=basket_id, user=request.user)
        
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
            
            # Clear caches
            cache.delete_many([
                f'basket_value_{basket.id}*',
                f'basket_metrics_{basket.id}*',
            ])
            
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


def contact_us(request):
    """Contact Us page"""
    from django.shortcuts import render
    from django.middleware.csrf import get_token
    from django.contrib import messages
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        if name and email and message:
            # Here you would typically send an email
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('contact_us')
        else:
            messages.error(request, 'Please fill in all fields.')
    
    context = {'csrf_token': get_token(request)}
    return render(request, 'stocks/contact.j2', context)