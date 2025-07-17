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