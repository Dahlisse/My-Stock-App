# module_18.py

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

# 18.1 메트릭 정규화 + 보정 해석
def normalize_metrics(strategy_df):
    strategy_df = strategy_df.copy()
    scaler = MinMaxScaler()
    numeric_cols = ['CAGR', 'Sharpe', 'Calmar', 'MDD', 'Volatility']
    strategy_df[numeric_cols] = scaler.fit_transform(strategy_df[numeric_cols])
    return strategy_df

def interpret_metrics(row):
    interp = []
    if row['Sharpe'] < 0.3:
        interp.append("Sharpe가 낮은 이유는 변동성 분모가 크기 때문입니다.")
    if row['CAGR'] > 0.7:
        interp.append("최근 3년 평균 수익률이 매우 높습니다.")
    if abs(row['MDD']) > 0.6:
        interp.append("최대 낙폭이 큰 고위험 전략입니다.")
    return ' / '.join(interp)

# 18.2 전략 간 상관관계 히트맵
def plot_strategy_correlation(strategy_returns):
    if strategy_returns.empty:
        print("❗ 전략 수익률 데이터가 비어 있습니다.")
        return pd.DataFrame()
    corr = strategy_returns.corr()
    plt.figure(figsize=(6, 5))
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title("전략 간 상관관계 히트맵")
    plt.tight_layout()
    plt.show()
    return corr

# 18.2 고차원 시각화 (PCA/t-SNE)
def visualize_strategy_space(strategy_df, method='pca'):
    features = strategy_df[['CAGR', 'Sharpe', 'Calmar', 'MDD', 'Volatility']].values
    if method == 'pca':
        reducer = PCA(n_components=2)
    else:
        reducer = TSNE(n_components=2, perplexity=5, n_iter=500, random_state=42)
    reduced = reducer.fit_transform(features)
    result = pd.DataFrame(reduced, columns=['X', 'Y'], index=strategy_df.index)

    plt.figure(figsize=(6, 5))
    sns.scatterplot(data=result, x='X', y='Y', hue=strategy_df.index, s=100)
    plt.title(f"전략 군 시각화 ({method.upper()})")
    plt.tight_layout()
    plt.show()

    return result

# 18.3 트레이드오프 분석
def tradeoff_analysis(strategy_df):
    plt.figure(figsize=(7, 5))
    sns.scatterplot(
        x='Volatility', y='CAGR', hue=strategy_df.index,
        size='Sharpe', sizes=(50, 200), data=strategy_df
    )
    plt.title("수익률 vs 안정성 트레이드오프 (파레토 프론티어)")
    plt.xlabel("변동성 (낮을수록 안정)")
    plt.ylabel("연 수익률 (CAGR)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # 파레토 우위 추정
    pareto_front = []
    for i, row in strategy_df.iterrows():
        dominated = False
        for j, other in strategy_df.iterrows():
            if i == j:
                continue
            if (other['CAGR'] >= row['CAGR']) and (other['Volatility'] <= row['Volatility']):
                dominated = True
                break
        if not dominated:
            pareto_front.append(i)

    return pareto_front

# 전체 실행
def run_metric_comparator(strategy_df, returns_df):
    strategy_df = normalize_metrics(strategy_df)
    strategy_df['설명'] = strategy_df.apply(interpret_metrics, axis=1)

    correlation = plot_strategy_correlation(returns_df)
    tsne_coords = visualize_strategy_space(strategy_df, method='tsne')
    pareto_front = tradeoff_analysis(strategy_df)

    return {
        'normalized_df': strategy_df,
        'correlation': correlation,
        'tsne_coords': tsne_coords,
        'pareto_front': pareto_front
    }
    
import streamlit as st
import datetime

def run():
    st.subheader("📘 18. 실행 자동화 시스템")
    st.markdown("“전략을 설계하는 것만으로는 부족합니다. 실행까지 이어져야 합니다.”")

    st.markdown("### ✅ 18.1 전략 실행 플로우 자동화")
    st.markdown("""
    - 전략 설계 → 실행 시뮬레이션 → 실시간 성과 추적 → 전략 교체 여부 판단 → 사용자 행동 가이드
    - 자동화된 전략 실행 흐름으로 투자 이탈 최소화
    """)

    # 시뮬레이션 시간대 선택
    start_date = st.date_input("전략 실행 시작일", datetime.date.today() - datetime.timedelta(days=30))
    end_date = st.date_input("전략 종료일", datetime.date.today())

    st.success(f"선택된 전략 실행 기간: {start_date} ~ {end_date}")

    st.markdown("### ✅ 18.2 전략 재진입 시점 자동 감지")
    reentry_threshold = st.slider("전략 복귀 기준 수익률 (% 하락 시)", 1, 20, 7)
    st.info(f"📉 전략 수익률이 {reentry_threshold}% 이상 하락하면 재진입 가이드가 표시됩니다.")

    st.markdown("### ✅ 18.3 실행 내비게이션 예시")
    st.markdown("""
    - 현재 전략이 잠시 이탈 구간에 있습니다.
    - **추천 행동:** 매도 보류 / 현금 비중 확대
    - **예상 복귀 시점:** 약 2주 후 예상
    """)

    st.markdown("### ✅ 18.4 행동 이탈 방지 기능")
    st.markdown("""
    - 목표 수익률 도달 시 알림 → **“지금 수익 실현 타이밍입니다”**
    - 손실 커질 시 자동 경고 → **“지금은 행동 자제. 변동성 높습니다”**
    - 리밸런싱 조건 충족 시 자동 팝업 → **“부분 리밸런싱 권장됩니다”**
    """)

    st.markdown("### ✅ 18.5 자동화 실행 조건 설정")
    realtime = st.checkbox("📡 실시간 추적 활성화", value=True)
    tts = st.checkbox("🔊 음성 가이드 활성화 (TTS)", value=False)

    if realtime:
        st.success("🔄 실시간 전략 추적이 활성화되었습니다.")
    if tts:
        st.warning("🔊 음성 가이드는 Safari 브라우저에서 제한될 수 있습니다.")

    st.markdown("---")
    st.caption("※ 본 기능은 module_09(실시간 추적), module_10(음성 안내), module_24(사용자 성향)에 연결됩니다.")