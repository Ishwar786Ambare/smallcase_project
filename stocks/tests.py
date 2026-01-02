from django.test import TestCase

# Create your tests here.
data = [{'UNITDSPR.NS': 'United Spirits'}, {'TARIL.NS': 'Transformers & Rectifiers'}]
import yfinance as yf

for item in data:
    ticker = next(iter(item))
    stock = yf.Ticker(ticker)
    history = stock.history(period='1d')
    if not history.empty:
        price = history['Close'].iloc[-1]
        print(f"{ticker}: {price}")
    else:
        print(f"{ticker}: possibly delisted; no price data found (period=1d)")
