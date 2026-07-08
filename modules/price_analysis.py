import yfinance as yf

def get_price_analysis(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="6mo")

    if hist.empty:
        return None

    # 현재가
    current_price = hist['Close'].dropna().iloc[-1]

    # 20일 이동평균 및 이격도
    ma20 = hist['Close'].dropna().tail(20).mean()
    deviation = ((current_price - ma20) / ma20) * 100

    # 거래량 분석
    current_volume = hist['Volume'].dropna().iloc[-1]
    avg_volume = hist['Volume'].dropna().tail(20).mean()
    volume_ratio = ((current_volume - avg_volume) / avg_volume) * 100

    # 이격도 진단
    if deviation >= 10:
        deviation_status = "심각한 과열 구간"
    elif deviation >= 5:
        deviation_status = "단기 과열 구간"
    elif deviation <= -10:
        deviation_status = "심각한 침체 구간"
    elif deviation <= -5:
        deviation_status = "단기 침체 구간"
    else:
        deviation_status = "정상 구간"

    # 거래량 진단
    if volume_ratio >= 100:
        volume_status = "거래 폭증"
    elif volume_ratio >= 30:
        volume_status = "거래 활발"
    elif volume_ratio <= -30:
        volume_status = "거래 급감"
    else:
        volume_status = "거래 보통"

    return {
        "ticker": ticker,
        "current_price": round(current_price, 2),
        "ma20": round(ma20, 2),
        "deviation": round(deviation, 2),
        "deviation_status": deviation_status,
        "current_volume": int(current_volume),
        "avg_volume": int(avg_volume),
        "volume_ratio": round(volume_ratio, 2),
        "volume_status": volume_status
    }