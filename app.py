import yfinance as yf
import streamlit as st
import plotly.graph_objects as go
from modules.ticker_manager import load_tickers, add_ticker, remove_ticker
from modules.price_analysis import get_price_analysis
from modules.sentiment import get_stocktwits_sentiment
from modules.signal import get_signal
from modules.diagnosis import get_diagnosis
from config import send_telegram

st.set_page_config(page_title="ISSP", layout="wide")

# ── CSS ──────────────────────────────────────────
st.markdown("""
<style>
body { font-family: 'Segoe UI', sans-serif; }
.metric-card {
    background: white;
    border: 0.5px solid #e0e0e0;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 8px;
}
.card-label { font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px; }
.card-value { font-size: 26px; font-weight: 500; }
.card-sub   { font-size: 12px; margin-top: 4px; }
.green { color: #27500A; }
.red   { color: #A32D2D; }
.amber { color: #854F0B; }
.blue  { color: #185FA5; }
.section-title {
    font-size: 11px; font-weight: 500;
    color: #888; text-transform: uppercase;
    letter-spacing: 0.1em; margin: 20px 0 10px;
}
.comment-pos { background:#F4FAF0; border:0.5px solid #C0DD97; border-radius:8px; padding:10px 14px; margin-bottom:6px; color:#27500A; font-size:13px; }
.comment-neg { background:#FEF5F5; border:0.5px solid #F7C1C1; border-radius:8px; padding:10px 14px; margin-bottom:6px; color:#791F1F; font-size:13px; }
.comment-neu { background:#F5F5F5; border:0.5px solid #ddd;    border-radius:8px; padding:10px 14px; margin-bottom:6px; color:#555;    font-size:13px; }
.signal-buy  { background:#EAF3DE; border:0.5px solid #97C459; border-radius:12px; padding:16px 20px; }
.signal-sell { background:#FEF5F5; border:0.5px solid #F7C1C1; border-radius:12px; padding:16px 20px; }
.signal-hold { background:#F5F5F5; border:0.5px solid #CBD5E1; border-radius:12px; padding:16px 20px; }
.signal-watch{ background:#E6F1FB; border:0.5px solid #85B7EB; border-radius:12px; padding:16px 20px; }
</style>
""", unsafe_allow_html=True)

# ── 헤더 ─────────────────────────────────────────
st.markdown("## ISSP")
st.caption("Individual Stock Sentiment & Price Analysis System")
st.divider()

# ── 티커 관리 ─────────────────────────────────────
st.markdown('<div class="section-title">Watch List</div>', unsafe_allow_html=True)

tickers = load_tickers()

col_input, col_btn, col_del = st.columns([3, 1, 1])
with col_input:
    new_ticker = st.text_input("", placeholder="티커 입력 (예: TSLA)", label_visibility="collapsed")
with col_btn:
    if st.button("➕ 추가"):
        if new_ticker:
            result = add_ticker(new_ticker)
            if result:
                st.success(f"{new_ticker.upper()} 추가됨")
                st.rerun()
            else:
                st.warning("이미 존재하는 티커입니다")
with col_del:
    if st.button("🗑 삭제"):
        if new_ticker:
            result = remove_ticker(new_ticker)
            if result:
                st.success(f"{new_ticker.upper()} 삭제됨")
                st.rerun()
            else:
                st.warning("존재하지 않는 티커입니다")

tickers = load_tickers()
if not tickers:
    st.info("티커를 추가해주세요. 예: TSLA, NVDA, AAPL")
    st.stop()

selected = st.pills("", tickers, default=tickers[0])
st.divider()

if not selected:
    st.stop()

# ── 데이터 로딩 ───────────────────────────────────
with st.spinner(f"{selected} 데이터 불러오는 중..."):
    price_data     = get_price_analysis(selected)
    sentiment_data = get_stocktwits_sentiment(selected)
    signal_data    = get_signal(sentiment_data, price_data)
    diagnosis_text = get_diagnosis(selected, sentiment_data, price_data, signal_data)

# ── 주가 현황 ─────────────────────────────────────
st.markdown('<div class="section-title">주가 현황</div>', unsafe_allow_html=True)

