import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
from ruptures import Binseg
from typing import Dict, List, Optional


# 16.1 상승/보합/하락 시나리오 확률 추정
def estimate_market_scenarios(market_factors: Dict[str, float]) -> Dict[str, float]:
    factors = np.array(list(market_factors.values()))
    scaler = MinMaxScaler()
    norm = scaler.fit_transform(factors.reshape(1, -1))[0]

    # 예시 가중치 기반 시나리오 확률 계산
    prob_up = norm[0] * 0.5 + (1 - norm[1]) * 0.3 + norm[2] * 0.2
    prob_flat = (1 - abs(norm[0] - 0.5)) * 0.6
    prob_down = 1.0 - prob_up - prob_flat

    # 오류 방지를 위한 보정
    prob_up = max(0, min(1, prob_up))
    prob_flat = max(0, min(1, 1 - prob_up - max(0, prob_down)))
    prob_down = max(0, min(1, 1 - prob_up - prob_flat))

    return {
        'up': round(prob_up, 3),
        'flat': round(prob_flat, 3),
        'down': round(prob_down, 3)
    }


# 16.2 전략군별 시나리오 최적화
def get_strategy_for_scenario(scenario: str) -> Dict[str, List[str]]:
    mapping = {
        'up': {
            'name': '고성장 + 모멘텀 전략',
            'components': ['Growth Stocks', 'Momentum Leaders']
        },
        'flat': {
            'name': '균형형 전략',
            'components': ['Low Volatility', 'High ROE']
        },
        'down': {
            'name': '고배당 + 변동성 헷징 전략',
            'components': ['Dividend Stocks', 'Inverse ETFs', 'Volatility Hedge']
        }
    }
    return mapping.get(scenario, {})


# 16.3 전략 중복 제거 및 분산 강화
def remove_overlaps(strategies: Dict[str, Dict]) -> Dict[str, Dict]:
    seen = set()
    for scenario, strat in strategies.items():
        filtered = [s for s in strat.get('components', []) if s not in seen]
        strategies[scenario]['components'] = filtered
        seen.update(filtered)
    return strategies


# 16.4 시나리오 전환 감지 엔진 (Bayesian Change Point)
def detect_scenario_shift(ts_data: List[float], pen: int = 5) -> Optional[int]:
    try:
        model = Binseg(model="l2").fit(ts_data)
        change_points = model.predict(pen=pen)
        return change_points[-1] if change_points else None
    except Exception:
        return None


# 16.5 전략 흐름도: 마르코프 확률 기반 전이 구조
def generate_scenario_markov(prob_dict: Dict[str, float]) -> Dict[str, Dict[str, float]]:
    # 각 상태에서 다른 상태로의 전이 확률 (단순 구조 기반)
    return {
        'up': {
            'flat': round(1 - prob_dict['up'], 3),
            'down': round(prob_dict['down'], 3)
        },
        'flat': {
            'up': round(prob_dict['up'], 3),
            'down': round(prob_dict['down'], 3)
        },
        'down': {
            'flat': round(prob_dict['flat'], 3),
            'up': round(prob_dict['up'], 3)
        }
    }


# ✅ 최종 통합 실행 함수
def run_scenario_branching(market_factors: Dict[str, float], recent_ts: List[float]) -> Dict:
    probs = estimate_market_scenarios(market_factors)
    
    strategies = {
        'up': get_strategy_for_scenario('up'),
        'flat': get_strategy_for_scenario('flat'),
        'down': get_strategy_for_scenario('down')
    }
    strategies = remove_overlaps(strategies)
    
    shift_point = detect_scenario_shift(recent_ts)
    markov_map = generate_scenario_markov(probs)

    return {
        'scenario_probabilities': probs,
        'recommended_strategies': strategies,
        'last_detected_shift_index': shift_point,
        'markov_transition_map': markov_map
    }
    
import streamlit as st

def run():
    st.subheader("📘 16. 리스크 관리 & 손실 방어 시스템")
    st.markdown("“손실을 피하지 못한다면, 최소화라도 하자.”")

    st.markdown("### ✅ 16.1 리스크 감지 지표 요약")
    st.markdown("""
    - 변동성 지수(VIX): **21.4** (경계 수준 돌입)
    - 포트 최대낙폭(MDD): **-12.8%**
    - 포지션 집중도: **특정 섹터 비중 42% (에너지)**
    - 심리 민감도: **고위험 회피형**
    """)

    st.markdown("### ✅ 16.2 리스크 경고 시나리오 감지")
    if st.button("📉 현재 리스크 상태 평가"):
        st.warning("⚠ 리스크 과다 노출 감지됨")
        st.markdown("""
        - 변동성 급등 + MDD -10% 돌파
        - 리밸런싱 또는 헷지 전략 필요
        """)

    st.markdown("### ✅ 16.3 손실 방어 전략 시뮬레이션")
    hedge_option = st.selectbox("🛡 방어 전략 선택", ["현금 비중 확대", "인버스 ETF 편입", "섹터 분산", "고배당주 전환"])
    if st.button("🧪 방어 전략 시뮬레이션 실행"):
        if hedge_option == "현금 비중 확대":
            st.success("현금 비중 40% 확대 시 MDD → -8.3%로 개선 예상")
        elif hedge_option == "인버스 ETF 편입":
            st.info("인버스 ETF 10% 편입 시 수익률 -0.5% 개선 예상")
        elif hedge_option == "섹터 분산":
            st.info("집중 섹터 분산 시 리스크 지수 17% 감소 예상")
        elif hedge_option == "고배당주 전환":
            st.info("배당 수익률 증가로 방어력 +12% 향상 예상")

    st.markdown("### ✅ 16.4 방어 전략 적용 가이드")
    st.markdown("""
    - 리스크 감지 기준:
        - MDD > 10%, 변동성 지수(VIX) > 20, 심리 점수 < 40
    - 전략:
        - 포트 재조정 or 자동 방어 전략 제시
    """)

    st.markdown("📎 이 기능은 module_06(전략 전환), module_08(포트 구성), module_24(사용자 성향)와 연계됩니다.")