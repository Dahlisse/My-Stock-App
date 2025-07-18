# module_03.py

import streamlit as st
import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Any

# 1) 이동평균
def calc_moving_average(series: pd.Series, window: int) -> pd.Series:
    try:
        return series.rolling(window=window, min_periods=1).mean()
    except Exception as e:
        st.error(f"이동평균 계산 오류: {e}")
        return pd.Series(dtype=float)

# 2) RSI
def calc_rsi(series: pd.Series, window: int = 14) -> pd.Series:
    try:
        delta = series.diff()
        up = delta.clip(lower=0)
        down = -delta.clip(upper=0)
        ma_up = up.rolling(window=window, min_periods=1).mean()
        ma_down = down.rolling(window=window, min_periods=1).mean()
        rs = ma_up / (ma_down + 1e-9)
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)
    except Exception as e:
        st.error(f"RSI 계산 오류: {e}")
        return pd.Series(dtype=float)

# 3) MACD
def calc_macd(series: pd.Series,
              fast: int = 12, slow: int = 26, signal: int = 9
             ) -> Tuple[pd.Series, pd.Series, pd.Series]:
    try:
        ema_fast = series.ewm(span=fast, adjust=False).mean()
        ema_slow = series.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    except Exception as e:
        st.error(f"MACD 계산 오류: {e}")
        empty = pd.Series(dtype=float)
        return empty, empty, empty

# 4) 골든/데드 크로스 감지
def detect_golden_dead_cross(ma_short: pd.Series,
                             ma_long: pd.Series
                            ) -> Tuple[bool, bool]:
    try:
        if ma_short.empty or ma_long.empty:
            return False, False
        cross_up = (ma_short > ma_long) & (ma_short.shift(1) <= ma_long.shift(1))
        cross_down = (ma_short < ma_long) & (ma_short.shift(1) >= ma_long.shift(1))
        return bool(cross_up.iloc[-1]), bool(cross_down.iloc[-1])
    except Exception as e:
        st.error(f"크로스 감지 오류: {e}")
        return False, False

# 5) 뉴스 감성 점수 (간단 버전)
def sentiment_score_from_news(news_texts: List[str]) -> float:
    if not news_texts:
        return 0.0
    positive = ['상승', '호재', '강세', '이익', '성장']
    negative = ['하락', '악재', '약세', '손실', '위험']
    score = 0
    for text in news_texts:
        txt = text.lower()
        for w in positive:
            if w in txt: score += 1
        for w in negative:
            if w in txt: score -= 1
    return float(np.tanh(score / len(news_texts)))

# 6) 밸류에이션 점수
def valuation_score(per: float, pbr: float,
                    sector_per: float, sector_pbr: float
                   ) -> float:
    try:
        per_score = 100 * (sector_per / (per + 1e-9))
        pbr_score = 100 * (sector_pbr / (pbr + 1e-9))
        return float(np.clip((per_score + pbr_score) / 2, 0, 100))
    except Exception as e:
        st.error(f"밸류에이션 점수 계산 오류: {e}")
        return 50.0

# 7) 기술 점수 (MA, RSI, MACD 통합)
def technical_score(close: pd.Series) -> float:
    try:
        ma_short = calc_moving_average(close, 20)
        ma_long = calc_moving_average(close, 60)
        golden, dead = detect_golden_dead_cross(ma_short, ma_long)
        rsi_val = calc_rsi(close).iloc[-1] if not calc_rsi(close).empty else 50
        macd_line, sig_line, _ = calc_macd(close)
        macd_diff = macd_line.iloc[-1] - sig_line.iloc[-1] if not macd_line.empty else 0

        score = 50
        score += 20 if golden else 0
        score -= 20 if dead else 0
        score += 10 if rsi_val < 30 else (-10 if rsi_val > 70 else 0)
        score += 10 if macd_diff > 0 else -10
        return float(np.clip(score, 0, 100))
    except Exception as e:
        st.error(f"기술 점수 계산 오류: {e}")
        return 50.0

# 8) 전략 통합 점수
def integrate_strategy_scores(valuation: float, technical: float,
                              sentiment: float,
                              weights: Tuple[float, float, float] = (0.4, 0.4, 0.2)
                             ) -> float:
    try:
        w = np.array(weights, dtype=float)
        if not np.isclose(w.sum(), 1.0):
            w = w / w.sum()
        # sentiment은 -1~1 → 0~100 스케일로 변환
        senti_scaled = (sentiment + 1) / 2 * 100
        total = valuation * w[0] + technical * w[1] + senti_scaled * w[2]
        return float(np.clip(total, 0, 100))
    except Exception as e:
        st.error(f"통합 점수 계산 오류: {e}")
        return 50.0

