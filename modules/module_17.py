# module_17.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA

# 17.1 전략 비교 메트릭
def compare_strategies(strategies_data):
    # strategies_data: dict[전략명] = {'return': [], 'mdd': [], 'sharpe': [], ...}
    df = pd.DataFrame(strategies_data).T
    df['calmar'] = df['return'] / (abs(df['mdd']) + 1e-6)
    return df[['return', 'mdd', 'sharpe', 'calmar']].round(3)

# 17.2 사용자 성향 기반 전략 적합도 점수화
def score_by_user_profile(strategy_df, user_type='보수형'):
    weights = {
        '보수형': {'return': 0.2, 'mdd': -0.4, 'sharpe': 0.3, 'calmar': 0.1},
        '중립형': {'return': 0.3, 'mdd': -0.3, 'sharpe': 0.3, 'calmar': 0.1},
        '공격형': {'return': 0.5, 'mdd': -0.1, 'sharpe': 0.3, 'calmar': 0.1}
    }
    w = weights.get(user_type, weights['중립형'])

    scaler = MinMaxScaler()
    norm_df = pd.DataFrame(scaler.fit_transform(strategy_df), columns=strategy_df.columns)
    score = norm_df.apply(lambda row: sum(row[k]*w[k] for k in w), axis=1)
    strategy_df['적합도(0~1)'] = score.round(3)
    return strategy_df

# 17.3 전략 우위 전환 감지
def detect_strategy_leader(history_data):
    # history_data: DataFrame(columns=[A, B, C...], index=시점), 수익률
    mean_returns = history_data.rolling(window=20).mean()
    leader = mean_returns.idxmax(axis=1)
    return leader

# 17.4 전략 선택 해설 생성기
def explain_strategy_choice(strategy_name, strategy_df):
    row = strategy_df.loc[strategy_name]
    parts = []
    if row['sharpe'] > 1:
        parts.append("수익 대비 리스크가 우수하며")
    if abs(row['mdd']) < 0.1:
        parts.append("낙폭이 작아 안정적입니다.")
    else:
        parts.append("낙폭이 크지만 수익률이 이를 상쇄할 수 있습니다.")
    return f"{strategy_name} 전략은 " + ' '.join(parts)

# 17.5 행동경제 기반 심리 보정
def apply_behavioral_adjustment(strategy_df, bias_type):
    # bias_type: 'loss_aversion', 'overconfidence', 'herding'
    if bias_type == 'loss_aversion':
        strategy_df['적합도(0~1)'] -= strategy_df['mdd'].abs() * 0.3
    elif bias_type == 'overconfidence':
        strategy_df['적합도(0~1)'] += strategy_df['return'] * 0.2
    elif bias_type == 'herding':
        strategy_df['적합도(0~1)'] += strategy_df['sharpe'] * 0.1
    return strategy_df.round(3)

# 전체 실행 함수
def run_strategy_comparator(strategies_data, user_type='보수형', bias_type=None, history_data=None):
    comparison_df = compare_strategies(strategies_data)
    scored_df = score_by_user_profile(comparison_df, user_type)

    if bias_type:
        scored_df = apply_behavioral_adjustment(scored_df, bias_type)

    best_strategy = scored_df['적합도(0~1)'].idxmax()
    explanation = explain_strategy_choice(best_strategy, scored_df)

    flow = None
    if history_data is not None:
        flow = detect_strategy_leader(history_data)

    return {
        'scored_df': scored_df,
        'best_strategy': best_strategy,
        'explanation': explanation,
        'leader_flow': flow
    }