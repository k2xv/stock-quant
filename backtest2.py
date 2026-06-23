import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def backtest(symbol, period="1y", initial_cash=10000, ma_fast=10, ma_slow=50, stop_loss=0.05):
    print(f"正在回测 {symbol}... MA{ma_fast}/MA{ma_slow} 止损{stop_loss*100:.0f}%")
    df = yf.Ticker(symbol).history(period=period)
    df[f'MA{ma_fast}'] = df['Close'].rolling(ma_fast).mean()
    df[f'MA{ma_slow}'] = df['Close'].rolling(ma_slow).mean()

    df['Signal'] = 0
    df.loc[df[f'MA{ma_fast}'] > df[f'MA{ma_slow}'], 'Signal'] = 1
    df.loc[df[f'MA{ma_fast}'] < df[f'MA{ma_slow}'], 'Signal'] = -1
    df['Position'] = df['Signal'].diff()

    cash = initial_cash
    shares = 0
    buy_price = 0
    portfolio = []
    buys, sells = [], []

    for i, row in df.iterrows():
        if pd.isna(row[f'MA{ma_slow}']):
            portfolio.append(cash + shares * row['Close'])
            continue

        # 止损检查
        if shares > 0 and row['Close'] < buy_price * (1 - stop_loss):
            cash = shares * row['Close']
            sells.append((i, row['Close'], '止损'))
            shares = 0
            buy_price = 0

        # 买入信号
        elif row['Position'] == 1 and cash > 0:
            shares = cash / row['Close']
            buy_price = row['Close']
            cash = 0
            buys.append((i, row['Close']))

        # 卖出信号
        elif row['Position'] == -2 and shares > 0:
            cash = shares * row['Close']
            sells.append((i, row['Close'], '信号'))
            shares = 0
            buy_price = 0

        portfolio.append(cash + shares * row['Close'])

    df['Portfolio'] = portfolio
    df['BuyHold'] = initial_cash * df['Close'] / df['Close'].iloc[0]

    final = df['Portfolio'].iloc[-1]
    bh = df['BuyHold'].iloc[-1]
    ret = (final - initial_cash) / initial_cash * 100
    bh_ret = (bh - initial_cash) / initial_cash * 100

    print(f"\n{'='*45}")
    print(f"  {symbol}  MA{ma_fast}/MA{ma_slow}  止损{stop_loss*100:.0f}%")
    print(f"{'='*45}")
    print(f"  策略收益:   ${final:,.0f}  ({ret:+.1f}%)")
    print(f"  买入持有:   ${bh:,.0f}  ({bh_ret:+.1f}%)")
    print(f"  交易次数:   {len(buys)} 买 / {len(sells)} 卖")
    stop_count = sum(1 for s in sells if s[2] == '止损')
    print(f"  止损触发:   {stop_count} 次")
    print(f"{'='*45}\n")

    # 画图
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.55, 0.45], vertical_spacing=0.05,
                        subplot_titles=(f"{symbol} 价格 + 买卖点", "资金曲线对比"))

    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name="收盘价", line=dict(color='white', width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df[f'MA{ma_fast}'], name=f"MA{ma_fast}", line=dict(color='#ff9800', width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df[f'MA{ma_slow}'], name=f"MA{ma_slow}", line=dict(color='#2196f3', width=1.5)), row=1, col=1)

    if buys:
        bx, by = zip(*buys)
        fig.add_trace(go.Scatter(x=list(bx), y=list(by), mode='markers',
                                 marker=dict(symbol='triangle-up', size=14, color='#00e676'),
                                 name="买入"), row=1, col=1)
    if sells:
        sx = [s[0] for s in sells]
        sy = [s[1] for s in sells]
        sc = ['#ff1744' if s[2]=='信号' else '#ff9800' for s in sells]
        fig.add_trace(go.Scatter(x=sx, y=sy, mode='markers',
                                 marker=dict(symbol='triangle-down', size=14, color=sc),
                                 name="卖出(红=信号 橙=止损)"), row=1, col=1)

    fig.add_trace(go.Scatter(x=df.index, y=df['Portfolio'],
                             name=f"策略 ({ret:+.1f}%)", line=dict(color='#00e676', width=2)), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['BuyHold'],
                             name=f"买入持有 ({bh_ret:+.1f}%)", line=dict(color='#2196f3', width=2)), row=2, col=1)

    fig.update_layout(template="plotly_dark", height=720,
                      title=f"{symbol} | MA{ma_fast}/MA{ma_slow} | 止损{stop_loss*100:.0f}% | 初始${initial_cash:,}")
    fig.show()

# ========== 修改参数试试不同组合 ==========
backtest("NVDA", period="1y", initial_cash=10000, ma_fast=10, ma_slow=50, stop_loss=0.05)
