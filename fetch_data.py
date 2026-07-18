import yfinance as yf
import pandas as pd
import json
import sys
import time
import os
from datetime import datetime, timezone


# Fallback ticker list — if one dies on Yahoo Finance, the next is tried.
# GC=F  = COMEX Gold Futures (most reliable proxy for spot gold)
# GLD   = SPDR Gold Shares ETF
# IAU   = iShares Gold Trust ETF
TICKER_CANDIDATES = ["GC=F", "GLD", "IAU"]


def fetch_xauusd_data():
    """
    Fetch daily gold price data from Yahoo Finance and append to local JSON store.
    Includes multi-ticker fallback, retry logic, and robust error handling
    for long-term unattended use.
    """
    filepath = "data/xauusd_daily.json"
    max_retries = 3

    # --- Fetch with fallback tickers and retries ---
    hist = None
    used_ticker = None

    for ticker_symbol in TICKER_CANDIDATES:
        for attempt in range(1, max_retries + 1):
            try:
                print(f"[{ticker_symbol}] Attempt {attempt}/{max_retries}...")
                ticker = yf.Ticker(ticker_symbol)
                hist = ticker.history(period="5d")
                if hist is not None and not hist.empty:
                    used_ticker = ticker_symbol
                    break
                print(f"  Warning: Empty dataframe returned.")
            except Exception as e:
                print(f"  Error: {e}")
            if attempt < max_retries:
                wait = attempt * 10
                print(f"  Retrying in {wait}s...")
                time.sleep(wait)

        if hist is not None and not hist.empty:
            break
        print(f"  Ticker {ticker_symbol} failed, trying next fallback...")

    if hist is None or hist.empty:
        print("FATAL: All tickers failed after all retries. Exiting.")
        sys.exit(1)

    print(f"  Using ticker: {used_ticker}")

    # --- Build record ---
    latest = hist.iloc[-1]
    now_utc = datetime.now(timezone.utc)
    today_str = now_utc.strftime("%Y-%m-%d")

    data = {
        "date": today_str,
        "timestamp": now_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "symbol": "XAUUSD",
        "source_ticker": used_ticker,
        "open": round(float(latest["Open"]), 2),
        "high": round(float(latest["High"]), 2),
        "low": round(float(latest["Low"]), 2),
        "close": round(float(latest["Close"]), 2),
        "volume": int(latest["Volume"]) if pd.notna(latest["Volume"]) else 0,
    }

    # --- Read existing data ---
    os.makedirs("data", exist_ok=True)
    existing_data = []

    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            print("Warning: Corrupted JSON detected, creating backup.")
            backup = filepath + ".bak"
            try:
                os.replace(filepath, backup)
                print(f"  Backed up to {backup}")
            except OSError:
                pass

    # --- Deduplicate: skip if today's date already exists ---
    existing_dates = {r.get("date") for r in existing_data if isinstance(r, dict)}
    if today_str in existing_dates:
        print(f"Data for {today_str} already exists. Skipping.")
        return

    # --- Append and write ---
    existing_data.append(data)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=4, ensure_ascii=False)

    print(f"OK -> {data['date']} | Close: {data['close']} | Ticker: {used_ticker}")


if __name__ == "__main__":
    fetch_xauusd_data()
