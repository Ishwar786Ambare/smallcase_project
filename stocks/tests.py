from django.test import TestCase

# Create your tests here.
# Garden Reach Shipbuilders
# Coforge
# Indian Hotels Company
# Hero Motocorp
# Larsen & Toubro
# Reliance Industries
# Chambal Fertilisers & Chemicals
# Bharat Electronics
# Interglobe Aviation
# Bharti Airtel


data = [
    {'GRSE.NS': 'Garden Reach Shipbuilders'}, 
    {'COFORGE.NS': 'Coforge'}, 
    {'INDHOTEL.NS': 'Indian Hotels Company'}, 
    {'HEROMOTOCO.NS': 'Hero Motocorp'}, 
    {'LT.NS': 'Larsen & Toubro'}, 
    {'RELIANCE.NS': 'Reliance Industries'}, 
    {'CHAMBLFERT.NS': 'Chambal Fertilisers & Chemicals'}, 
    {'BEL.NS': 'Bharat Electronics'}, 
    {'INDIGO.NS': 'Interglobe Aviation'}, 
    {'BHARTIARTL.NS': 'Bharti Airtel'}
]
import yfinance as yf

for item in data:
    ticker = next(iter(item))
    stock = yf.Ticker(ticker)
    history = stock.history(period='1d')
    if not history.empty:
        price = history['Close'].iloc[-1]
        print(f"{ticker}: {price}")
    else:
        break
        print(f"{ticker}: possibly delisted; no price data found (period=1d)")
