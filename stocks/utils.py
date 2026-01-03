# stocks/utils.py

import yfinance as yf
from decimal import Decimal
from .models import Stock

# Popular Indian stocks (NSE symbols - add .NS suffix for yfinance)
INDIAN_STOCKS = {
    'RELIANCE.NS': 'Reliance Industries',
    'TCS.NS': 'Tata Consultancy Services',
    'HDFCBANK.NS': 'HDFC Bank',
    'INFY.NS': 'Infosys',
    'ICICIBANK.NS': 'ICICI Bank',
    'HINDUNILVR.NS': 'Hindustan Unilever',
    'BHARTIARTL.NS': 'Bharti Airtel',
    'ITC.NS': 'ITC Limited',
    'SBIN.NS': 'State Bank of India',
    'LT.NS': 'Larsen & Toubro',
    'AXISBANK.NS': 'Axis Bank',
    'KOTAKBANK.NS': 'Kotak Mahindra Bank',
    'BAJFINANCE.NS': 'Bajaj Finance',
    'ASIANPAINT.NS': 'Asian Paints',
    'MARUTI.NS': 'Maruti Suzuki',
    'TITAN.NS': 'Titan Company',
    'SUNPHARMA.NS': 'Sun Pharmaceutical',
    'WIPRO.NS': 'Wipro',
    'HCLTECH.NS': 'HCL Technologies',
    'ULTRACEMCO.NS': 'UltraTech Cement',
    'CGPOWER.NS': 'CG Power & Industrial Solutions',
    'AUROPHARM.NS': 'Aurobindo Pharma',
    'CAMS.NS': 'CAMS',
    'CDSL.NS': 'CDSL',
    'CHALET.NS': 'Chalet Hotels',
    'KAYNES.NS': 'Kaynes Technology India',
    'LUPIN.NS': 'Lupin',
    'PERSISTENT.NS': 'Persistent Systems',
    'POWERGRID.NS': 'Power Grid Corporation of India',
    'PRICOLLTD.NS': 'Pricol',
    'THYROCARE.NS': 'Thyrocare Technologies',
    'UNITDSPR.NS': 'United Spirits',
    'TARIL.NS': 'Transformers & Rectifiers',
    'MAZDOCK.NS': 'Mazagon Dock Shipbuilding',
    'GRSE.NS': 'Garden Reach Shipbuilders', 
    'COFORGE.NS': 'Coforge', 
    'INDHOTEL.NS': 'Indian Hotels Company', 
    'HEROMOTOCO.NS': 'Hero Motocorp', 
    'LT.NS': 'Larsen & Toubro', 
    'RELIANCE.NS': 'Reliance Industries', 
    'CHAMBLFERT.NS': 'Chambal Fertilisers & Chemicals', 
    'BEL.NS': 'Bharat Electronics', 
    'INDIGO.NS': 'Interglobe Aviation', 
    'BHARTIARTL.NS': 'Bharti Airtel'
}

# Indian market indices
INDIAN_INDICES = {
    '^NSEI': 'Nifty 50',
    '^NSEBANK': 'Nifty Bank',
    '^BSESN': 'Sensex',
}

# Time period mappings for yfinance
TIME_PERIODS = {
    '1d': '1d',
    '7d': '7d',
    '1m': '1mo',
    '3m': '3mo',
    '6m': '6mo',
    '1y': '1y',
    '3y': '3y',
    '5y': '5y',
}


def fetch_index_historical_data(index_symbol, period='1mo'):
    """
    Fetch historical data for an index
    
    Args:
        index_symbol: Index ticker (e.g., '^NSEI' for Nifty 50)
        period: Time period - '1d', '7d', '1m', '3m', '6m', '1y', '3y', '5y'
    
    Returns:
        List of {date, value} dictionaries
    """
    try:
        # Convert our period format to yfinance format
        yf_period = TIME_PERIODS.get(period, '1mo')
        
        index = yf.Ticker(index_symbol)
        df = yf.download(index_symbol, period=yf_period, progress=False)
        
        if not df.empty:
            result = []
            for date, row in df.iterrows():
                result.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'value': float(row['Close'])
                })
            return result
        return []
    except Exception as e:
        print(f"Error fetching index data for {index_symbol}: {e}")
        return []


