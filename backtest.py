import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def backtest(symbol, period="1y", initial_cash=10000):
    print(f"正在回测 {symbol}...")
    df = yf.Ticker(symbol).history(period=period)
    df['MA5'] = df['Close'].rolling(5).mean()
    df['MA20'] = df['Close'].rolling(20).mean()

    # 生成信号：MA5上穿MA20买入=1，下穿卖出=-1
    df['Signal'] = 0
    df.loc[df['MA5'] > df['MA20'], 'Signal'] = 1
    df.loc[df['MA5'] < df['MA20'], 'Signal'] = -1
    df['Position'] = df['Signal'].diff()  # 1=买入 -2=卖出

    # 回测资金曲线
    cash = initial_cash
    shares = 0
    portfolio = []
    trades = []

    for i, row in df.iterrows():
        if pd.isna(row['MA20']):
            portfolio.append(cash)
            continue
        if row['Position'] == 1 and cash > 0:  # 买入
            shares = cash / row['Close']
            cash = 0
            trades.append({'date': i, 'type': '买入', 'price': row['Close'], 'shares': shares})
        elif row['Position'] == -2 and shares > 0:  # 卖出
            cash = shares * row['Close']
            trades.append({'date': i, 'type': '卖出', 'price': row['Close'], 'profit': cash - initial_cash})
            shares = 0
        total = cash + shares * row['Close']
        portfolio.append(total)

    df['Portfolio'] = portfolio
    df['BuyHold'] = initial_cash * df['Close'] / df['Close'].iloc[0]

    final_value = df['Portfolio'].iloc[-1]
    buyhold_value = df['BuyHold'].iloc[-1]
    ret = (final_value - initial_cash) / initial_cash * 100
    bh_ret = (buyhold_value - initial_cash) / initial_cash * 100

    print(f"\n{'='*40}")
    print(f"  {symbol} 回测结果（{period}）")
    print(f"{'='*40}")
    print(f"  初始资金:     ${initial_cash:,.0f}")
    print(f"  策略最终:     ${final_value:,.0f}  ({ret:+.1f}%)")
    print(f"  买入持有:     ${buyhold_value:,.0f}  ({bh_ret:+.1f}%)")
    print(f"  交易次数:     {len(trades)} 笔")
    print(f"{'='*40}\n")

    # 画图
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.5, 0.5], vertical_spacing=0.05,
                        subplot_titles=(f"{symbol} 价格 + 买卖点", "资金曲线对比"))

    # K线
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name="收盘价", line=dict(color='white', width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA5'], name="MA5", line=dict(color='#ff9800', width=1.2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name="MA20", line=dict(color='#2196f3', width=1.2)), row=1, col=1)

    # 买卖点
    buys = df[df['Position'] == 1]
    sells = df[df['Position'] == -2]
    fig.add_trace(go.Scatter(x=buys.index, y=buys['Close'], mode='markers',
                             marker=dict(symbol='triangle-up', size=12, color='#00e676'),
                             name="买入"), row=1, col=1)
    fig.add_trace(go.Scatter(x=sells.index, y=sells['Close'], mode='markers',
                             marker=dict(symbol='triangle-down', size=12, color='#ff1744'),
                             name="卖出"), row=1, col=1)

    # 资金曲线
    fig.add_trace(go.Scatter(x=df.index, y=df['Portfolio'], name=f"策略 ({ret:+.1f}%)",
                             line=dict(color='#00e676', width=2)), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['BuyHold'], name=f"买入持有 ({bh_ret:+.1f}%)",
                             line=dict(color='#2196f3', width=2)), row=2, col=1)

    fig.update_layout(template="plotly_dark", height=700,
                      title=f"{symbol} 均线交叉策略回测 | 初始 ${initial_cash:,}")
    fig.show()

# ========== 修改这里 ==========
backtest("NVDA", period="1y", initial_cash=10000)
