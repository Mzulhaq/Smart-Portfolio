import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd

from .nvda_strategy import NvdaStrategyConfig, add_indicators, generate_signals


@dataclass
class BacktestResult:
    equity_curve: pd.Series
    trades: pd.DataFrame
    stats: Dict[str, float]


def load_nvda_data(path: str = "data/NVDA_alpdata.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.set_index("timestamp")
    elif "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"])
        df = df.set_index("time")
    df = df.sort_index()
    return df


def _calculate_max_drawdown(equity: pd.Series) -> float:
    roll_max = equity.cummax()
    drawdown = equity / roll_max - 1.0
    return float(drawdown.min())


def run_backtest(
    raw_df: pd.DataFrame,
    initial_equity: float = 100_000.0,
    cfg: NvdaStrategyConfig | None = None,
) -> BacktestResult:
    if cfg is None:
        cfg = NvdaStrategyConfig()

    df_ind = add_indicators(raw_df, cfg)
    df = generate_signals(df_ind, cfg)

    position = df["position"]
    close = df["close"]

    equity = pd.Series(index=df.index, dtype=float)
    position_flag = 0
    entry_price = 0.0
    capital = initial_equity

    trades = []

    for ts, row in df.iterrows():
        pos = int(row["position"])
        price = float(row["close"])

        if position_flag == 0 and pos == 1:
            entry_price = price
            position_flag = 1

        elif position_flag == 1 and pos == 0:
            ret_pct = (price / entry_price) - 1.0
            pnl = capital * ret_pct
            capital = capital + pnl
            trades.append(
                {
                    "entry_time": ts,
                    "exit_time": ts,
                    "entry_price": entry_price,
                    "exit_price": price,
                    "return_pct": ret_pct,
                    "pnl": pnl,
                }
            )
            entry_price = 0.0
            position_flag = 0

        equity[ts] = capital

    if position_flag == 1 and entry_price > 0:
        last_price = float(close.iloc[-1])
        ret_pct = (last_price / entry_price) - 1.0
        pnl = capital * ret_pct
        capital = capital + pnl
        trades.append(
            {
                "entry_time": close.index[-1],
                "exit_time": close.index[-1],
                "entry_price": entry_price,
                "exit_price": last_price,
                "return_pct": ret_pct,
                "pnl": pnl,
            }
        )
        equity.iloc[-1] = capital

    trades_df = pd.DataFrame(trades)

    if not trades_df.empty:
        wins = trades_df["pnl"] > 0
        win_rate = float(wins.mean())
        avg_win = float(trades_df.loc[wins, "return_pct"].mean()) if wins.any() else 0.0
        avg_loss = float(trades_df.loc[~wins, "return_pct"].mean()) if (~wins).any() else 0.0
    else:
        win_rate = 0.0
        avg_win = 0.0
        avg_loss = 0.0

    final_equity = float(equity.iloc[-1])
    total_return = final_equity / initial_equity - 1.0
    max_dd = _calculate_max_drawdown(equity)

    returns = equity.pct_change().dropna()
    sharpe = float(np.sqrt(252) * returns.mean() / returns.std()) if returns.std() != 0 else 0.0

    stats = {
        "initial_equity": initial_equity,
        "final_equity": final_equity,
        "total_return": total_return,
        "max_drawdown": max_dd,
        "win_rate": win_rate,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "num_trades": int(len(trades_df)),
        "sharpe_like": sharpe,
    }

    return BacktestResult(equity_curve=equity, trades=trades_df, stats=stats)


def save_backtest_results(
    result: BacktestResult,
    out_dir: str = "data",
    prefix: str = "nvda",
) -> None:
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    equity_path = out_path / f"{prefix}_equity_curve.csv"
    trades_path = out_path / f"{prefix}_trades.csv"
    stats_path = out_path / f"{prefix}_stats.json"

    result.equity_curve.to_csv(equity_path, header=["equity"])
    result.trades.to_csv(trades_path, index=False)
    with stats_path.open("w") as f:
        json.dump(result.stats, f, indent=2, default=float)


def run_and_save_backtest(
    data_path: str = "data/NVDA_alpdata.csv",
    out_dir: str = "data",
    initial_equity: float = 100_000.0,
) -> BacktestResult:
    df = load_nvda_data(data_path)
    result = run_backtest(df, initial_equity=initial_equity)
    save_backtest_results(result, out_dir=out_dir, prefix="nvda")
    return result


if __name__ == "__main__":
    run_and_save_backtest()