if price_data:
    c1, c2, c3 = st.columns(3)

    price_color = "green" if price_data['deviation'] >= 0 else "red"
    dev_color   = "amber" if abs(price_data['deviation']) < 10 else "red"
    vol_color   = "red" if price_data['volume_ratio'] >= 100 else "amber" if price_data['volume_ratio'] >= 30 else "blue"

    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="card-label">현재가</div>
            <div class="card-value {price_color}">${price_data['current_price']}</div>
            <div class="card-sub {price_color}">20일 MA ${price_data['ma20']}</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="card-label">이격도 (20일 MA 대비)</div>
            <div class="card-value {dev_color}">{price_data['deviation']:+.1f}%</div>
            <div class="card-sub {dev_color}">{price_data['deviation_status']}</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="card-label">거래량 (평균 대비)</div>
            <div class="card-value {vol_color}">{price_data['volume_ratio']:+.1f}%</div>
            <div class="card-sub {vol_color}">{price_data['volume_status']}</div>
        </div>""", unsafe_allow_html=True)

# ── 티커 로고 + 주가 그래프 ─────────────────────────
if price_data:
    # 로고 - yfinance에서 웹사이트 도메인 자동 추출
    # 로고 + 티커명
    try:
        info = yf.Ticker(selected).info
        website = info.get('website', '')
        if website:
            domain = website.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
            logo_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=64"
            st.markdown(
                f"""
                <div style="display:flex; align-items:center; gap:10px; margin:8px 0 4px 4px;">
                    <img src="{logo_url}" width="28" style="border-radius:6px;"/>
                    <span style="font-size:20px; font-weight:500; color:var(--text-color);">{selected}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(f"### {selected}")
    except:
        st.markdown(f"### {selected}")

    # 주가 + 20일 MA 그래프 (6개월)
    hist = yf.Ticker(selected).history(period="6mo")
    ma20 = hist['Close'].rolling(20).mean()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=hist.index,
        y=hist['Close'],
        name='주가',
        line=dict(color='#378ADD', width=2),
        hovertemplate='%{x|%m/%d}<br>$%{y:.2f}<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=hist.index,
        y=ma20,
        name='20일 MA',
        line=dict(color='#EF9F27', width=1.5, dash='dot'),
        hovertemplate='%{x|%m/%d}<br>MA $%{y:.2f}<extra></extra>'
    ))

    if sentiment_data:
        score = sentiment_data['score']
        dot_color = '#27500A' if score >= 65 else '#A32D2D' if score <= 35 else '#854F0B'
        fig.add_trace(go.Scatter(
            x=[hist.index[-1]],
            y=[hist['Close'].iloc[-1]],
            mode='markers+text',
            name=f'현재 심리 {score}점',
            marker=dict(color=dot_color, size=12),
            text=[f'  심리 {score}점'],
            textposition='middle right',
            textfont=dict(color=dot_color, size=12),
            hovertemplate=f'심리 점수: {score}점<extra></extra>'
        ))

    fig.update_layout(
        height=320,
        margin=dict(l=0, r=60, t=10, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0),
        xaxis=dict(showgrid=False, color='#888'),
        yaxis=dict(showgrid=True, gridcolor='#f0f0f0', color='#888'),
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)

# ── 심리 분석 ─────────────────────────────────────
st.markdown('<div class="section-title">StockTwits 심리 분석</div>', unsafe_allow_html=True)

