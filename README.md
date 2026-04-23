# XAUUSD Market Telemetry

This repository hosts an automated data pipeline that fetches daily closing prices and technical metadata for the **XAUUSD (Gold/USD)** pair.

## 🏗 Architecture
- **Data Source:** Yahoo Finance API (`yfinance`)
- **Automation Engine:** GitHub Actions
- **Storage:** JSON format appended daily (`data/xauusd_daily.json`)
- **Schedule:** Automated execution every night at 00:00 (TRT)

## 🎯 Purpose
This project serves as a reliable telemetry engine, ensuring consistent data collection for downstream quantitative analysis, algorithmic trading, and backtesting frameworks. By utilizing an automated CI/CD pipeline, the state is managed autonomously without manual intervention.

## 🚀 How It Works
The `.github/workflows/daily_update.yml` workflow triggers a Python script (`fetch_data.py`) daily. The script pulls the latest market data, appends it to the JSON datastore, and automatically commits the changes back to this repository.
