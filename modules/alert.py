from modules.ticker_manager import load_tickers
from modules.sentiment import get_stocktwits_sentiment
from modules.price_analysis import get_price_analysis
from modules.signal import get_signal
from modules.diagnosis import get_diagnosis
from config import send_telegram

def check_and_alert():
    tickers = load_tickers()
    for ticker in tickers:
        sentiment_data = get_stocktwits_sentiment(ticker)
        price_data = get_price_analysis(ticker)
        signal_data = get_signal(sentiment_data, price_data)

        if signal_data and signal_data['signal'] in ['BUY', 'SELL']:
            diagnosis = get_diagnosis(ticker, sentiment_data, price_data, signal_data)
            send_telegram(f"[ISSP 자동 알림]\n\n{diagnosis}")
            print(f"{ticker} 알림 전송 완료")

if __name__ == "__main__":
    check_and_alert()