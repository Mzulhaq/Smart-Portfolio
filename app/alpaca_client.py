import datetime as dt
import os
from typing import Any, Dict, Optional

import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest
from dotenv import load_dotenv

load_dotenv()

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

data_client = StockHistoricalDataClient(ALPACA_API_KEY, ALPACA_SECRET_KEY)
trading_client = TradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=True)


def get_historical_data(symbol: str, start: str, end: str) -> pd.DataFrame:
    """Fetch daily historical bars for a single symbol."""
    request_params = StockBarsRequest(
        symbol_or_symbols=[symbol],
        timeframe=TimeFrame.Day,
        start=start,
        end=end,
    )
    bars = data_client.get_stock_bars(request_params)
    return bars.df


def fetch_all_data(symbols: list[str], start_date: str) -> dict[str, pd.DataFrame]:
    """Fetch daily historical bars for a list of symbols."""
    print("Fetching historical data from Alpaca...")
    all_data: dict[str, pd.DataFrame] = {}
    for s in symbols:
        all_data[s] = get_historical_data(s, start_date, dt.datetime.now().strftime("%Y-%m-%d"))
    return all_data


def print_sample_data(all_data: dict[str, pd.DataFrame]) -> None:
    for symbol, df in all_data.items():
        print(f"{symbol} data:")
        print(df.tail())


def get_account() -> Any:
    """Return Alpaca account object."""
    return trading_client.get_account()


def get_positions() -> list[Any]:
    """Return all open positions."""
    return trading_client.get_all_positions()


def get_nvda_position() -> Optional[Any]:
    """Return NVDA position object if it exists, else None."""
    positions = get_positions()
    for pos in positions:
        if getattr(pos, "symbol", "").upper() == "NVDA":
            return pos
    return None


def submit_nvda_market_order(side: str, qty: int) -> Dict[str, Any]:
    """
    Submit a simple NVDA market order.

    side: 'buy' or 'sell'
    qty: number of shares
    """
    order_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
    order = MarketOrderRequest(
        symbol="NVDA",
        qty=qty,
        side=order_side,
        time_in_force=TimeInForce.DAY,
    )
    placed = trading_client.submit_order(order)
    return {
        "id": placed.id,
        "symbol": placed.symbol,
        "qty": placed.qty,
        "side": placed.side,
        "status": placed.status,
    }


if __name__ == "__main__":
    symbols = ["AAPL", "MSFT", "META", "AMZN", "COST", "GOOGL", "TSLA", "NVDA", "SHOP", "CRWD"]
    all_data = fetch_all_data(symbols, "2020-01-01")
    for symbol, df in all_data.items():
        df.to_csv(f"data/{symbol}_alpdata.csv", index=True)