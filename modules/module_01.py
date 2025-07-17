# module_01.py
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler
import re

def fetch_stock_basic_info(ticker: str):
    """
    yfinance를 활용하여 기본 정보 수집
    - 상장일, 시가총액, 거래량 등
    - 시장 구분 (KOSPI, KOSDAQ, NASDAQ, ETF 등)
    """
    stock = yf.Ticker(ticker)
    info = stock.info

    # 상장일
    try:
        ipo_date = info.get('ipoDate', None) or info.get('firstTradeDateEpochUtc', None)
        if ipo_date:
            ipo_date = datetime.fromtimestamp(int(ipo_date))
        else:
            ipo_date = None
    except:
        ipo_date = None

    # 시가총액, 거래량
    market_cap = info.get('marketCap', None)
    avg_volume = info.get('averageVolume', None)

    # 시장 분류: 대략 티커 규칙 활용
    if info.get('quoteType', '').lower() == 'etf':
        market_type = 'ETF'
    else:
        if re.match(r'^[A-Z]{1,5}$', ticker):
            # 미국시장 NASDAQ/NYSE 추정 (단순 예시)
            market_type = 'NASDAQ/NYSE'
        else:
            # 한국시장 분류(예: KOSPI, KOSDAQ)
            market_type = 'KOSPI/KOSDAQ'

    # 유통주식비율 등 (추가 데이터 필요시 확장)
    float_shares = info.get('floatShares', None)
    shares_outstanding = info.get('sharesOutstanding', None)
    float_ratio = None
    if float_shares and shares_outstanding:
        float_ratio = float_shares / shares_outstanding

    return {
        "ipo_date": ipo_date,
        "market_cap": market_cap,
        "avg_volume": avg_volume,
        "market_type": market_type,
        "float_ratio": float_ratio
    }

def estimate_liquidity_size(market_cap):
    """
    시가총액 기준 대형/중형/소형 분류
    (기준은 임의 설정: 대형>10조, 중형 1조~10조, 소형 <1조)
    """
    if market_cap is None:
        return "정보 없음"
    try:
        if market_cap >= 10_000_000_000_000:
            return "초대형"
        elif market_cap >= 1_000_000_000_000:
            return "대형"
        elif market_cap >= 200_000_000_000:
            return "중형"
        else:
            return "소형"
    except:
        return "정보 없음"

def calc_volatility_score(history):
    """
    변동성 스코어 예시: 3개월 일간 수익률 표준편차 기준 (연율화)
    """
    if history is None or len(history) < 60:
        return None
    daily_returns = history['Close'].pct_change().dropna()
    vol = daily_returns.rolling(window=60).std().iloc[-1]  # 3개월 approx 60거래일
    if vol is None or np.isnan(vol):
        return None
    annualized_vol = vol * np.sqrt(252)
    # MinMax 스케일링 예시 (0~1)
    return float(min(max(annualized_vol / 0.8, 0), 1))  # 0.8은 임의 최대 변동성 값

def classify_industry_sector(ticker):
    """
    NAICS 기반 고해상도 산업군 분류 모의 함수 (실제 API, DB 연동 필요)
    예시로 임의 매핑 사용
    """
    sector_map = {
        "AAPL": "정보기술>컴퓨터하드웨어",
        "TSLA": "자동차>전기차",
        "005930.KS": "반도체>메모리반도체",
        "000660.KS": "반도체>시스템반도체",
        "005380.KS": "자동차>내연기관차",
        "068270.KQ": "바이오>신약개발",
    }
    return sector_map.get(ticker, "기타>기타산업")