if sentiment_data:
    col_score, col_stat = st.columns([2, 1])

    with col_score:
        score = sentiment_data['score']
        st.markdown(f"""
        <div class="metric-card">
            <div class="card-label">종합 심리 점수</div>
            <div class="card-value {'green' if score >= 65 else 'red' if score <= 35 else 'amber'}">
                {score}점 <span style="font-size:14px;color:#888;">/ 100</span>
            </div>
            <div class="card-sub">{sentiment_data['sentiment_label']} · {sentiment_data['sentiment_eng']} · 분석 댓글 {sentiment_data['total_comments']}개</div>
        </div>""", unsafe_allow_html=True)
        st.progress(score / 100)

    with col_stat:
        st.markdown(f"""
        <div class="metric-card" style="height:100%">
            <div class="card-label">긍정 / 중립 / 부정</div>
            <div style="margin-top:8px;">
                <span class="green" style="font-size:18px;font-weight:500;">{sentiment_data['positive_pct']}%</span>
                <span style="color:#aaa;margin:0 6px;">/</span>
                <span style="font-size:18px;font-weight:500;color:#888;">{sentiment_data['neutral_pct']}%</span>
                <span style="color:#aaa;margin:0 6px;">/</span>
                <span class="red" style="font-size:18px;font-weight:500;">{sentiment_data['negative_pct']}%</span>
            </div>
        </div>""", unsafe_allow_html=True)

    # 댓글 샘플 페이지네이션
st.markdown('<div class="section-title">댓글 샘플</div>', unsafe_allow_html=True)

if sentiment_data:
    all_samples = sentiment_data['samples']
    
    PAGE_SIZE = 5
    total_pages = (len(all_samples) - 1) // PAGE_SIZE + 1
    
    # 티커 변경 시 댓글 페이지 리셋
    if 'current_ticker' not in st.session_state or st.session_state.current_ticker != selected:
        st.session_state.comment_page = 0
        st.session_state.current_ticker = selected

    if 'comment_page' not in st.session_state:
        st.session_state.comment_page = 0

    start = st.session_state.comment_page * PAGE_SIZE
    end = start + PAGE_SIZE
    page_samples = all_samples[start:end]

    for s in page_samples:
        sc = s['score']
        if sc >= 5:
            st.markdown(f'<div class="comment-pos">+{sc} &nbsp; {s["text"]}</div>', unsafe_allow_html=True)
        elif sc <= -5:
            st.markdown(f'<div class="comment-neg">{sc} &nbsp; {s["text"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="comment-neu">{sc} &nbsp; {s["text"]}</div>', unsafe_allow_html=True)

    # 페이지 네비게이션
    col_prev, col_info, col_next = st.columns([1, 3, 1])
    with col_prev:
        if st.button("◀ 이전", disabled=st.session_state.comment_page == 0):
            st.session_state.comment_page -= 1
            st.rerun()
    with col_info:
        st.markdown(
            f'<div style="text-align:center; color:#888; font-size:12px; padding-top:8px;">'
            f'{start+1}~{min(end, len(all_samples))} / 총 {len(all_samples)}개</div>',
            unsafe_allow_html=True
        )
    with col_next:
        if st.button("다음 ▶", disabled=st.session_state.comment_page >= total_pages - 1):
            st.session_state.comment_page += 1
            st.rerun()

# ── 심리-주가 매트릭스 ─────────────────────────────
st.markdown('<div style="font-size:15px; font-weight:600; color:#111; text-transform:uppercase; letter-spacing:.08em; margin:20px 0 10px;">심리 × 주가 포지션</div>', unsafe_allow_html=True)

