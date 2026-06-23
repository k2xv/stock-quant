import yfinance as yf
from rich.console import Console
from rich.table import Table
from rich import box
from datetime import datetime

console = Console()

def get_stock_info(symbol):
    """获取股票信息"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="2d")

        if hist.empty:
            return None

        current_price = hist['Close'].iloc[-1]
        prev_price = hist['Close'].iloc[-2] if len(hist) >= 2 else current_price
        change = current_price - prev_price
        change_pct = (change / prev_price) * 100
        volume = hist['Volume'].iloc[-1]

        return {
            "symbol": symbol.upper(),
            "name": info.get("shortName", symbol),
            "price": current_price,
            "change": change,
            "change_pct": change_pct,
            "volume": volume,
            "market_cap": info.get("marketCap", 0),
        }
    except Exception as e:
        console.print(f"[red]获取 {symbol} 数据失败: {e}[/red]")
        return None

def format_volume(vol):
    if vol >= 1_000_000:
        return f"{vol/1_000_000:.1f}M"
    elif vol >= 1_000:
        return f"{vol/1_000:.1f}K"
    return str(int(vol))

def format_market_cap(cap):
    if cap >= 1_000_000_000_000:
        return f"${cap/1_000_000_000_000:.2f}T"
    elif cap >= 1_000_000_000:
        return f"${cap/1_000_000_000:.2f}B"
    elif cap > 0:
        return f"${cap/1_000_000:.2f}M"
    return "N/A"

def show_stocks(symbols):
    """显示股票表格"""
    console.print(f"\n[bold cyan]📈 美股实时监控[/bold cyan] — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    table = Table(box=box.ROUNDED, show_header=True, header_style="bold white")
    table.add_column("代码", style="cyan", width=8)
    table.add_column("名称", width=20)
    table.add_column("价格 (USD)", justify="right", width=12)
    table.add_column("涨跌", justify="right", width=10)
    table.add_column("涨跌幅", justify="right", width=10)
    table.add_column("成交量", justify="right", width=10)
    table.add_column("市值", justify="right", width=12)

    for symbol in symbols:
        data = get_stock_info(symbol)
        if not data:
            continue

        color = "green" if data["change"] >= 0 else "red"
        sign = "+" if data["change"] >= 0 else ""
        arrow = "▲" if data["change"] >= 0 else "▼"

        table.add_row(
            data["symbol"],
            data["name"][:20],
            f"${data['price']:.2f}",
            f"[{color}]{sign}{data['change']:.2f}[/{color}]",
            f"[{color}]{arrow} {sign}{data['change_pct']:.2f}%[/{color}]",
            format_volume(data["volume"]),
            format_market_cap(data["market_cap"]),
        )

    console.print(table)

def price_alert(symbol, target_price, direction="above"):
    """价格提醒：direction = 'above' 或 'below'"""
    data = get_stock_info(symbol)
    if not data:
        return
    price = data["price"]
    if direction == "above" and price >= target_price:
        console.print(f"\n[bold yellow]⚠️  提醒：{symbol} 当前价格 ${price:.2f} 已超过目标 ${target_price}[/bold yellow]")
    elif direction == "below" and price <= target_price:
        console.print(f"\n[bold yellow]⚠️  提醒：{symbol} 当前价格 ${price:.2f} 已低于目标 ${target_price}[/bold yellow]")
    else:
        console.print(f"\n[dim]{symbol} 当前 ${price:.2f}，尚未触发提醒（目标：${target_price}）[/dim]")

# ========== 在这里修改你想监控的股票 ==========
watchlist = ["AAPL", "TSLA", "NVDA", "MSFT", "GOOGL"]

# ========== 价格提醒示例 ==========
alerts = [
    ("AAPL", 200, "above"),   # AAPL 超过 $200 提醒
    ("TSLA", 250, "below"),   # TSLA 低于 $250 提醒
]

if __name__ == "__main__":
    show_stocks(watchlist)

    console.print("\n[bold]价格提醒检查：[/bold]")
    for symbol, price, direction in alerts:
        price_alert(symbol, price, direction)
