# module_02.py
import streamlit as st
import pandas as pd
import numpy as np

def calc_cagr(series):
    """
    3년 CAGR (연복리 성장률) 계산
    series: pd.Series (기간순 매출 등)
    """
    try:
        if len(series) < 4:
            return None
        start = series.iloc[0]
        end = series.iloc[-1]
        periods = len(series) - 1
        if start <= 0 or end <= 0:
            return None
        cagr = (end / start) ** (1 / periods) - 1
        return cagr
    except:
        return None

def altman_z_score(financials):
    """
    Altman Z-Score 계산
    financials: dict with keys:
      working_capital, total_assets, retained_earnings, ebit,
      market_value_equity, total_liabilities, sales
    """
    try:
        WC = financials["working_capital"]
        TA = financials["total_assets"]
        RE = financials["retained_earnings"]
        EBIT = financials["ebit"]
        MVE = financials["market_value_equity"]
        TL = financials["total_liabilities"]
        S = financials["sales"]

        z = 1.2 * (WC / TA) + 1.4 * (RE / TA) + 3.3 * (EBIT / TA) + 0.6 * (MVE / TL) + 1.0 * (S / TA)
        return z
    except:
        return None

def percentile_rank(series):
    """
    Percentile 계산 (0~100)
    """
    return series.rank(pct=True).iloc[-1] * 100

def score_growth_stability(sales_series):
    """
    성장 지속성 지수 (매출 QoQ 성장률 변동성 낮을수록 안정적)
    """
    try:
        growth_rates = sales_series.pct_change().dropna()
        mean_growth = growth_rates.mean()
        std_growth = growth_rates.std()
        stability_score = mean_growth / (std_growth + 1e-6)
        return stability_score
    except:
        return None

def calculate_scores(financial_data: pd.DataFrame, market_metrics: dict, sector_metrics: pd.DataFrame):
    """
    재무 스코어 및 이상징후 계산
    financial_data: 재무제표 DataFrame, index = 재무 항목, columns = 기간(연도/분기)
    market_metrics: dict, PER, PBR, ROE, 부채비율, 유동비율 등
    sector_metrics: pd.DataFrame, 업종 내 종목 지표 (퍼센타일 산출용)
    """
    # 핵심 지표
    per = market_metrics.get('PER')
    pbr = market_metrics.get('PBR')
    roe = market_metrics.get('ROE')
    debt_ratio = market_metrics.get('debt_ratio')
    current_ratio = market_metrics.get('current_ratio')

    # 매출
    sales = financial_data.loc['Total Revenue'] if 'Total Revenue' in financial_data.index else None

    # 이익률 변화
    operating_income = financial_data.loc['Operating Income'] if 'Operating Income' in financial_data.index else None
    operating_margin_change = None
    if operating_income is not None and sales is not None:
        try:
            operating_margin = operating_income / sales
            operating_margin_change = operating_margin.iloc[-1] - operating_margin.iloc[-2]
        except:
            operating_margin_change = None

    # 성장성
    cagr = calc_cagr(sales) if sales is not None else None
    stability_score = score_growth_stability(sales) if sales is not None else None

    # 안정성 스코어: 부채비율 낮고 유동비율 높을수록 좋음 (0~100)
    debt_score = 100 - (debt_ratio * 100 if debt_ratio is not None else 50)
    current_score = current_ratio * 100 if current_ratio is not None else 50
    stability_composite = np.mean([debt_score, current_score])

    # PEG Ratio (PER / CAGR)
    peg_ratio = None
    if per and cagr and cagr > 0:
        peg_ratio = per / (cagr * 100)  # CAGR %로 변환

    # 이상징후 감지
    warnings = []
    if cagr is not None and cagr < 0.01:
        warnings.append("성장 급감")
    if debt_ratio is not None and debt_ratio > 0.6:
        warnings.append("부채 급증")
    # 이익 vs 현금흐름 괴리 (가정: 순이익 vs FCF 존재)
    if 'Net Income' in financial_data.index and 'Free Cash Flow' in financial_data.index:
        net_income = financial_data.loc['Net Income']
        fcf = financial_data.loc['Free Cash Flow']
        gap = np.mean(np.abs(net_income - fcf) / (np.abs(net_income) + 1e-6))
        if gap > 0.3:
            warnings.append("현금창출성 악화")

    # 업종 대비 Percentile (예: PER, ROE, 매출성장률)
    percentile_features = {}
    try:
        for col in ['PER', 'ROE', 'CAGR']:
            if col == 'PER' and per is not None:
                percentile_features['PER_percentile'] = percentile_rank(sector_metrics['PER'])
            elif col == 'ROE' and roe is not None:
                percentile_features['ROE_percentile'] = percentile_rank(sector_metrics['ROE'])
            elif col == 'CAGR' and cagr is not None:
                percentile_features['CAGR_percentile'] = percentile_rank(sector_metrics['CAGR'])
    except:
        pass

    # AI 종합 스코어 (단순 평균 기반 0~100)
    scores_to_average = [stability_composite]
    if cagr is not None:
        scores_to_average.append(min(max(cagr * 100, 0), 100))
    ai_score = np.mean(scores_to_average) if scores_to_average else None

    # 사용자 설명문 생성
    beginner_text = f"이 기업은 최근 3년간 평균 {cagr * 100:.2f}%의 매출 성장률을 기록했으며, 부채비율은 {debt_ratio:.2f}로 안정성은 {'양호' if debt_ratio < 0.6 else '주의 필요'}합니다."
    expert_text = f"PER는 {per}, ROE는 {roe}이며, 업종 내 PER percentile은 {percentile_features.get('PER_percentile', 'N/A'):.1f}%입니다. 주요 리스크로는 {', '.join(warnings) if warnings else '특별한 이상징후 없음'}가 있습니다."

    return {
        "PER": per,
        "PBR": pbr,
        "ROE": roe,
        "DebtRatio": debt_ratio,
        "CurrentRatio": current_ratio,
        "CAGR": cagr,
        "GrowthStability": stability_score,
        "OperatingMarginChange": operating_margin_change,
        "PEGRatio": peg_ratio,
        "Warnings": warnings,
        "PercentileFeatures": percentile_features,
        "AIScore": ai_score,
        "BeginnerSummary": beginner_text,
        "ExpertSummary": expert_text
    }

