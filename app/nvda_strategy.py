import pandas as pd
import numpy as np
from dataclasses import dataclass


@dataclass
class NvdaStrategyConfig:
    short_sma: int = 20
    mid_sma: int = 50
    long_sma: int = 200
    rsi_period: int = 14
    rsi_oversold: float = 30.0
    rsi_exit: float = 60.0


def _compute_rsi(series: pd.Series, period: int) -> pd.Series:
    delta = series.diff()
    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)

    gain_ema = pd.Series(gain, index=series.index).ewm(alpha=1 / period, adjust=False).mean()
    loss_ema = pd.Series(loss, index=series.index).ewm(alpha=1 / period, adjust=False).mean()

    rs = gain_ema / loss_ema.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(0.0)


def add_indicators(df: pd.DataFrame, cfg: NvdaStrategyConfig | None = None) -> pd.DataFrame:
    if cfg is None:
        cfg = NvdaStrategyConfig()

    data = df.copy()

    close = data["close"]
    data["sma_short"] = close.rolling(cfg.short_sma).mean()
    data["sma_mid"] = close.rolling(cfg.mid_sma).mean()
    data["sma_long"] = close.rolling(cfg.long_sma).mean()
    data["rsi"] = _compute_rsi(close, cfg.rsi_period)

    return data


def generate_signals(
    df_with_indicators: pd.DataFrame,
    cfg: NvdaStrategyConfig | None = None,
) -> pd.DataFrame:
    if cfg is None:
        cfg = NvdaStrategyConfig()

    data = df_with_indicators.copy()

    uptrend = (data["close"] > data["sma_mid"]) & (data["sma_mid"] > data["sma_long"])

    rsi = data["rsi"]
    rsi_prev = rsi.shift(1)
    rsi_cross_up = (rsi_prev < cfg.rsi_oversold) & (rsi >= cfg.rsi_oversold)

    entry_signal = uptrend & rsi_cross_up

    exit_signal_rsi = rsi >= cfg.rsi_exit
    exit_signal_trend = data["close"] < data["sma_mid"]
    exit_signal = exit_signal_rsi | exit_signal_trend

    position = pd.Series(0, index=data.index, dtype=int)
    in_position = False

    for i, (enter, exit_) in enumerate(zip(entry_signal, exit_signal)):
        if not in_position and enter:
            in_position = True
        elif in_position and exit_:
            in_position = False
        position.iat[i] = 1 if in_position else 0

    data["position"] = position

    signal = position.diff().fillna(0)
    data["signal"] = signal

    return data

