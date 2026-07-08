import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json'
}

def get_stocktwits_sentiment(ticker):
    url = f"https://api.stocktwits.com/api/2/streams/symbol/{ticker}.json"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        data = response.json()
    except Exception as e:
        return None

    if 'messages' not in data:
        return None

    messages = data['messages']
    
    scores = []
    samples = []

    for msg in messages:
        text = msg.get('body', '')
        score = analyzer.polarity_scores(text)['compound']
        scores.append(score)

        if len(samples) < 30:
            samples.append({
                "text": text,
                "score": round(score * 100)
            })

    if not scores:
        return None

    avg_score = sum(scores) / len(scores)
    normalized = round((avg_score + 1) / 2 * 100)

    positive = len([s for s in scores if s >= 0.05])
    negative = len([s for s in scores if s <= -0.05])
    neutral = len(scores) - positive - negative
    total = len(scores)

    if normalized >= 65:
        sentiment_label = "긍정적"
        sentiment_eng = "Bullish"
    elif normalized <= 35:
        sentiment_label = "부정적"
        sentiment_eng = "Bearish"
    else:
        sentiment_label = "중립적"
        sentiment_eng = "Neutral"

    return {
        "ticker": ticker,
        "score": normalized,
        "sentiment_label": sentiment_label,
        "sentiment_eng": sentiment_eng,
        "total_comments": total,
        "positive_pct": round(positive / total * 100),
        "neutral_pct": round(neutral / total * 100),
        "negative_pct": round(negative / total * 100),
        "samples": samples
    }