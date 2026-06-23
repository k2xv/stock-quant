# US Stock Quantitative Analysis

A Python-based stock monitoring and backtesting framework built from scratch.

## Files
- `stock.py` — Real-time stock price monitor with price alerts
- `stock_chart.py` — Interactive candlestick chart with MA, RSI, MACD
- `backtest.py` — Moving average crossover strategy backtest
- `backtest2.py` — Advanced backtest with custom MA parameters and stop-loss

## Key Findings
- MA crossover strategy significantly underperforms buy-and-hold on trending stocks (NVDA: +3.7% vs +44.9%)
- Strategy slightly outperforms on stable stocks like XOM
- 5% stop-loss is too tight for high-volatility stocks; 8-15% recommended

## Setup
```bash
python3 -m venv env
source env/bin/activate
pip install yfinance pandas rich plotly
```

## Usage
```bash
python3 stock.py          # Real-time price monitor
python3 stock_chart.py    # Interactive K-line chart
python3 backtest2.py      # Run backtest
```

## Tech Stack
Python / yfinance / plotly / pandas
