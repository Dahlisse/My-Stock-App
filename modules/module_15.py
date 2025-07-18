import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity

# ✅ 매크로 데이터 수집 함수
def fetch_macro_data():
    """
    예시용 매크로 데이터를 생성하여 반환.
    실제 배포 시 API 연동 필요 (app.py 또는 secrets.toml 기반).
    """
    try:
        data = {
            'date': pd.date_range(end=datetime.today(), periods=180, freq='D'),
            'interest_rate': np.random.uniform(1.0, 5.0, size=180),
            'cpi': np.random.uniform(1.5, 6.0, size=180),
            'oil_price': np.random.uniform(60, 120, size=180),
            'usd_krw': np.random.uniform(1100, 1400, size=180),
        }
        return pd.DataFrame(data)
    except Exception as e:
        print(f"[fetch_macro_data] 데이터 생성 오류: {e}")
        return pd.DataFrame()

# ✅ 정규화 및 사용자 성향 반영
def score_macro_variables(df, user_profile=None):
    """
    최근 30일의 매크로 변수에 대해 0~1 범위로 정규화하고, 사용자 성향 가중치 반영.
    """
    if df.empty or len(df) < 30:
        raise ValueError("매크로 데이터가 부족하거나 비어 있습니다.")

    recent = df.iloc[-30:].copy()
    scaler = MinMaxScaler()
    normed = scaler.fit_transform(recent[['interest_rate', 'cpi', 'oil_price', 'usd_krw']])
    scores = dict(zip(['interest_rate', 'cpi', 'oil_price', 'usd_krw'], normed[-1]))

    if user_profile:
        if user_profile.get('risk_aversion') == 'high':
            scores['interest_rate'] *= 1.2  # 금리 민감
        if user_profile.get('sensitivity') == 'inflation':
            scores['cpi'] *= 1.3  # 인플레이션 민감
    return scores

# ✅ 매크로 상황 해석
def interpret_macro_conditions(scores):
    """
    금리/인플레이션 조합 기반 시나리오 분기 해석.
    """
    ir = scores.get('interest_rate', 0)
    cpi = scores.get('cpi', 0)

    if ir > 0.7 and cpi > 0.7:
        return "긴축 시나리오", "금리와 인플레이션이 모두 높은 국면 → 가치주 중심 전략 적합"
    elif ir > 0.7 and cpi < 0.4:
        return "제한적 긴축", "금리는 높지만 인플레이션은 안정 → 배당·고정수익 전략 유효"
    elif ir < 0.3 and cpi > 0.6:
        return "인플레이션 위험", "저금리-고CPI → 원자재/리얼에셋 비중 확대 필요"
    else:
        return "중립 또는 혼조", "매크로 변화가 뚜렷하지 않음 → 전략 유지 or 보수적 전환 권장"

# ✅ 과거 유사 국면 탐지
def detect_similar_market(df, current_vector):
    """
    현재 매크로 벡터와 과거 위기 국면의 유사도 비교 (코사인 유사도).
    """
    historical_scenarios = {
        '2008_crisis': [0.9, 0.8, 0.7, 0.6],
        '2011_euro': [0.7, 0.7, 0.6, 0.5],
        '2020_covid': [0.3, 0.9, 0.4, 0.7]
    }
    try:
        similarities = {
            year: cosine_similarity([current_vector], [vec])[0][0]
            for year, vec in historical_scenarios.items()
            if len(vec) == len(current_vector)
        }
        best_match = max(similarities, key=similarities.get)
        return best_match, similarities[best_match]
    except Exception as e:
        print(f"[detect_similar_market] 유사도 계산 오류: {e}")
        return "알 수 없음", 0.0

