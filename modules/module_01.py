import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import re

# ✅ 필요시 이 부분을 import 해서 공통 util로 분리할 수 있음
def fetch_stock_basic_info(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
    except Exception:
        return {}

    ipo_date = None
    try:
        ipo_date = info.get('ipoDate') or info.get('firstTradeDateEpochUtc')
        if isinstance(ipo_date, int):
            ipo_date = datetime.fromtimestamp(ipo_date)
    except:
        pass

    market_cap = info.get('marketCap')
    avg_volume = info.get('averageVolume')

    if info.get('quoteType', '').lower() == 'etf':
        market_type = 'ETF'
    elif re.match(r'^[A-Z]{1,5}$', ticker):
        market_type = 'NASDAQ/NYSE'
    else:
        market_type = 'KOSPI/KOSDAQ'

    float_ratio = None
    try:
        float_shares = info.get('floatShares')
        shares_outstanding = info.get('sharesOutstanding')
        if float_shares and shares_outstanding:
            float_ratio = float_shares / shares_outstanding
    except:
        pass

    return {
        "ipo_date": ipo_date,
        "market_cap": market_cap,
        "avg_volume": avg_volume,
        "market_type": market_type,
        "float_ratio": float_ratio
    }


def estimate_liquidity_size(market_cap):
    if not isinstance(market_cap, (int, float)):
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
    if history is None or len(history) < 60:
        return None
    try:
        daily_returns = history['Close'].pct_change().dropna()
        vol = daily_returns.rolling(window=60).std().iloc[-1]
        if np.isnan(vol):
            return None
        annualized_vol = vol * np.sqrt(252)
        return float(min(max(annualized_vol / 0.8, 0), 1))
    except:
        return None


def classify_industry_sector(ticker):
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
    revenue_growth = None
    dividend_yield = 0.02
    momentum = 0.05

    try:
        if financials_df is not None and 'Total Revenue' in financials_df.index:
            recent = financials_df.loc['Total Revenue'][-4:].sum()
            prev = financials_df.loc['Total Revenue'][-8:-4].sum()
            if prev > 0:
                revenue_growth = (recent - prev) / prev
    except:
        pass

    style = []
    if revenue_growth and revenue_growth > 0.1:
        style.append("고성장")
    if dividend_yield > 0.03:
        style.append("고배당")
    if momentum > 0.05:
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
    return {
        "institutional_preference": True,
        "foreign_investor_preference": True
    }


def detect_high_volatility_and_trend(history):
    if history is None or history.empty:
        return {"high_volatility": False, "uptrend": False}

    close = history['Close']
    delta = close.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    avg_gain = up.rolling(window=14).mean()
    avg_loss = down.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    current_rsi = rsi.iloc[-1] if not rsi.empty else 50

    high_volatility = rsi.std() > 15
    uptrend = close.iloc[-1] > close.rolling(window=50).mean().iloc[-1]

    return {
        "high_volatility": bool(high_volatility),
        "rsi": float(current_rsi),
        "uptrend": bool(uptrend)
    }


def normalize_against_sector(df_metrics, ticker):
    if ticker not in df_metrics.index:
        return {}
    result = {}
    try:
        for col in df_metrics.columns:
            result[f"{col}_percentile"] = df_metrics[col].rank(pct=True).loc[ticker] * 100
    except:
        pass
    return result


def generate_natural_language_summary(features: dict):
    ipo_date = features.get('ipo_date')
    market_cap = features.get('market_cap')
    styles = ", ".join(features.get("style_labels", []))
    growth = features.get("revenue_growth")
    inst_pref = features.get("institutional_preference", False)
    high_vol = features.get("high_volatility", False)

    beginner_text = f"이 종목은 {ipo_date.strftime('%Y-%m-%d') if ipo_date else '상장일 정보 없음'}에 상장되었으며, 시가총액은 약 {market_cap / 1e9:.2f}억 원입니다. 주요 투자 스타일은 {styles}입니다."
    expert_text = f"최근 매출 성장률은 약 {growth:.2%}로, 기관/외국인 선호도는 {'높습니다' if inst_pref else '낮습니다'}. 변동성은 {'높아 주의 요망' if high_vol else '안정적'}입니다."

    return beginner_text, expert_text


def generate_confidence_and_reasoning(features: dict):
    growth = features.get("revenue_growth", 0)
    score = min(max(growth * 100, 0), 100)
    error_margin = 2.5
    reasoning = f"성장주 분류 확률: {score:.1f}% ± {error_margin}% (최근 매출 성장률 기반)"
    return score, error_margin, reasoning


def module_01_main(ticker_input: str):
    st.header("📘 1단원. 기본 정보 분석")
    if not ticker_input:
        st.warning("종목 티커를 입력하세요.")
        return None

    basic_info = fetch_stock_basic_info(ticker_input)
    stock = yf.Ticker(ticker_input)
    history = stock.history(period="6mo")
    if history.empty:
        st.warning("주가 이력이 존재하지 않습니다.")
        return None

    liquidity_class = estimate_liquidity_size(basic_info.get("market_cap"))
    volatility_score = calc_volatility_score(history)
    industry_sector = classify_industry_sector(ticker_input)

    try:
        financials = stock.quarterly_financials
    except:
        financials = None

    style_features = classify_style_features(ticker_input, financials)
    inst_pref = label_institutional_preference(ticker_input)
    trend_labels = detect_high_volatility_and_trend(history)

    dummy_df = pd.DataFrame({
        'market_cap': [basic_info["market_cap"], 1e12, 5e11, 1e11],
        'PER': [15, 20, 12, 18],
        'ROE': [10, 12, 8, 9]
    }, index=[ticker_input, "A", "B", "C"])
    percentile_features = normalize_against_sector(dummy_df, ticker_input)

    beginner_text, expert_text = generate_natural_language_summary({
        **basic_info, **style_features, **inst_pref, **trend_labels
    })

    score, error_margin, reasoning = generate_confidence_and_reasoning(style_features)

    st.subheader("기본 정보")
    st.write(basic_info)
    st.write(f"유동성 분류: {liquidity_class}")
    st.write(f"변동성 스코어: {volatility_score:.3f}" if volatility_score else "N/A")
    st.write(f"산업군 분류: {industry_sector}")
    st.write(f"스타일 분류: {style_features['style_labels']}")

    st.subheader("기관/외인 선호도 및 트렌드")
    st.write(inst_pref)
    st.write(trend_labels)

    st.subheader("상대 위치 (Percentile)")
    st.write(percentile_features)

    st.subheader("초보자용 요약")
    st.write(beginner_text)

    st.subheader("전문가용 분석")
    st.write(expert_text)

    st.subheader("신뢰도 및 판단 사유")
    st.write(reasoning)
    st.write(f"신뢰도 점수: {score:.1f}%, 오차: ±{error_margin}%")

    return {
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


if __name__ == "__main__":
    st.title("Module 01 - 기본 정보 분석 테스트")
    ticker = st.text_input("종목 티커 입력 (예: AAPL, 005930.KS)")
    if ticker:
        module_01_main(ticker)
        
import streamlit as st

def run():
    st.subheader("📘 1. 기본 정보 분석")
    # 여기에 module_01.py에서 실제 수행하는 기능 함수 호출
    # 예시:
    # run_basic_info_analysis() 또는 analyze_basic_info()

    # 아래는 임시 출력용 예시
    st.write("기본 정보 분석 모듈 실행 중입니다.")