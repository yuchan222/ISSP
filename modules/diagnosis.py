def get_diagnosis(ticker, sentiment_data, price_data, signal_data):
    if not sentiment_data or not price_data or not signal_data:
        return "데이터를 불러오는 중 오류가 발생했습니다."

    score = sentiment_data['score']
    sentiment_label = sentiment_data['sentiment_label']
    deviation = price_data['deviation']
    deviation_status = price_data['deviation_status']
    volume_ratio = price_data['volume_ratio']
    volume_status = price_data['volume_status']
    signal = signal_data['signal']
    signal_kor = signal_data['signal_kor']

    # 심리 vs 주가 괴리 분석
    if score >= 65 and deviation <= -5:
        gap_insight = (
            f"대중은 {ticker}에 낙관적이지만 주가는 아직 평균 이하입니다. "
            f"시장이 심리를 따라잡기 전 선제 매수 기회일 수 있습니다."
        )
    elif score <= 35 and deviation >= 5:
        gap_insight = (
            f"대중은 {ticker}에 비관적이지만 주가는 이미 고평가 상태입니다. "
            f"하락 전환 가능성을 주의해야 합니다."
        )
    elif score >= 65 and deviation >= 5:
        gap_insight = (
            f"심리와 주가가 동시에 과열 상태입니다. "
            f"환희 구간 진입 가능성이 높으며 추격 매수는 위험합니다."
        )
    elif score <= 35 and deviation <= -5:
        gap_insight = (
            f"심리와 주가가 동시에 침체 상태입니다. "
            f"공포가 극에 달한 구간으로 역발상 매수의 최적 타이밍일 수 있습니다."
        )
    else:
        gap_insight = (
            f"심리와 주가 모두 특별한 극단 신호 없이 안정적인 흐름을 보입니다."
        )

    # 거래량 인사이트
    if volume_ratio >= 100:
        vol_insight = f"거래량이 평균의 {volume_ratio}% 수준으로 폭증하고 있어 단기 급변동 가능성이 있습니다."
    elif volume_ratio >= 30:
        vol_insight = f"거래량이 평균 대비 활발한 상태로 시장의 관심이 높아지고 있습니다."
    elif volume_ratio <= -30:
        vol_insight = f"거래량이 급감하여 시장 관심이 식고 있어 방향성 판단에 주의가 필요합니다."
    else:
        vol_insight = f"거래량은 평균 수준으로 안정적입니다."

    diagnosis = (
        f"{signal_kor}\n\n"
        f"{ticker} · 심리 {score}점 · 이격도 {deviation:+.1f}% · 거래량 {volume_ratio:+.1f}%\n\n"
        f"{gap_insight} {vol_insight}"
    )

    return diagnosis