def fetch_stock_historical_data(symbol, period='1mo'):
    """
    Fetch historical data for a stock
    
    Args:
        symbol: Stock ticker (e.g., 'RELIANCE.NS')
        period: Time period - '1d', '7d', '1m', '3m', '6m', '1y', '3y', '5y'
    
    Returns:
        List of {date, value} dictionaries
    """
    try:
        yf_period = TIME_PERIODS.get(period, '1mo')
        
        stock = yf.Ticker(symbol)
        df = yf.download(symbol, period=yf_period, progress=False)
        
        if not df.empty:
            result = []
            for date, row in df.iterrows():
                result.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'value': float(row['Close'])
                })
            return result
        return []
    except Exception as e:
        print(f"Error fetching stock data for {symbol}: {e}")
        return []


def calculate_basket_historical_performance(basket, period='1mo'):
    """
    Calculate historical performance of a basket
    
    Args:
        basket: Basket model instance
        period: Time period
    
    Returns:
        List of {date, value} dictionaries representing basket value over time
    """
    from .models import BasketItem
    
    items = basket.items.all()
    if not items:
        return []
    
    # Fetch historical data for all stocks in basket
    stock_histories = {}
    for item in items:
        hist_data = fetch_stock_historical_data(item.stock.symbol, period)
        if hist_data:
            stock_histories[item.stock.symbol] = hist_data
    
    if not stock_histories:
        return []
    
    # Get common dates across all stocks
    all_dates = set()
    for hist_data in stock_histories.values():
        for point in hist_data:
            all_dates.add(point['date'])
    
    common_dates = sorted(all_dates)
    
    # Calculate basket value for each date
    basket_performance = []
    
    for date in common_dates:
        total_value = 0
        all_stocks_have_data = True
        
        for item in items:
            symbol = item.stock.symbol
            if symbol in stock_histories:
                # Find price for this date
                date_data = next((d for d in stock_histories[symbol] if d['date'] == date), None)
                if date_data:
                    stock_value = float(item.quantity) * date_data['value']
                    total_value += stock_value
                else:
                    all_stocks_have_data = False
                    break
            else:
                all_stocks_have_data = False
                break
        
        if all_stocks_have_data:
            basket_performance.append({
                'date': date,
                'value': total_value
            })
    
    return basket_performance


def fetch_stock_price(symbol):
    """
    Fetch current stock price using yfinance
    Returns price or None if failed
    """
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period='1d')
        if not data.empty:
            return float(data['Close'].iloc[-1])
        return None
    except Exception as e:
        print(f"Error fetching price for {symbol}: {e}")
        return None


def update_stock_prices_bulk(symbols):
    """
    OPTIMIZATION: Update prices for multiple stocks in bulk (much faster than one-by-one)
    
    Args:
        symbols: List of stock symbols to update
    
    Returns:
        Number of stocks updated
    """
    from django.utils import timezone
    from datetime import timedelta
    
    if not symbols:
        return 0
    
    try:
        # Fetch data for all symbols at once (much faster!)
        symbols_str = ' '.join(symbols)
        data = yf.download(symbols_str, period='1d', group_by='ticker', progress=False)
        
        updated_count = 0
        for symbol in symbols:
            try:
                if len(symbols) == 1:
                    # Single stock
                    if not data.empty and 'Close' in data.columns:
                        price = float(data['Close'].iloc[-1])
                        stock = Stock.objects.get(symbol=symbol)
                        stock.current_price = Decimal(str(price))
                        stock.save()
                        updated_count += 1
                else:
                    # Multiple stocks
                    if symbol in data.columns.get_level_values(0):
                        stock_data = data[symbol]
                        if not stock_data.empty and 'Close' in stock_data.columns:
                            price = float(stock_data['Close'].iloc[-1])
                            stock = Stock.objects.get(symbol=symbol)
                            stock.current_price = Decimal(str(price))
                            stock.save()
                            updated_count += 1
            except Exception as e:
                print(f"Error updating {symbol}: {e}")
                continue
        
        print(f"Bulk updated {updated_count} stock prices")
        return updated_count
        
    except Exception as e:
        print(f"Error in bulk update: {e}")
        # Fallback to individual updates
        updated_count = 0
        for symbol in symbols:
            try:
                price = fetch_stock_price(symbol)
                if price:
                    stock = Stock.objects.get(symbol=symbol)
                    stock.current_price = Decimal(str(price))
                    stock.save()
                    updated_count += 1
            except Exception as e:
                print(f"Error updating {symbol}: {e}")
                continue
        return updated_count


