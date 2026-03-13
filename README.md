# Smart Portfolio – NVDA Swing Bot & Dashboard

This project contains a **Smart Portfolio** playground plus a focused **Nvidia (NVDA) swing-trading bot** with a Streamlit dashboard.

## Features

- **Data ingestion**
  - Fetch historical daily bars for multiple symbols from:
    - Alpaca (`*_alpdata.csv`) via `app/alpaca_client.py`
    - yfinance (`*_yfdata.csv`) via `app/yahoo_client.py`
  - Data is stored in the `data/` folder (e.g. `data/NVDA_alpdata.csv`, `data/NVDA_yfdata.csv`).

- **NVDA swing strategy**
  - Strategy logic (indicators, signals) in `app/nvda_strategy.py`.
  - Simple long-only rules based on:
    - Moving averages on NVDA daily close.
    - RSI dip-and-recover entries and exits.

- **Backtesting**
  - Backtest engine in `app/nvda_backtest.py`:
    - Uses `data/NVDA_alpdata.csv` as price history.
    - Simulates a single NVDA position over time.
    - Outputs equity curve, trade list, and summary stats.
  - Results are written under `data/`:
    - `nvda_equity_curve.csv`
    - `nvda_trades.csv`
    - `nvda_stats.json`

- **Paper trading (Alpaca)**
  - `app/alpaca_client.py` wraps Alpaca REST APIs for:
    - Historical data downloads.
    - Account and position info.
    - Simple NVDA market orders.
  - `app/nvda_trader.py`:
    - Computes the latest NVDA signal.
    - Checks your current NVDA paper position.
    - Places a buy/sell market order when a change is needed.

- **Dashboard (`app/dashboard.py`)**
  - Streamlit UI for:
    - Current Alpaca paper account equity and NVDA position.
    - Latest NVDA strategy signal.
    - NVDA backtest equity curve (Plotly, zoomable).
    - Backtest summary statistics and recent trades table.
    - **Stock price history section** that:
      - Detects `*_yfdata.csv` and `*_alpdata.csv` in `data/`.
      - Lets you pick a symbol and plots two price charts (yfinance vs Alpaca) side by side.

## Setup

1. **Create / activate virtual environment** (example PowerShell):

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. **Install dependencies** (adjust as needed for your environment):

   ```powershell
   pip install streamlit pandas numpy alpaca-py yfinance python-dotenv plotly
   ```

3. **Configure Alpaca credentials**

   Create a `.env` file in the project root (or set environment variables another way):

   ```env
   ALPACA_API_KEY=your_paper_api_key
   ALPACA_SECRET_KEY=your_paper_secret_key
   ALPACA_BASE_URL=https://paper-api.alpaca.markets
   ```

## Common workflows

### 1. Fetch or refresh historical data

Populate `data/` with Alpaca and/or yfinance history (example from `app` modules):

- From Alpaca:

  ```powershell
  (venv) PS> python app/alpaca_client.py
  ```

- From yfinance:

  ```powershell
  (venv) PS> python app/yahoo_client.py
  ```

### 2. Run an NVDA backtest

From the repository root:

```powershell
(venv) PS> python app/nvda_backtest.py
```

This reads `data/NVDA_alpdata.csv`, runs the swing strategy, and writes equity/trades/stats into `data/`.

### 3. Start the dashboard

```powershell
(venv) PS> streamlit run app/dashboard.py
```

Open the local URL shown in the terminal (e.g. `http://localhost:8501`) to view:

- Live NVDA paper-trading status (from Alpaca).
- NVDA backtest equity curve and summary statistics.
- Recent backtest trades.
- Stock price history charts for any symbol with `*_yfdata.csv` / `*_alpdata.csv` files in `data/`.

### 4. Trigger a one-shot NVDA paper trade

```powershell
(venv) PS> python app/nvda_trader.py
```

This:

- Recomputes the latest NVDA signal from historical data.
- Checks your current NVDA paper position via Alpaca.
- Submits a market order to enter or exit NVDA if required.

You can schedule this script (e.g. once per day) using the Windows Task Scheduler if you want it to run automatically.

## Notes

- The strategy logic is intentionally simple and meant as a starting point for experimentation, not as investment advice.
- You can iterate on `app/nvda_strategy.py` and rerun `app/nvda_backtest.py` to see how changes affect performance in the dashboard.

