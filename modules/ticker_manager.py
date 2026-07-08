import json
import os

TICKER_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'tickers.json')

def load_tickers():
    if not os.path.exists(TICKER_FILE):
        return []
    with open(TICKER_FILE, 'r') as f:
        return json.load(f)

def save_tickers(tickers):
    with open(TICKER_FILE, 'w') as f:
        json.dump(tickers, f)

def add_ticker(ticker):
    tickers = load_tickers()
    ticker = ticker.upper().strip()
    if ticker not in tickers:
        tickers.append(ticker)
        save_tickers(tickers)
        return True
    return False  # 이미 존재

def remove_ticker(ticker):
    tickers = load_tickers()
    ticker = ticker.upper().strip()
    if ticker in tickers:
        tickers.remove(ticker)
        save_tickers(tickers)
        return True
    return False  # 존재하지 않음