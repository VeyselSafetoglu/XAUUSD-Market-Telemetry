import yfinance as yf
import pandas as pd
import json
from datetime import datetime
import os

def fetch_xauusd_data():
    print("Fetching XAUUSD data...")
    # XAUUSD ticker in Yahoo Finance
    ticker = "XAUUSD=X"
    gold = yf.Ticker(ticker)
    
    # Get last 5 days to ensure we have data even on weekends/holidays
    hist = gold.history(period="5d")
    
    if hist.empty:
        print("Error: No data fetched from yfinance.")
        return
    
    # Get the latest available day's data
    latest = hist.iloc[-1]
    
    # Format the data
    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": "XAUUSD",
        "close": round(latest["Close"], 3),
        "open": round(latest["Open"], 3),
        "high": round(latest["High"], 3),
        "low": round(latest["Low"], 3),
        "volume": int(latest["Volume"]) if pd.notna(latest["Volume"]) else 0
    }
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    filepath = "data/xauusd_daily.json"
    existing_data = []
    
    # Read existing data if file exists
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                pass
                
    # Append the new record
    existing_data.append(data)
    
    # Write back to JSON
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=4)
        
    print(f"Success! Data saved for {data['timestamp']} -> Close: {data['close']}")

if __name__ == "__main__":
    fetch_xauusd_data()
