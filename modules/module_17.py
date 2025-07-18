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
import matplotlib.pyplot as plt

def run():
    st.subheader("📘 17. 트레이드오프 분석 시각화")
    st.markdown("“수익률만 보는 시대는 끝났다. 리스크를 감안해야 진짜 실력이다.”")

    st.markdown("### ✅ 17.1 전략 간 수익률 vs 리스크 맵")
    st.markdown("아래 그래프는 전략별 연평균 수익률과 변동성을 시각화한 것입니다.")

    strategies = ["A(성장형)", "B(가치형)", "C(안정형)", "D(모멘텀형)"]
    returns = [12.5, 9.1, 7.0, 11.3]
    risks = [18.2, 12.7, 9.3, 15.4]

    fig, ax = plt.subplots()
    ax.scatter(risks, returns)

    for i, strategy in enumerate(strategies):
        ax.annotate(strategy, (risks[i]+0.3, returns[i]+0.3))

    ax.set_xlabel("변동성 (%)")
    ax.set_ylabel("연평균 수익률 (%)")
    ax.set_title("전략별 수익률 vs 리스크 비교")
    st.pyplot(fig)

    st.markdown("### ✅ 17.2 성장성 vs 안정성 비교")
    st.markdown("아래는 전략별 성장성 지표(ROE 등)와 안정성 지표(Stability Index)를 비교한 그래프입니다.")

    growth_scores = [8.2, 5.9, 4.1, 7.3]
    stability_scores = [0.52, 0.71, 0.83, 0.48]

    fig2, ax2 = plt.subplots()
    ax2.scatter(growth_scores, stability_scores, color='green')

    for i, strategy in enumerate(strategies):
        ax2.annotate(strategy, (growth_scores[i]+0.1, stability_scores[i]+0.01))

    ax2.set_xlabel("성장성 지표 (평균 ROE 등급)")
    ax2.set_ylabel("전략 안정성 지표 (0~1)")
    ax2.set_title("전략별 성장성 vs 안정성")
    st.pyplot(fig2)

    st.markdown("### ✅ 17.3 전략 선택 가이드")
    st.markdown("""
    - 📈 **공격형 사용자**: 성장성 우선 (예: 전략 A, D)
    - 🛡 **보수형 사용자**: 안정성 우선 (예: 전략 C)
    - ⚖ **균형형 사용자**: B 전략 적합

    👉 *전략 선택은 module_24 사용자 성향 분석을 기반으로 자동 제안될 수 있습니다.*
    """)

    st.markdown("📎 이 시각화는 module_06(전략), module_08(포트 구성), module_16(리스크 분석)과 연동됩니다.")