def classify_style_features(ticker, financials_df):
    """
    성장/가치/배당/모멘텀/테마 성향 AI 분류(예시)
    - 최근 1년 매출증가율, 배당수익률, 모멘텀 지표 등 사용
    - 실제 AI 모델 또는 규칙 기반 처리 가능
    """
    # 임의 값 예시
    revenue_growth = None
    dividend_yield = None
    momentum = None

    if financials_df is not None and not financials_df.empty:
        try:
            # 매출증가율 (최근 4분기 합계 비교)
            recent_revenue = financials_df.loc['Total Revenue'][-4:].sum()
            prev_revenue = financials_df.loc['Total Revenue'][-8:-4].sum()
            if prev_revenue and prev_revenue > 0:
                revenue_growth = (recent_revenue - prev_revenue) / prev_revenue
        except:
            revenue_growth = None

    # 임의 모멘텀 및 배당 수익률 설정 (실제 데이터 필요)
    dividend_yield = 0.02  # 2%
    momentum = 0.05  # 5% 3개월 수익률

    style = []
    if revenue_growth and revenue_growth > 0.1:
        style.append("고성장")
    if dividend_yield and dividend_yield > 0.03:
        style.append("고배당")
    if momentum and momentum > 0.05:
        style.append("모멘텀강세")
    if not style:
        style.append("가치주")

    return {
        "revenue_growth": revenue_growth,
        "dividend_yield": dividend_yield,
        "momentum": momentum,
        "style_labels": style
    }

def label_institutional_preference(ticker):
    """
    기관/외국인 선호도 판단 (예: 순매수 지속성 + 보유비중 증가율 기반)
    - 실제는 거래 데이터 기반 AI 분석 필요
    - 임의 예시로 True/False 반환
    """
    # 실제 분석 미구현, 임의 True
    return {
        "institutional_preference": True,
        "foreign_investor_preference": True
    }

def detect_high_volatility_and_trend(history):
    """
    고변동성/이슈주/상승추세 감지 예시
    - 3개월 기술지표 (RSI, 이동평균 등) 기반
    """
    # 간단 RSI 14일 계산 예시
    if history is None or history.empty:
        return {"high_volatility": False, "uptrend": False}

    close = history['Close']
    delta = close.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    avg_gain = up.rolling(window=14).mean()
    avg_loss = down.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    current_rsi = rsi.iloc[-1] if len(rsi) > 0 else 50

    high_volatility = rsi.std() > 15
    uptrend = (close.iloc[-1] > close.rolling(window=50).mean().iloc[-1])

    return {
        "high_volatility": bool(high_volatility),
        "rsi": float(current_rsi),
        "uptrend": bool(uptrend)
    }

def percentile_rank(series):
    """
    상대 Percentile 계산 (0~100)
    """
    return series.rank(pct=True).iloc[-1] * 100

def normalize_against_sector(df_metrics, ticker):
    """
    업종 내 상대 위치 계산 (시총, PER, ROE 등 Percentile)
    - df_metrics: DataFrame(종목별 지표), index=ticker
    """
    if ticker not in df_metrics.index:
        return {}

    result = {}
    try:
        for col in df_metrics.columns:
            result[f"{col}_percentile"] = percentile_rank(df_metrics[col])
    except:
        pass
    return result

def generate_natural_language_summary(features: dict):
    """
    ChatGPT 스타일 자연어 요약 생성 예시
    - 초보자용 + 전문가용 병렬 생성
    """
    ipo_date = features.get('ipo_date')
    market_cap = features.get('market_cap')
    styles = ", ".join(features.get("style_labels", []))
    growth = features.get("revenue_growth", None)
    inst_pref = features.get("institutional_preference", False)
    high_vol = features.get("high_volatility", False)

    beginner_text = f"이 종목은 {ipo_date.strftime('%Y-%m-%d') if ipo_date else '상장일 정보 없음'}에 상장되었으며, 현재 시가총액은 약 {market_cap / 1e9:.2f}억 원입니다. 주요 투자 스타일은 {styles}입니다."

    expert_text = f"최근 3년간 CAGR은 약 {growth:.2%}로 평가되며, 기관 및 외국인 투자자 선호도가 {'높습니다' if inst_pref else '낮습니다'}. 변동성은 {'높아 주의가 필요합니다' if high_vol else '안정적인 편입니다'}."

    return beginner_text, expert_text

