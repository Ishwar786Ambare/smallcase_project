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
    'TARIL.NS': 'Transformers & Rectifiers'
}


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
    """Update prices for all stocks in database"""
    stocks = Stock.objects.all()
    for stock in stocks:
        price = fetch_stock_price(stock.symbol)
        if price:
            stock.current_price = Decimal(str(price))
            stock.save()
    return stocks.count()


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
                quantity = amount_per_stock / stock.current_price

                allocations.append({
                    'stock': stock,
                    'weight_percentage': weight_per_stock,
                    'allocated_amount': amount_per_stock,
                    'quantity': quantity,
                    'price': stock.current_price,
                })
        except Stock.DoesNotExist:
            continue

    return allocations


def create_basket_with_stocks(name, description, investment_amount, stock_symbols):
    """
    Create a basket with equal-weighted stocks

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

    # Create basket items
    for alloc in allocations:
        BasketItem.objects.create(
            basket=basket,
            stock=alloc['stock'],
            weight_percentage=alloc['weight_percentage'],
            allocated_amount=alloc['allocated_amount'],
            quantity=alloc['quantity'],
            purchase_price=alloc['price']
        )

    return basket