# 9) 메인 실행 함수
def run(close_prices: pd.Series,
        per: float, pbr: float,
        sector_per: float, sector_pbr: float,
        news_texts: List[str],
        show_details: bool = True
       ) -> Dict[str, Any]:
    st.header("📘 3단원. 통합 전략 판단 시스템")

    # 입력 유효성
    if close_prices is None or close_prices.empty:
        st.warning("종가 데이터가 필요합니다.")
        return {}
    if per is None or pbr is None:
        st.warning("PER, PBR 값을 입력하세요.")
        return {}

    # 1) 점수 계산
    val_score = valuation_score(per, pbr, sector_per, sector_pbr)
    tech_score = technical_score(close_prices)
    senti_score = sentiment_score_from_news(news_texts)

    # 2) UI 출력
    if show_details:
        st.subheader("1) 밸류에이션 점수")    ; st.metric("Valuation", f"{val_score:.1f}/100")
        st.subheader("2) 기술점수")          ; st.metric("Technical", f"{tech_score:.1f}/100")
        st.subheader("3) 심리지수")          ; st.metric("Sentiment", f"{senti_score:.3f} (-1~1)")

    # 3) 통합
    total_score = integrate_strategy_scores(val_score, tech_score, senti_score)
    st.subheader("🔗 종합 전략 점수")       ; st.metric("Total Score", f"{total_score:.1f}/100")

    # 4) 추천 및 시나리오
    recommendation = "진입 추천" if total_score > 60 else "관망/청산 검토"
    scenario = (
        "적극 매수" if total_score > 80 else
        "부분 매수" if total_score > 60 else
        "청산 또는 대기"
    )
    st.write(f"👉 전략 판단: **{recommendation}**")
    st.write(f"▶ 전략 시나리오: {scenario}")

    return {
        "valuation_score": val_score,
        "technical_score": tech_score,
        "sentiment_score": senti_score,
        "total_score": total_score,
        "recommendation": recommendation,
        "scenario": scenario
    }

# 10) 테스트 모드
if __name__ == "__main__":
    st.title("Module 03 테스트")
    # 더미 종가 데이터
    dates = pd.date_range("2023-01-01", periods=100)
    dummy_prices = pd.Series(100 + np.random.randn(100).cumsum(), index=dates)
    dummy_news = [
        "주가가 상승 흐름을 보이고 있습니다.",
        "시장 전반에 호재가 많습니다.",
        "일부 악재도 존재합니다."
    ]
    run(dummy_prices, per=15, pbr=1.2, sector_per=18, sector_pbr=1.5, news_texts=dummy_news)
    
    # module_03.py

import streamlit as st

def run():
    st.subheader("📘 3. 통합 전략 판단 시스템")
    st.markdown("""
    단순 수치가 아닌, 전략 판단을 위한 AI 기반 통합 분석을 실행합니다.

    ### 🔹 3.1 밸류에이션 분석
    - 적정 PER/PBR 추정
    - 업종 평균 대비 고저평가 판단
    - 시가총액 대비 이익/자산 비율 분석

    ### 🔹 3.2 기술적 분석 확장
    - 이동평균선(MA), RSI, MACD, OBV 등 주요 지표 시각화
    - 골든/데드크로스 탐지
    - 다중 신호 기반 최적 전략 조합

    ### 🔹 3.3 심리·이슈 분석
    - 뉴스 키워드 기반 감성 분석
    - 테마 순환 및 군중 관심 변화 감지

    ### 🔹 3.4 전략 통합 스코어링
    - 밸류 × 기술 × 심리 조합 통합 점수 산출
    - "지금 진입 추천" 여부 판단

    ### 🔹 3.5 추가 확장 모듈 (고급)
    - 타이밍 예측 모델
    - 매크로 환경 보정 (금리, 환율, CPI 등)
    - 리스크 정량화: MDD, VaR, CVaR
    - 전략 A/B 비교 및 Trade-off 차트

    ⚙️ 이 판단 시스템은 module_06, module_08 등과 연계되어 실제 백테스트 및 전략 제안에 사용됩니다.
    """)