def update_stock_prices():
    """Update prices for all stocks in database (with 5-minute cache)"""
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    stocks = Stock.objects.all()
    
    # Filter stocks that need updating (no price or stale price)
    stale_stocks = []
    for stock in stocks:
        should_update = False
        if not stock.current_price:
            should_update = True
        elif stock.last_updated and stock.last_updated < timezone.now() - timedelta(minutes=5):
            should_update = True
        
        if should_update:
            stale_stocks.append(stock.symbol)
    
    if not stale_stocks:
        print("All stock prices are up to date")
        return 0
    
    # OPTIMIZATION: Use bulk update instead of individual fetches
    updated_count = update_stock_prices_bulk(stale_stocks)
    
    print(f"Updated {updated_count} stock prices")
    return updated_count


def populate_indian_stocks():
    """Populate database with Indian stocks"""
    created_count = 0
    for symbol, name in INDIAN_STOCKS.items():
        stock, created = Stock.objects.get_or_create(
            symbol=symbol,
            defaults={'name': name}
        )
        if created:
            created_count += 1
            # Fetch initial price
            price = fetch_stock_price(symbol)
            if price:
                stock.current_price = Decimal(str(price))
                stock.save()
    return created_count


def calculate_equal_weight_basket(stock_symbols, investment_amount):
    """
    Calculate equal weight allocation for selected stocks

    Args:
        stock_symbols: List of stock symbols
        investment_amount: Total amount to invest

    Returns:
        List of dictionaries with stock allocation details
    """
    if not stock_symbols:
        return []

    num_stocks = len(stock_symbols)
    weight_per_stock = Decimal('100.00') / num_stocks
    amount_per_stock = Decimal(str(investment_amount)) / num_stocks

    allocations = []

    for symbol in stock_symbols:
        try:
            stock = Stock.objects.get(symbol=symbol)

            # Fetch latest price if not available
            if not stock.current_price:
                price = fetch_stock_price(symbol)
                if price:
                    stock.current_price = Decimal(str(price))
                    stock.save()

            if stock.current_price and stock.current_price > 0:
                # Calculate quantity as whole number
                quantity = int(amount_per_stock / stock.current_price)
                
                # Recalculate actual allocated amount based on whole quantity
                actual_allocated_amount = quantity * stock.current_price
                
                # Recalculate actual weight based on actual allocated amount
                actual_weight = (actual_allocated_amount / Decimal(str(investment_amount))) * 100

                allocations.append({
                    'stock': stock,
                    'weight_percentage': actual_weight,
                    'allocated_amount': actual_allocated_amount,
                    'quantity': quantity,
                    'price': stock.current_price,
                })
        except Stock.DoesNotExist:
            continue

    return allocations


def create_basket_with_stocks(name, description, investment_amount, stock_symbols, user=None):
    """
    Create a basket with equal-weighted stocks (quantities as whole numbers)

    Args:
        name: Basket name
        description: Basket description
        investment_amount: Total investment amount
        stock_symbols: List of stock symbols to include
        user: User who owns the basket (optional for backward compatibility)

    Returns:
        Basket object
    """
    from .models import Basket, BasketItem

    # Calculate allocations
    allocations = calculate_equal_weight_basket(stock_symbols, investment_amount)

    if not allocations:
        return None

    # Create basket
    basket = Basket.objects.create(
        name=name,
        description=description,
        investment_amount=Decimal(str(investment_amount)),
        user=user
    )

    # Create basket items with whole number quantities
    total_allocated = Decimal('0')
    
    for alloc in allocations:
        BasketItem.objects.create(
            basket=basket,
            stock=alloc['stock'],
            weight_percentage=alloc['weight_percentage'],
            allocated_amount=alloc['allocated_amount'],
            quantity=alloc['quantity'],  # Already an integer
            purchase_price=alloc['price']
        )
        total_allocated += alloc['allocated_amount']

    # Update basket investment amount to actual total
    if total_allocated > 0:
        basket.investment_amount = total_allocated
        basket.save()
        
        # Recalculate weights to ensure they sum to 100% relative to actual investment
        for item in basket.items.all():
            item.weight_percentage = (item.allocated_amount / total_allocated) * 100
            item.save()

    return basket