if sentiment_data and price_data:
    score = sentiment_data['score']
    deviation = price_data['deviation']

    # X축: 이격도 → -15 ~ +15 범위로 정규화
    x = max(-15, min(15, deviation))
    # Y축: 심리 점수 → 0~100
    y = score

    # 격자 색상 (3x3, 왼쪽아래부터)
    # y축: 공포(0-35) / 정상(35-65) / 탐욕(65-100)
    # x축: 저평가(-15~-5) / 정상(-5~5) / 과열(5~15)
    zone_colors = [
        # 공포행
        ['#C8E6C9', '#FFF9C4', '#FFCCBC'],  # 공포+저평가=매수, 공포+정상=관망, 공포+과열=주의
        # 정상행
        ['#DCEDC8', '#F5F5F5', '#FFE0B2'],  # 정상+저평가=관심, 정상+정상=중립, 정상+과열=주의
        # 탐욕행
        ['#FFF9C4', '#FFE0B2', '#FFCCBC'],  # 탐욕+저평가=관심, 탐욕+정상=주의, 탐욕+과열=매도
    ]

    zone_labels = [
        ['🟢 역발상\n매수', '🟡 관망', '⚠️ 하락\n경고'],
        ['🟡 관심', '⚪ 중립', '🟡 주의'],
        ['🟡 관심', '⚠️ 주의', '🔴 전략적\n매도'],
    ]

    fig2 = go.Figure()

    # 격자 배경 색상
    x_bounds = [-15, -10, 10, 15]
    y_bounds = [0, 35, 65, 100]

    for row in range(3):
        for col in range(3):
            x0, x1 = x_bounds[col], x_bounds[col+1]
            y0, y1 = y_bounds[row], y_bounds[row+1]
            color = zone_colors[row][col]
            label = zone_labels[row][col]

            fig2.add_shape(
                type='rect',
                x0=x0, x1=x1, y0=y0, y1=y1,
                fillcolor=color,
                line=dict(color='#ddd', width=1),
                layer='below'
            )
            fig2.add_annotation(
                x=(x0+x1)/2, y=(y0+y1)/2,
                text=label,
                showarrow=False,
                font=dict(size=11, color='#555'),
                align='center'
            )

    # 현재 종목 위치 점
    fig2.add_trace(go.Scatter(
        x=[x], y=[y],
        mode='markers+text',
        marker=dict(
            size=16,
            color='#185FA5',
            line=dict(color='white', width=2),
            symbol='circle'
        ),
        text=[f"  {selected}"],
        textposition='middle right',
        textfont=dict(size=13, color='#185FA5'),
        hovertemplate=f"{selected}<br>심리: {score}점<br>이격도: {deviation:+.1f}%<extra></extra>"
    ))

    # 축 구분선
    fig2.add_shape(type='line', x0=-10, x1=-10, y0=0, y1=100,
                   line=dict(color='#bbb', width=1.5, dash='dot'))
    fig2.add_shape(type='line', x0=10, x1=10, y0=0, y1=100,
                   line=dict(color='#bbb', width=1.5, dash='dot'))
    fig2.add_shape(type='line', x0=-15, x1=15, y0=35, y1=35,
                   line=dict(color='#bbb', width=1.5, dash='dot'))
    fig2.add_shape(type='line', x0=-15, x1=15, y0=65, y1=65,
                   line=dict(color='#bbb', width=1.5, dash='dot'))

    fig2.update_layout(
        height=380,
        margin=dict(l=60, r=40, t=40, b=80),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        xaxis=dict(
            range=[-16, 16],
            tickvals=[-15, -10, -5, 0, 5, 10, 15],
            ticktext=[
                '주가 매우 낮음<br>(-15%)',
                '-10%',
                '-5%',
                '정상 범위<br>(0%)',
                '+5%',
                '+10%',
                '주가 매우 높음<br>(+15%)'
            ],
            title='주가 이격도 (20일 MA 대비)',
            title_font=dict(size=12, color='#111'),
            tickfont=dict(color='#111'),
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            range=[-2, 102],
            tickvals=[0, 35, 50, 65, 100],
            ticktext=['0<br>공포', '35', '50<br>중립', '65', '100<br>탐욕'],
            title='심리 점수',
            title_font=dict(size=12, color='#111'),
            tickfont=dict(color='#111'),
            showgrid=False,
            zeroline=False
        )
    )

    st.plotly_chart(fig2, use_container_width=True)

# ── 종합 진단 + 신호 ──────────────────────────────
st.markdown('<div class="section-title">종합 진단</div>', unsafe_allow_html=True)

if signal_data:
    signal = signal_data['signal']
    css_class = {
        "BUY": "signal-buy",
        "SELL": "signal-sell",
        "HOLD": "signal-hold",
        "WATCH": "signal-watch"
    }.get(signal, "signal-hold")

    st.markdown(f'<div class="{css_class}">{diagnosis_text}</div>', unsafe_allow_html=True)

    # 텔레그램 알림
    if signal in ["BUY", "SELL"]:
        if st.button("📲 텔레그램 알림 전송"):
            send_telegram(f"[ISSP 알림] {selected}\n\n{diagnosis_text}")
            st.success("텔레그램으로 알림을 전송했습니다!")

st.divider()
st.caption("ISSP · StockTwits 기반 개별 종목 심리 분석 시스템")