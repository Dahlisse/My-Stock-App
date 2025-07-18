import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# 17.1 전략 비교 메트릭
def compare_strategies(strategies_data):
    # strategies_data: dict[전략명] = {'return': [], 'mdd': [], 'sharpe': [], ...}
    df = pd.DataFrame(strategies_data).T
    df['calmar'] = df['return'] / (abs(df['mdd']) + 1e-6)  # divide-by-zero 회피
    df = df[['return', 'mdd', 'sharpe', 'calmar']].round(4)
    return df

# 17.2 사용자 성향 기반 전략 적합도 점수화
def score_by_user_profile(strategy_df, user_type='중립형'):
    weights = {
        '보수형': {'return': 0.2, 'mdd': -0.4, 'sharpe': 0.3, 'calmar': 0.1},
        '중립형': {'return': 0.3, 'mdd': -0.3, 'sharpe': 0.3, 'calmar': 0.1},
        '공격형': {'return': 0.5, 'mdd': -0.1, 'sharpe': 0.3, 'calmar': 0.1}
    }
    w = weights.get(user_type, weights['중립형'])

    scaler = MinMaxScaler()
    norm_values = scaler.fit_transform(strategy_df)
    norm_df = pd.DataFrame(norm_values, columns=strategy_df.columns, index=strategy_df.index)

    score = norm_df.apply(lambda row: sum(row[k]*w[k] for k in w), axis=1)
    strategy_df['적합도(0~1)'] = score.fillna(0).round(3)
    return strategy_df

# 17.3 전략 우위 전환 감지
def detect_strategy_leader(history_data):
    if history_data is None or history_data.empty:
        return None
    mean_returns = history_data.rolling(window=20).mean()
    leader = mean_returns.idxmax(axis=1)
    return leader

# 17.4 전략 선택 해설 생성기
def explain_strategy_choice(strategy_name, strategy_df):
    if strategy_name not in strategy_df.index:
        return f"{strategy_name} 전략 데이터가 존재하지 않습니다."
    
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
def apply_behavioral_adjustment(strategy_df, bias_type=None):
    if bias_type not in ['loss_aversion', 'overconfidence', 'herding']:
        return strategy_df

    adjustment = strategy_df.copy()
    if '적합도(0~1)' not in adjustment.columns:
        return adjustment

    if bias_type == 'loss_aversion':
        adjustment['적합도(0~1)'] -= adjustment['mdd'].abs() * 0.3
    elif bias_type == 'overconfidence':
        adjustment['적합도(0~1)'] += adjustment['return'] * 0.2
    elif bias_type == 'herding':
        adjustment['적합도(0~1)'] += adjustment['sharpe'] * 0.1

    adjustment['적합도(0~1)'] = adjustment['적합도(0~1)'].clip(0, 1).round(3)
    return adjustment

# 전체 실행 함수
def run_strategy_comparator(strategies_data, user_type='중립형', bias_type=None, history_data=None):
    try:
        comparison_df = compare_strategies(strategies_data)
        scored_df = score_by_user_profile(comparison_df.copy(), user_type)

        if bias_type:
            scored_df = apply_behavioral_adjustment(scored_df, bias_type)

        best_strategy = scored_df['적합도(0~1)'].idxmax()
        explanation = explain_strategy_choice(best_strategy, scored_df)

        leader_flow = detect_strategy_leader(history_data) if history_data is not None else None

        return {
            'scored_df': scored_df,
            'best_strategy': best_strategy,
            'explanation': explanation,
            'leader_flow': leader_flow
        }
    
    except Exception as e:
        # 에러 로깅 필요시 여기 삽입
        return {
            'error': str(e),
            'scored_df': None,
            'best_strategy': None,
            'explanation': None,
            'leader_flow': None
        }
        
import streamlit as st

def run():
    st.header("📘 17단원. 전략 비교 & 트레이드오프 시스템")
    st.markdown("""
    “당신이 무엇을 선택하느냐가 아니라, 당신이 어떤 사람인지가 선택을 만든다.”

    - 17.1 전략 비교 시각화  
      수익률, MDD, Sharpe, Calmar, 변동성 비교  
      사용자 우선순위별 강조 옵션 (수익 vs 안정)

    - 17.2 사용자 성향 기반 전략 적합도 조정  
      보수형: 손실 회피 전략 우선  
      공격형: 성장+변동성 수용 전략  
      적합도 스코어 시각화 포함

    - 17.3 전략 우위 전환 감지  
      시장 변화에 따른 우위 전략 자동 판별  
      우위 흐름 시계열 차트 제공

    - 17.4 전략 선택 해설 생성기 (Explainable AI)  
      사용자 입력 + 시장 조건 분석 후 제안  
      “당신 조건에 최적 전략은 A입니다” 자연어 설명

    - 17.5 행동경제 기반 심리 보정 기능  
      손실회피, 과신, 군중추종 편향 보정  
      성향별 편향 보정 가중치 적용
    """)