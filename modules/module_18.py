# module_18.py

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

# 18.1 메트릭 정규화 + 보정 해석
def normalize_metrics(strategy_df):
    scaler = MinMaxScaler()
    numeric_cols = ['CAGR', 'Sharpe', 'Calmar', 'MDD', 'Volatility']
    normalized = pd.DataFrame(scaler.fit_transform(strategy_df[numeric_cols]), columns=numeric_cols, index=strategy_df.index)
    strategy_df[numeric_cols] = normalized
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
    corr = strategy_returns.corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm')
    plt.title("전략 간 상관관계 히트맵")
    plt.show()
    return corr

# 18.2 고차원 시각화 (PCA/t-SNE)
def visualize_strategy_space(strategy_df, method='pca'):
    features = strategy_df[['CAGR', 'Sharpe', 'Calmar', 'MDD', 'Volatility']].values
    if method == 'pca':
        reducer = PCA(n_components=2)
    else:
        reducer = TSNE(n_components=2, perplexity=5, n_iter=500, random_state=0)
    reduced = reducer.fit_transform(features)
    result = pd.DataFrame(reduced, columns=['X', 'Y'], index=strategy_df.index)

    plt.figure(figsize=(6,5))
    sns.scatterplot(data=result, x='X', y='Y', hue=strategy_df.index, s=100)
    plt.title(f"전략 군 시각화 ({method.upper()})")
    plt.show()

    return result

# 18.3 트레이드오프 분석
def tradeoff_analysis(strategy_df):
    plt.figure(figsize=(7,5))
    sns.scatterplot(
        x='Volatility', y='CAGR', hue=strategy_df.index,
        size='Sharpe', sizes=(50, 200), data=strategy_df
    )
    plt.title("수익률 vs 안정성 트레이드오프 (파레토 프론티어)")
    plt.xlabel("변동성 (낮을수록 안정)")
    plt.ylabel("연 수익률 (CAGR)")
    plt.grid(True)
    plt.show()

    # 파레토 우위 추정
    pareto_front = []
    for i, row in strategy_df.iterrows():
        if all((row['CAGR'] >= other['CAGR']) and (row['Volatility'] <= other['Volatility']) 
               for j, other in strategy_df.iterrows() if i != j):
            pareto_front.append(i)

    return pareto_front

# 전체 실행
def run_metric_comparator(strategy_df, returns_df):
    strategy_df = normalize_metrics(strategy_df)
    strategy_df['설명'] = strategy_df.apply(interpret_metrics, axis=1)

    corr = plot_strategy_correlation(returns_df)
    tsne_result = visualize_strategy_space(strategy_df, method='tsne')
    pareto_strategies = tradeoff_analysis(strategy_df)

    return {
        'normalized_df': strategy_df,
        'correlation': corr,
        'tsne_coords': tsne_result,
        'pareto_front': pareto_strategies
    }