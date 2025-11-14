# Handles Alpaca API calls
import os
import pandas as pd
import datetime as dt
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from dotenv import load_dotenv

load_dotenv()
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
ALPACA_BASE_URL = os.getenv("ALPACA_BASE_URL")
client = StockHistoricalDataClient(ALPACA_API_KEY, ALPACA_SECRET_KEY)

#Data aquisition from Alpaca API
def get_historical_data(symbol: str, start: str, end: str):
    request_params = StockBarsRequest(
        symbol_or_symbols=[symbol],
        timeframe=TimeFrame.Day,
        start=start,
        end=end
    )
    bars = client.get_stock_bars(request_params)
    return bars.df

def fetch_all_data(symbols: list):
    print("Fetching historical data from Alpaca...")
    all_data = {}
    for s in symbols:
        all_data[s] = get_historical_data(s, "2025-01-01", dt.datetime.now().strftime('%Y-%m-%d'))
    return all_data

def print_sample_data(all_data: dict):
    for i in all_data:
        print(f"{i} data:")
        print(all_data[i].tail())

if __name__ == "__main__":
    #stocks invested in
    symbols = ["AAPL", "MSFT", "META", "AMZN", "COST", "GOOGL", "TSLA", "NVDA", "SHOP", "CRWD"]
    all_data = fetch_all_data(symbols)
    print_sample_data(all_data)
    for symbol, df in all_data.items():
        df.to_csv(f"data/{symbol}_data.csv", index=True)