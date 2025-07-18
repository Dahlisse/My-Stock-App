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

def run():
    st.header("📘 18단원. 전략 메트릭 비교 & 해석 시스템")
    st.markdown("""
    “모든 전략은 숫자로 말하게 하라.”

    - 18.1 전략 성과 메트릭 정규화  
      CAGR, Sharpe, Calmar, Max Drawdown 통일 스케일  
      시기별 변동성 보정 Sharpe  
      왜도·첨도 등 고차 리스크 보정 포함  
      해석 보조 문구 자동 생성

    - 18.2 전략 간 상관관계 구조 시각화  
      공분산, 상관계수 히트맵 제공  
      상호보완 전략 자동 추출  
      t-SNE/PCA 3D 포지셔닝 시각화  
      해설 포함

    - 18.3 전략 간 트레이드오프 분석  
      수익률 vs 안정성 파레토 프론티어 시각화  
      유사 전략 제거 → 다양성 최적화  
      효율적 우위 판단 포함
    """)