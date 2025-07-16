# module_16.py

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
from scipy.stats import entropy
from statsmodels.tsa.stattools import adfuller
from ruptures import Binseg

# 16.1 상승/보합/하락 시나리오 확률 추정
def estimate_market_scenarios(market_factors):
    # market_factors: dict with keys like 'momentum', 'volatility', 'macro_score'
    factors = np.array(list(market_factors.values()))
    scaler = MinMaxScaler()
    norm = scaler.fit_transform(factors.reshape(1, -1))[0]

    prob_up = norm[0] * 0.5 + (1 - norm[1]) * 0.3 + norm[2] * 0.2
    prob_flat = (1 - abs(norm[0] - 0.5)) * 0.6
    prob_down = 1 - prob_up - prob_flat
    prob_down = max(0, min(1, prob_down))
    prob_flat = max(0, min(1, 1 - prob_up - prob_down))
    prob_up = max(0, min(1, 1 - prob_down - prob_flat))

    probs = {'up': round(prob_up, 3), 'flat': round(prob_flat, 3), 'down': round(prob_down, 3)}
    return probs

# 16.2 전략군별 시나리오 최적화
def get_strategy_for_scenario(scenario):
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
def remove_overlaps(strategies):
    seen = set()
    for scenario, strat in strategies.items():
        filtered = [s for s in strat['components'] if s not in seen]
        strategies[scenario]['components'] = filtered
        seen.update(filtered)
    return strategies

# 16.4 시나리오 전환 감지 엔진 (Bayesian Change Point)
def detect_scenario_shift(ts_data, pen=5):
    # ts_data: 시계열 (ex. 수익률, 심리 점수 등)
    model = Binseg(model="l2").fit(ts_data)
    change_points = model.predict(pen=pen)
    return change_points[-1] if change_points else None

# 16.5 전략 흐름도: 마르코프 확률 기반
def generate_scenario_markov(prob_dict):
    flow_map = {
        'up': {'flat': 1 - prob_dict['up'], 'down': prob_dict['down']},
        'flat': {'up': prob_dict['up'], 'down': prob_dict['down']},
        'down': {'flat': prob_dict['flat'], 'up': prob_dict['up']}
    }
    return flow_map

# 통합 실행 함수
def run_scenario_branching(market_factors, recent_ts):
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