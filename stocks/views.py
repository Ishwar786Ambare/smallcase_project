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
    stocks = Stock.objects.all()
    baskets = Basket.objects.all().order_by('-created_at')
    print([basket.get_total_value() for basket in baskets])
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

    context = {
        'stocks': stocks,
        'csrf_token': get_token(request),
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