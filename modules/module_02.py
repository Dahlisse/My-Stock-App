import streamlit as st
import pandas as pd
import numpy as np

# ⬛ CAGR 계산
def calc_cagr(series):
    try:
        start_value = series.iloc[0]
        end_value = series.iloc[-1]
        periods = len(series) - 1
        if start_value <= 0 or periods <= 0:
            return None
        return (end_value / start_value) ** (1 / periods) - 1
    except:
        return None

# ⬛ Altman Z-Score 계산 (간이 버전)
def altman_z_score(financials):
    try:
        working_capital = financials.get('Current Assets', 0) - financials.get('Current Liabilities', 0)
        retained_earnings = financials.get('Retained Earnings', 0)
        ebit = financials.get('EBIT', 0)
        market_value_equity = financials.get('Market Cap', 0)
        total_liabilities = financials.get('Total Liabilities', 0)
        total_assets = financials.get('Total Assets', 1)
        sales = financials.get('Total Revenue', 0)

        if total_assets == 0 or total_liabilities == 0:
            return None

        z_score = (
            1.2 * (working_capital / total_assets) +
            1.4 * (retained_earnings / total_assets) +
            3.3 * (ebit / total_assets) +
            0.6 * (market_value_equity / total_liabilities) +
            1.0 * (sales / total_assets)
        )
        return round(z_score, 2)
    except:
        return None

# ⬛ 성장성 & 안정성 점수 계산
def score_growth_stability(financial_data):
    try:
        revenue = financial_data.get('Revenue', pd.Series(dtype=float))
        debt_ratio = financial_data.get('Debt Ratio', None)

        cagr = calc_cagr(revenue) if isinstance(revenue, pd.Series) and not revenue.empty else None
        stability = 1 - debt_ratio if debt_ratio is not None else 0

        growth_score = min(max(cagr * 100, 0), 100) if cagr is not None else 0
        stability_score = min(max(stability * 100, 0), 100)

        return growth_score, stability_score, cagr, debt_ratio
    except:
        return 0, 0, None, None

# ⬛ 퍼센타일 계산
def percentile_rank(series, target_value):
    try:
        return (series < target_value).mean() * 100
    except:
        return None

# ⬛ 전체 종목 대비 상대점수 계산
def calculate_scores(target, industry_df):
    try:
        scores = {}
        features = ['PER', 'PBR', 'ROE', 'EPS', 'FCF']
        for feature in features:
            value = target.get(feature)
            if value is not None and not pd.isna(value):
                series = industry_df[feature].dropna()
                scores[f"{feature}_percentile"] = percentile_rank(series, value)
        return scores
    except:
        return {}

# ⬛ 종합 설명 생성
def generate_summaries(cagr, debt_ratio, percentile_features, per, roe, warnings):
    try:
        cagr_text = f"{cagr * 100:.2f}%" if cagr is not None else "정보 없음"
        debt_text = f"{debt_ratio:.2f}" if debt_ratio is not None else "정보 없음"
        per_pct = f"{percentile_features.get('PER_percentile', 0):.1f}%" if 'PER_percentile' in percentile_features else "정보 없음"

        beginner = (
            f"이 기업은 최근 3년간 평균 {cagr_text}의 매출 성장률을 기록했으며, "
            f"부채비율은 {debt_text}로 안정성은 {'양호' if debt_ratio is not None and debt_ratio < 0.6 else '주의 필요'}합니다."
        )
        expert = (
            f"PER는 {per}, ROE는 {roe}이며, 업종 내 PER percentile은 {per_pct}입니다. "
            f"주요 리스크로는 {', '.join(warnings) if warnings else '특별한 이상징후 없음'}가 있습니다."
        )
        return beginner, expert
    except:
        return "정보 부족", "정보 부족"

# ⬛ 메인 실행 함수
def run():
    st.header("📊 2단원: 재무 실적 분석")

    # ⬛ 샘플 데이터 입력
    st.subheader("🔢 종목 데이터 입력")
    target_data = {
        "Revenue": pd.Series([100, 120, 150, 180]),
        "Debt Ratio": 0.45,
        "PER": 15.2,
        "PBR": 1.8,
        "ROE": 12.5,
        "EPS": 3200,
        "FCF": 5000,
        "PEG": 1.2
    }

    industry_data = pd.DataFrame({
        "PER": np.random.normal(18, 5, 100),
        "PBR": np.random.normal(2, 0.5, 100),
        "ROE": np.random.normal(10, 3, 100),
        "EPS": np.random.normal(3000, 500, 100),
        "FCF": np.random.normal(4000, 1000, 100)
    })

    # ⬛ 분석 실행
    growth_score, stability_score, cagr, debt_ratio = score_growth_stability(target_data)
    percentile_scores = calculate_scores(target_data, industry_data)
    z_score = altman_z_score({
        "Current Assets": 5000,
        "Current Liabilities": 3000,
        "Retained Earnings": 2000,
        "EBIT": 1500,
        "Market Cap": 8000,
        "Total Liabilities": 7000,
        "Total Assets": 10000,
        "Total Revenue": 12000,
    })

    # ⬛ 이상징후 감지
    warnings = []
    if target_data["PER"] > 30:
        warnings.append("PER 과대평가 가능성")
    if debt_ratio and debt_ratio > 0.8:
        warnings.append("부채비율 과다")
    if z_score and z_score < 1.8:
        warnings.append("재무위험 경고 (Z-score < 1.8)")

    # ⬛ 설명 생성
    beginner_txt, expert_txt = generate_summaries(
        cagr, debt_ratio, percentile_scores,
        target_data["PER"], target_data["ROE"], warnings
    )

    # ⬛ 출력
    st.success("✅ 재무 분석 요약")
    st.markdown(f"**📌 성장성 점수:** {growth_score:.1f} / 100")
    st.markdown(f"**📌 안정성 점수:** {stability_score:.1f} / 100")
    st.markdown(f"**📌 Altman Z-Score:** {z_score if z_score is not None else '계산 불가'}")
    st.markdown("---")
    st.info(f"👶 **초보자 해설:** {beginner_txt}")
    st.info(f"🧠 **전문가 해설:** {expert_txt}")