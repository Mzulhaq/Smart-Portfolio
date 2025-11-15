# Handles yfinance data fetching
import os
import pandas as pd
import datetime as dt
import yfinance as yf



def collect_yfinance_data(symbol: str, start: str, end: str):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(start=start, end=end)
    return hist

#fetches data from yfinance API based on list of symbols/tickers
def fetch_all_data(symbols: list, start_date: str):
    print("Fetching historical data from yfinance...")
    all_data = {}
    for s in symbols:
        all_data[s] = collect_yfinance_data(s, start_date, dt.datetime.now().strftime('%Y-%m-%d'))
    return all_data

def print_sample_data(all_data: dict):
    for i in all_data:
        print(f"{i} data:")
        print(all_data[i].tail())


if __name__ == "__main__":
    #stocks invested in
    symbols = ["AAPL", "MSFT", "META", "AMZN", "COST", "GOOGL", "TSLA", "NVDA", "SHOP", "CRWD"]
    all_data = fetch_all_data(symbols, "2020-01-01")
    
    for symbol, df in all_data.items():
        df.to_csv(f"data/{symbol}_yfdata.csv", index=True)