def module_02_ui(financial_data, market_metrics, sector_metrics):
    st.header("📘 2단원. 재무 실적 분석")
    results = calculate_scores(financial_data, market_metrics, sector_metrics)

    st.subheader("핵심 재무 지표")
    st.write({
        "PER": results["PER"],
        "PBR": results["PBR"],
        "ROE": results["ROE"],
        "부채비율": results["DebtRatio"],
        "유동비율": results["CurrentRatio"],
        "3년 CAGR": results["CAGR"],
        "PEG Ratio": results["PEGRatio"]
    })

    st.subheader("성장성 및 안정성")
    st.write(f"성장 지속성 지수: {results['GrowthStability']:.3f}" if results['GrowthStability'] else "정보 없음")
    st.write(f"영업이익률 증감: {results['OperatingMarginChange']:.3f}" if results['OperatingMarginChange'] else "정보 없음")

    st.subheader("업종 대비 Percentile")
    st.write(results["PercentileFeatures"])

    st.subheader("이상징후 및 경고")
    if results["Warnings"]:
        for w in results["Warnings"]:
            st.warning(w)
    else:
        st.success("이상징후 없음")

    st.subheader("종합 AI 판단 점수")
    st.write(f"{results['AIScore']:.2f}" if results['AIScore'] else "정보 없음")

    st.subheader("초보자용 해석")
    st.write(results["BeginnerSummary"])

    st.subheader("전문가용 해석")
    st.write(results["ExpertSummary"])

    return results

if __name__ == "__main__":
    st.title("Module 02 재무 실적 분석 테스트")

    # 테스트용 더미 데이터 생성 예시 (실제 사용 시 데이터 소스로 대체)
    idx = ['Total Revenue', 'Operating Income', 'Net Income', 'Free Cash Flow']
    cols = ['2019', '2020', '2021', '2022']
    data = [
        [1000, 1100, 1300, 1500],
        [100, 150, 180, 200],
        [80, 120, 160, 190],
        [70, 100, 140, 170]
    ]
    financial_data = pd.DataFrame(data, index=idx, columns=cols).astype(float)

    market_metrics = {
        "PER": 15,
        "PBR": 1.5,
        "ROE": 12,
        "debt_ratio": 0.35,
        "current_ratio": 1.8
    }

    sector_metrics = pd.DataFrame({
        "PER": [10, 15, 20, 25],
        "ROE": [8, 10, 12, 14],
        "CAGR": [0.05, 0.10, 0.12, 0.15]
    })

    module_02_ui(financial_data, 
market_metrics, sector_metrics)