def generate_confidence_and_reasoning(features: dict):
    """
    판단 사유, 신뢰도, 오차범위 수치화 예시
    """
    growth = features.get("revenue_growth", 0)
    score = min(max(growth * 100, 0), 100)
    error_margin = 2.5  # 예시

    reasoning = f"성장주로 분류된 확률: {score:.1f}% ± {error_margin}% (최근 3년 매출 성장률 기반)"

    return score, error_margin, reasoning

def module_01_main(ticker_input: str):
    """
    1단원 전체 통합 함수 - streamlit UI 포함
    """
    st.header("📘 1단원. 기본 정보 분석")

    if not ticker_input:
        st.warning("종목 티커를 입력하세요.")
        return None

    # 1. 종목 정보 수집
    basic_info = fetch_stock_basic_info(ticker_input)

    # 2. 주가 이력 조회 (6개월 이상)
    stock = yf.Ticker(ticker_input)
    history = stock.history(period="6mo")
    if history.empty:
        st.warning("주가 데이터가 없습니다.")
        return None

    # 3. 유동성 스코어 및 분류
    liquidity_class = estimate_liquidity_size(basic_info["market_cap"])
    volatility_score = calc_volatility_score(history)

    # 4. 산업군 분류
    industry_sector = classify_industry_sector(ticker_input)

    # 5. 스타일 분류
    financials = None
    try:
        financials = stock.quarterly_financials
    except:
        financials = None

    style_features = classify_style_features(ticker_input, financials)

    # 6. 기관/외인 선호도
    inst_pref = label_institutional_preference(ticker_input)

    # 7. 변동성 및 상승추세 감지
    trend_labels = detect_high_volatility_and_trend(history)

    # 8. 상대 위치 (Percentile) - 임의 더미 데이터 예시, 실제 DB 필요
    dummy_df = pd.DataFrame({
        'market_cap': [basic_info["market_cap"], 1e12, 5e11, 1e11],
        'PER': [15, 20, 12, 18],
        'ROE': [10, 12, 8, 9]
    }, index=[ticker_input, "A", "B", "C"])
    percentile_features = normalize_against_sector(dummy_df, ticker_input)

    # 9. 자연어 요약
    beginner_text, expert_text = generate_natural_language_summary({**basic_info, **style_features, **inst_pref, **trend_labels})

    # 10. 판단 사유 및 신뢰도
    score, error_margin, reasoning = generate_confidence_and_reasoning(style_features)

    # UI 출력
    st.subheader("기본 정보")
    st.write(basic_info)
    st.write(f"유동성 분류: {liquidity_class}")
    st.write(f"변동성 스코어: {volatility_score:.3f}" if volatility_score else "변동성 스코어 정보 없음")
    st.write(f"산업군 분류: {industry_sector}")
    st.write(f"스타일 분류: {style_features['style_labels']}")

    st.subheader("기관/외국인 선호도 및 변동성")
    st.write(inst_pref)
    st.write(trend_labels)

    st.subheader("상대 위치 (Percentile)")
    st.write(percentile_features)

    st.subheader("초보자용 요약")
    st.write(beginner_text)

    st.subheader("전문가용 분석")
    st.write(expert_text)

    st.subheader("판단 신뢰도 및 사유")
    st.write(reasoning)
    st.write(f"신뢰도 점수: {score:.1f}%, 오차범위: ±{error_margin}%")

    # 결과 딕셔너리 리턴 (연계용)
    feature_vector = {
        **basic_info,
        **style_features,
        **inst_pref,
        **trend_labels,
        **percentile_features,
        "confidence_score": score,
        "confidence_error": error_margin,
        "reasoning": reasoning,
        "liquidity_class": liquidity_class,
        "volatility_score": volatility_score,
        "industry_sector": industry_sector
    }
    return feature_vector


if __name__ == "__main__":
    st.title("Module 01 기본 정보 분석 테스트")
    ticker = st.text_input("종목 티커 입력 (예: AAPL, 005930.KS)")
    if ticker:
        module_01_main(ticker)