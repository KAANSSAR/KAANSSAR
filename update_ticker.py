"""
Fetches live-ish quotes for a watchlist from Yahoo Finance's public chart
endpoint (no API key required) and regenerates ticker-header.svg.
Run on a schedule via .github/workflows/update-ticker.yml
"""
import json
import urllib.request
from render_ticker import build

SYMBOLS = ["AAPL", "NVDA", "TSLA", "MSFT"]
UA = "Mozilla/5.0 (compatible; ticker-header-bot/1.0)"

def fetch_quote(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1mo"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        result = data["chart"]["result"][0]
        meta = result["meta"]
        price = meta.get("regularMarketPrice")
        prev_close = meta.get("chartPreviousClose") or meta.get("previousClose")
        closes = result["indicators"]["quote"][0].get("close", [])
        closes = [c for c in closes if c is not None]
        pct = None
        if price is not None and prev_close:
            pct = (price - prev_close) / prev_close * 100
        return {
            "symbol": symbol,
            "price": price,
            "pct": pct,
            "history": closes[-20:] if closes else [],
        }
    except Exception as e:
        print(f"warn: failed to fetch {symbol}: {e}")
        return {"symbol": symbol, "price": None, "pct": None, "history": []}

def main():
    stocks = [fetch_quote(s) for s in SYMBOLS]
    svg = build(stocks)
    with open("ticker-header.svg", "w") as f:
        f.write(svg)
    print("wrote ticker-header.svg")

if __name__ == "__main__":
    main()
