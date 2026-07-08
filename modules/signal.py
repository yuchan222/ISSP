def get_signal(sentiment_data, price_data):
    if not sentiment_data or not price_data:
        return None

    score = sentiment_data['score']
    deviation = price_data['deviation']
    volume_ratio = price_data['volume_ratio']

    # 매수 신호: 심리 침체 + 주가 저평가
    if score <= 35 and deviation <= -10:
        signal = "BUY"
        signal_kor = "🟢 역발상 매수 구간"
        reason = (
            f"대중 심리가 침체({score}점)이고 "
            f"주가가 20일 평균 대비 {deviation}% 저평가 상태입니다. "
            f"역발상 매수 기회일 수 있습니다."
        )

    # 매도 신호: 심리 과열 + 주가 과열
    elif score >= 65 and deviation >= 10:
        signal = "SELL"
        signal_kor = "🔴 전략적 매도 구간"
        reason = (
            f"대중 심리가 과열({score}점)이고 "
            f"주가가 20일 평균 대비 {deviation}% 과열 상태입니다. "
            f"전략적 매도를 고려할 구간입니다."
        )

    # 거래량 폭증 단독 경고
    elif volume_ratio >= 100:
        signal = "WATCH"
        signal_kor = "🟡 거래량 급등 관망"
        reason = (
            f"거래량이 평균 대비 {volume_ratio}% 급증했습니다. "
            f"단기 변동성 확대 가능성이 있으니 관망을 권장합니다."
        )

    # 관망
    else:
        signal = "HOLD"
        signal_kor = "⚪ 중립 구간"
        reason = (
            f"현재 심리({score}점)와 주가 이격도({deviation}%)가 "
            f"특별한 신호를 보이지 않습니다. 보유 및 관망을 권장합니다."
        )

    return {
        "signal": signal,
        "signal_kor": signal_kor,
        "reason": reason
    }