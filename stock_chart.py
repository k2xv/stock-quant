import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def get_stock_data(symbol, period="3mo"):
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period)
    return df

def calc_indicators(df):
    df['MA5'] = df['Close'].rolling(5).mean()
    df['MA20'] = df['Close'].rolling(20).mean()
    df['MA60'] = df['Close'].rolling(60).mean()
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    ema12 = df['Close'].ewm(span=12).mean()
    ema26 = df['Close'].ewm(span=26).mean()
    df['MACD'] = ema12 - ema26
    df['Signal'] = df['MACD'].ewm(span=9).mean()
    df['Hist'] = df['MACD'] - df['Signal']
    return df

def plot_stock(symbol, period="3mo"):
    print(f"正在获取 {symbol} 数据...")
    df = get_stock_data(symbol, period)
    df = calc_indicators(df)
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.6, 0.2, 0.2], subplot_titles=(f"{symbol} K线图", "RSI", "MACD"))
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="K线", increasing_line_color='#26a69a', decreasing_line_color='#ef5350'), row=1, col=1)
    for ma, color in [('MA5', '#ff9800'), ('MA20', '#2196f3'), ('MA60', '#9c27b0')]:
        fig.add_trace(go.Scatter(x=df.index, y=df[ma], name=ma, line=dict(color=color, width=1.2)), row=1, col=1)
    colors = ['#26a69a' if c >= o else '#ef5350' for c, o in zip(df['Close'], df['Open'])]
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI", line=dict(color='#ff9800', width=1.5)), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], name="MACD", line=dict(color='#2196f3', width=1.2)), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['Signal'], name="Signal", line=dict(color='#ff9800', width=1.2)), row=3, col=1)
    hist_colors = ['#26a69a' if v >= 0 else '#ef5350' for v in df['Hist']]
    fig.add_trace(go.Bar(x=df.index, y=df['Hist'], name="柱状", marker_color=hist_colors), row=3, col=1)
    last = df.iloc[-1]
    prev = df.iloc[-2]
    change = last['Close'] - prev['Close']
    change_pct = change / prev['Close'] * 100
    sign = "+" if change >= 0 else ""
    fig.update_layout(title=dict(text=f"{symbol}  ${last['Close']:.2f}  {sign}{change:.2f} ({sign}{change_pct:.2f}%)", font=dict(size=20)), template="plotly_dark", height=800, xaxis_rangeslider_visible=False)
    fig.update_yaxes(title_text="RSI", row=2, col=1, range=[0, 100])
    fig.show()

plot_stock("NVDA", period="3mo")