# ✅ 전략 매핑
def recommend_strategy(scores):
    """
    매크로 점수에 기반하여 전략 추천.
    """
    ir = scores.get('interest_rate', 0)
    cpi = scores.get('cpi', 0)
    oil = scores.get('oil_price', 0)
    fx = scores.get('usd_krw', 0)

    if ir > 0.7 and cpi > 0.7:
        return "가치주 전략", "금리와 CPI가 높아 방어적 가치주 중심 포트가 유리합니다."
    elif cpi > 0.7 and oil > 0.6:
        return "원자재 중심 전략", "원자재 가격과 인플레이션 급등 구간입니다."
    elif fx > 0.8:
        return "수출 중심 전략", "환율 급등기 → 수출주 중심 전략이 유리합니다."
    else:
        return "중립 전략", "공격/수비 전략을 명확히 구분하기 어려운 상황입니다."

# ✅ 통합 매크로 분석 파이프라인
def macro_analysis_pipeline(user_profile=None):
    """
    전체 매크로 분석 과정 자동화 파이프라인.
    """
    df = fetch_macro_data()
    if df.empty:
        return {
            'macro_scores': {},
            'scenario': "데이터 없음",
            'scenario_explanation': "매크로 데이터를 수집할 수 없습니다.",
            'similar_past': "없음",
            'similarity_score': 0.0,
            'recommended_strategy': "중립",
            'strategy_explanation': "데이터 오류로 인해 분석이 제한됩니다."
        }

    scores = score_macro_variables(df, user_profile)
    scenario_name, scenario_explanation = interpret_macro_conditions(scores)
    current_vector = list(scores.values())
    match_name, match_score = detect_similar_market(df, current_vector)
    strategy, strategy_comment = recommend_strategy(scores)

    return {
        'macro_scores': scores,
        'scenario': scenario_name,
        'scenario_explanation': scenario_explanation,
        'similar_past': match_name,
        'similarity_score': round(match_score, 3),
        'recommended_strategy': strategy,
        'strategy_explanation': strategy_comment
    }
    
import streamlit as st

def run():
    st.subheader("📘 15. 매크로 필터링 & 외부 환경 반영")
    st.markdown("“전략은 시장 밖에서도 영향을 받는다.”")

    st.markdown("### ✅ 15.1 주요 매크로 지표 요약")
    st.markdown("""
    - 기준금리: **3.5%** (최근 2개월 정체)
    - 물가상승률: **2.9%** (완만한 하락세)
    - 원/달러 환율: **1,330원** (달러 강세 흐름)
    - 유가(WTI): **$82.5** (단기 급등)
    """)

    st.markdown("### ✅ 15.2 매크로 조건에 따른 전략 적합도")
    st.markdown("""
    - 현재는 **금리 고점 + 유가 급등** 조합 → **가치주 / 에너지 업종 중심 전략** 우선
    - 기술주 / 성장형 전략 적합도 하락 (할인율 영향)
    """)

    st.markdown("### ✅ 15.3 전략 필터링 시뮬레이션")
    selected_strategy = st.selectbox("📈 전략 유형 선택", ["가치형", "성장형", "모멘텀형", "안정형"])
    if st.button("🔍 매크로 기반 적합도 분석"):
        if selected_strategy == "가치형":
            st.success("적합도: **높음** (금리+유가 조건과 일치)")
        elif selected_strategy == "성장형":
            st.warning("적합도: **낮음** (할인율 상승 영향)")
        elif selected_strategy == "모멘텀형":
            st.info("적합도: **중간** (단기 유동성 영향 관찰)")
        elif selected_strategy == "안정형":
            st.info("적합도: **중간~높음** (리스크 회피 심리 반영)")

    st.markdown("### ✅ 15.4 전략 자동 조정 가이드")
    st.markdown("""
    - 매크로 급변 감지 시:
        - 전략 리밸런싱 우선순위 변경
        - AI 포트 구성 알고리즘에 외부 환경 변수 자동 반영
    - 예: **'모멘텀 → 가치주 중심' 전환 제안**
    """)

    st.markdown("📎 이 기능은 module_06 전략 전환 / module_08 포트 구성 / module_24 사용자 심리와 연계됩니다.")