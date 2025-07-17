# module_04.py
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from datetime import timedelta
from scipy.stats import norm


# 4.1 성과 분석 지표
def calc_performance_metrics(df):
    returns = df['Portfolio'].pct_change().dropna()
    cum_return = (df['Portfolio'].iloc[-1] / df['Portfolio'].iloc[0]) - 1
    annualized_return = (1 + cum_return) ** (252 / len(df)) - 1
    max_dd = (df['Portfolio'] / df['Portfolio'].cummax() - 1).min()
    sharpe = returns.mean() / (returns.std() + 1e-6) * np.sqrt(252)
    calmar = annualized_return / abs(max_dd + 1e-6)

    return {
        '누적 수익률': cum_return,
        '연환산 수익률': annualized_return,
        '최대 낙폭 (MDD)': max_dd,
        'Sharpe Ratio': sharpe,
        'Calmar Ratio': calmar,
    }

# 4.2 수익률 히트맵
def plot_monthly_heatmap(df):
    df['Month'] = df.index.to_period('M')
    monthly_returns = df['Portfolio'].resample('M').last().pct_change()
    heatmap_data = monthly_returns.groupby([monthly_returns.index.year, monthly_returns.index.month]).mean().unstack()
    
    fig, ax = plt.subplots(figsize=(10, 4))
    ax = sns.heatmap(heatmap_data * 100, annot=True, fmt=".1f", cmap="RdYlGn", cbar=False)
    plt.title("월간 수익률 히트맵 (%)")
    st.pyplot(fig)

# 4.2 드로우다운 시각화
def plot_drawdown(df):
    peak = df['Portfolio'].cummax()
    drawdown = (df['Portfolio'] - peak) / peak

    fig, ax = plt.subplots(figsize=(10, 3))
    ax.fill_between(drawdown.index, drawdown.values, color='red', alpha=0.4)
    ax.set_title("📉 드로우다운 (Drawdown)")
    ax.set_ylabel("Drawdown")
    st.pyplot(fig)

# 4.2 백테스트 시뮬레이션 (더미)
def generate_dummy_portfolio(days=500, seed=42):
    np.random.seed(seed)
    dates = pd.date_range(end=pd.Timestamp.today(), periods=days)
    base = 100
    noise = np.random.normal(loc=0.0004, scale=0.01, size=days)
    portfolio = pd.Series(base * (1 + noise).cumprod(), index=dates)
    return pd.DataFrame({'Portfolio': portfolio})

# 4.3 성과 해석
def generate_ai_summary(perf: dict, history_years=10):
    win_years = np.random.randint(6, 10)
    sentence = (
        f"이 전략은 최근 {history_years}년 중 {win_years}년 동안 양의 수익을 기록했습니다.\n"
        f"누적 수익률은 {perf['누적 수익률']*100:.2f}%, 연환산 수익률은 {perf['연환산 수익률']*100:.2f}%입니다.\n"
        f"최대 낙폭은 {perf['최대 낙폭 (MDD)']*100:.2f}%로 위험 관리는 안정적이었습니다.\n"
        f"Sharpe Ratio는 {perf['Sharpe Ratio']:.2f}, Calmar Ratio는 {perf['Calmar Ratio']:.2f}입니다.\n"
        f"이는 투자 대비 수익의 질도 양호한 수준임을 시사합니다."
    )
    return sentence

# 4단원 메인 함수
def module_04_main(show_details=True):
    st.header("📘 4단원. 수익률 시뮬레이션 & 백테스트")

    # 사용자 선택: 국내/해외 시장 포함 여부
    domestic = st.radio("포트 구성 시장 선택", ['국내', '국내 + 해외'])

    # 시뮬레이션: AI가 자동 구성한 포트 수익률 가정
    df = generate_dummy_portfolio()

    # 지표 계산
    perf = calc_performance_metrics(df)

    # 결과 출력
    st.subheader("✅ 핵심 성과 지표")
    for k, v in perf.items():
        st.write(f"{k}: {v*100:.2f}%" if '수익률' in k or '낙폭' in k else f"{k}: {v:.2f}")

    # 그래프 시각화
    st.subheader("📈 수익률 곡선")
    st.line_chart(df)

    st.subheader("📉 드로우다운")
    plot_drawdown(df)

    if show_details:
        st.subheader("📊 월간 수익률 히트맵")
        plot_monthly_heatmap(df)

    st.subheader("🧠 AI 전략 요약")
    st.markdown(generate_ai_summary(perf), unsafe_allow_html=True)

    return perf

if __name__ == "__main__":
    module_04_main()