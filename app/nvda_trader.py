from __future__ import annotations

import datetime as dt
from typing import Tuple

import pandas as pd

from . import alpaca_client
from .nvda_backtest import load_nvda_data
from .nvda_strategy import NvdaStrategyConfig, add_indicators, generate_signals


def _compute_latest_signal(cfg: NvdaStrategyConfig | None = None) -> Tuple[pd.Timestamp, int, float]:
    """
    Compute the latest NVDA position signal and price using historical data.

    Returns (timestamp, desired_position, last_close_price).
    desired_position is 0 (flat) or 1 (long).
    """
    if cfg is None:
        cfg = NvdaStrategyConfig()

    # Use existing cached NVDA_alpdata.csv for now
    df = load_nvda_data("data/NVDA_alpdata.csv")
    df = add_indicators(df, cfg)
    df = generate_signals(df, cfg)

    latest_row = df.iloc[-1]
    ts = df.index[-1]
    desired_position = int(latest_row["position"])
    last_price = float(latest_row["close"])
    return ts, desired_position, last_price


def _decide_order(current_nvda_shares: float, desired_position: int, last_price: float) -> Tuple[str | None, int]:
    """
    Decide what order (if any) to place.

    Returns (side, qty):
      - side is 'buy', 'sell', or None
      - qty is an integer share quantity if side is not None
    """
    current_in_position = current_nvda_shares > 0

    if not current_in_position and desired_position == 1:
        # Enter new position: risk a small % of equity with a rough 10% stop
        account = alpaca_client.get_account()
        equity = float(account.equity)
        risk_per_trade = 0.01  # 1% of equity
        stop_fraction = 0.1
        dollar_risk = equity * risk_per_trade
        per_share_risk = last_price * stop_fraction
        qty = max(int(dollar_risk / per_share_risk), 1)
        return "buy", qty

    if current_in_position and desired_position == 0:
        # Exit existing position: sell all
        return "sell", int(current_nvda_shares)

    return None, 0


def run_nvda_paper_trade() -> None:
    """
    One-shot NVDA paper trading decision:
    - Reads latest NVDA signal from historical data + strategy
    - Checks current NVDA Alpaca paper position
    - Places a market order if we need to enter or exit
    """
    ts, desired_position, last_price = _compute_latest_signal()
    nvda_pos = alpaca_client.get_nvda_position()
    current_shares = float(getattr(nvda_pos, "qty", 0)) if nvda_pos is not None else 0.0

    side, qty = _decide_order(current_shares, desired_position, last_price)

    print(f"[{dt.datetime.now().isoformat()}] Latest bar: {ts}, close={last_price:.2f}")
    print(f"Desired position: {desired_position}, current NVDA shares: {current_shares}")

    if side is None or qty <= 0:
        print("No order to place today.")
        return

    print(f"Placing {side} market order for {qty} NVDA shares...")
    order_info = alpaca_client.submit_nvda_market_order(side, qty)
    print("Order response:", order_info)


if __name__ == "__main__":
    run_nvda_paper_trade()

