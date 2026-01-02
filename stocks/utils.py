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
}

# Indian market indices
INDIAN_INDICES = {
    '^NSEI': 'Nifty 50',
    '^NSEBANK': 'Nifty Bank',
    '^BSESN': 'Sensex',
}


def fetch_index_historical_data(index_symbol, start_date):
    """
    Fetch historical data for an index
    Returns list of {date, value} dictionaries
    """
    try:
        index = yf.Ticker(index_symbol)
        data = index.history(start=start_date)
        
        if not data.empty:
            result = []
            for date, row in data.iterrows():
                result.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'value': float(row['Close'])
                })
            return result
        return []
    except Exception as e:
        print(f"Error fetching index data for {index_symbol}: {e}")
        return []


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


def update_stock_prices():
    """Update prices for all stocks in database (with 5-minute cache)"""
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    stocks = Stock.objects.all()
    updated_count = 0
    
    for stock in stocks:
        try:
            # Only update if price is old (more than 5 minutes) or missing
            should_update = False
            if not stock.current_price:
                should_update = True
            elif stock.last_updated and stock.last_updated < timezone.now() - timedelta(minutes=5):
                should_update = True
            else:
                # Price exists and is fresh (less than 5 minutes old)
                should_update = False
            
            if should_update:
                price = fetch_stock_price(stock.symbol)
                if price:
                    stock.current_price = Decimal(str(price))
                    stock.save()  # This will auto-update last_updated due to auto_now=True
                    updated_count += 1
        except Exception as e:
            print(f"Error updating {stock.symbol}: {e}")
            continue
    
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


def create_basket_with_stocks(name, description, investment_amount, stock_symbols):
    """
    Create a basket with equal-weighted stocks (quantities as whole numbers)

    Args:
        name: Basket name
        description: Basket description
        investment_amount: Total investment amount
        stock_symbols: List of stock symbols to include

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
        investment_amount=Decimal(str(investment_amount))
    )

    # Create basket items with whole number quantities
    for alloc in allocations:
        BasketItem.objects.create(
            basket=basket,
            stock=alloc['stock'],
            weight_percentage=alloc['weight_percentage'],
            allocated_amount=alloc['allocated_amount'],
            quantity=alloc['quantity'],  # Already an integer
            purchase_price=alloc['price']
        )

    return basket