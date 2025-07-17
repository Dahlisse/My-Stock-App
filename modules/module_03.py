# module_03.py
import streamlit as st
import numpy as np
import pandas as pd

def calc_moving_average(series, window):
    return series.rolling(window=window).mean()

def calc_rsi(series, window=14):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ma_up = up.rolling(window=window).mean()
    ma_down = down.rolling(window=window).mean()
    rs = ma_up / (ma_down + 1e-9)
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calc_macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def detect_golden_dead_cross(ma_short, ma_long):
    cross = (ma_short > ma_long) & (ma_short.shift(1) <= ma_long.shift(1))
    golden_cross = cross.any()
    cross_dead = (ma_short < ma_long) & (ma_short.shift(1) >= ma_long.shift(1))
    dead_cross = cross_dead.any()
    return golden_cross, dead_cross

def sentiment_score_from_news(news_texts):
    # 단순 감성 분석 예시 (실제론 NLP모델 연동 필요)
    positive_words = ['상승', '호재', '강세', '이익', '성장']
    negative_words = ['하락', '악재', '약세', '손실', '위험']

    score = 0
    for text in news_texts:
        text = text.lower()
        for w in positive_words:
            if w in text:
                score += 1
        for w in negative_words:
            if w in text:
                score -= 1
    return np.tanh(score / (len(news_texts) + 1e-6))  # -1 ~ 1 사이 값

def valuation_score(per, pbr, sector_per_avg, sector_pbr_avg):
    """
    PER/PBR 업종평균 대비 점수 산출 (낮을수록 고평가 아님)
    0~100 스케일
    """
    per_score = max(0, min(100, 100 * (sector_per_avg / (per + 1e-6))))
    pbr_score = max(0, min(100, 100 * (sector_pbr_avg / (pbr + 1e-6))))
    return (per_score + pbr_score) / 2

def technical_score(close_prices: pd.Series):
    """
    MA, RSI, MACD 지표 통합 점수 계산 (0~100)
    """
    ma_short = calc_moving_average(close_prices, 20)
    ma_long = calc_moving_average(close_prices, 60)
    golden_cross, dead_cross = detect_golden_dead_cross(ma_short, ma_long)
    rsi = calc_rsi(close_prices).iloc[-1]
    macd_line, signal_line, hist = calc_macd(close_prices)
    macd_signal_diff = macd_line.iloc[-1] - signal_line.iloc[-1]

    score = 50  # 중간값 기준

    if golden_cross:
        score += 20
    if dead_cross:
        score -= 20

    if rsi is not None:
        if rsi < 30:
            score += 10  # 과매도 반등 기대
        elif rsi > 70:
            score -= 10  # 과매수 주의

    if macd_signal_diff > 0:
        score += 10
    else:
        score -= 10

    return max(0, min(100, score))

def integrate_strategy_scores(valuation, technical, sentiment, weights=(0.4, 0.4, 0.2)):
    """
    밸류에이션, 기술, 심리 점수를 가중합
    weights 합 = 1.0
    """
    total_score = valuation * weights[0] + technical * weights[1] + ((sentiment + 1) / 2) * weights[2] * 100
    return max(0, min(100, total_score))

def module_03_main(
    close_prices: pd.Series,
    per: float,
    pbr: float,
    sector_per_avg: float,
    sector_pbr_avg: float,
    news_texts: list[str],
    show_details=True
):
    st.header("📘 3단원. 통합 전략 판단 시스템")

    # 3.1 밸류에이션 점수
    val_score = valuation_score(per, pbr, sector_per_avg, sector_pbr_avg)
    if show_details:
        st.write(f"밸류에이션 점수 (PER, PBR 비교 기반): {val_score:.1f}/100")

    # 3.2 기술적 분석 점수
    tech_score = technical_score(close_prices)
    if show_details:
        st.write(f"기술적 분석 점수 (MA, RSI, MACD 기반): {tech_score:.1f}/100")

    # 3.3 심리·이슈 분석 점수
    senti_score = sentiment_score_from_news(news_texts)
    if show_details:
        st.write(f"심리·이슈 점수 (뉴스 감성 분석): {senti_score:.3f} (-1~1)")

    # 3.4 전략 통합 점수
    total_score = integrate_strategy_scores(val_score, tech_score, senti_score)
    st.subheader("종합 전략 점수 (밸류 × 기술 × 심리 통합)")
    st.write(f"{total_score:.1f}/100")

    # 진입 추천 여부
    recommendation = "진입 추천" if total_score > 60 else "관망 또는 청산 검토"
    st.write(f"👉 전략 판단: **{recommendation}**")

    # 3.5 추가 확장 - 시나리오 분기 예시
    if total_score > 80:
        scenario = "상승 전략: 적극 매수 및 포지션 확대"
    elif total_score > 60:
        scenario = "보합 전략: 부분 매수 또는 모니터링"
    else:
        scenario = "하락 전략: 청산 또는 대기"
    st.write(f"▶ 전략 시나리오: {scenario}")

    return {
        "valuation_score": val_score,
        "technical_score": tech_score,
        "sentiment_score": senti_score,
        "total_score": total_score,
        "recommendation": recommendation,
        "scenario": scenario
    }

if __name__ == "__main__":
    st.title("Module 03 통합 전략 판단 시스템 테스트")

    # 테스트용 더미 종가 데이터 생성 (랜덤 워크)
    np.random.seed(42)
    days = pd.date_range(start="2023-01-01", periods=100)
    prices = pd.Series(100 + np.cumsum(np.random.randn(100)), index=days)

    # 테스트용 지표 및 뉴스 텍스트
    per = 15
    pbr = 1.2
    sector_per_avg = 18
    sector_pbr_avg = 1.5
    news_texts = [
        "최근 기업의 이익 상승 기대감이 커지고 있습니다.",
        "시장에서는 강세 흐름이 이어지고 있다는 평가입니다.",
        "다만 일부 악재 소식도 존재합니다."
    ]

    module_03_main(prices, per, pbr, 
sector_per_avg, sector_pbr_avg,
news_texts)