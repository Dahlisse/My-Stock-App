import streamlit as st
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# 대체 variation 함수 (scipy 없이도 작동)
def safe_variation(series):
    mean = np.mean(series)
    std = np.std(series)
    return std / mean if mean != 0 else 0

# 6.1 전략 제안
def suggest_strategy(fin_metrics, perf_metrics, sentiment_score, macro_vars):
    per = fin_metrics.get("PER", 10)
    peg = fin_metrics.get("PEG", 1.2)
    growth = fin_metrics.get("매출성장률", 0.12)
    roe = fin_metrics.get("ROE", 10)
    volatility = perf_metrics.get("변동성", 0.15)
    interest = macro_vars.get("금리", 3.0)

    if sentiment_score > 65 and growth > 0.15:
        return "📈 성장형"
    elif per < 10 and peg < 1.0 and interest > 3.0:
        return "🏦 가치형"
    elif roe > 8 and volatility > 0.2 and sentiment_score < 40:
        return "🛡 안정형"
    else:
        return "⚡ 모멘텀형"

# 6.2 전략 전환 감지
def detect_strategy_shift(portfolio_returns, sentiment_series, macro_df):
    if len(portfolio_returns) < 30:
        return False, 0.0, "데이터 부족"

    recent_returns = portfolio_returns[-30:]
    mdd = (recent_returns / np.maximum.accumulate(recent_returns) - 1).min()
    vol = np.std(recent_returns)
    stability = 1 - safe_variation(recent_returns)

    sentiment_delta = sentiment_series.diff().rolling(3).mean().iloc[-1]
    macro_jump = macro_df.pct_change().abs().mean().mean()

    trigger = stability < 0.35 or abs(sentiment_delta) > 10 or macro_jump > 0.03
    reason = []
    if stability < 0.35:
        reason.append("전략 안정성 저하")
    if abs(sentiment_delta) > 10:
        reason.append("시장 심리 급변")
    if macro_jump > 0.03:
        reason.append("매크로 변수 급등락")

    return trigger, round(stability, 2), " + ".join(reason)

# 6.3 전략 비교
def compare_strategies(results: list):
    df = pd.DataFrame(results)
    scaler = MinMaxScaler()
    score_cols = ["누적수익률", "최대낙폭", "Sharpe", "심리적합도", "전략안정성"]
    for col in score_cols:
        if col in df:
            if col == "최대낙폭":
                df[col + "_norm"] = 1 - scaler.fit_transform(df[[col]])
            else:
                df[col + "_norm"] = scaler.fit_transform(df[[col]])

    norm_cols = [c + "_norm" for c in score_cols if c + "_norm" in df.columns]
    df["종합점수"] = df[norm_cols].mean(axis=1)
    return df.sort_values("종합점수", ascending=False)

# 전략 해설
def explain_strategy(name, score_row):
    return (
        f"🔍 **{name} 전략 해설**\n"
        f"- 누적 수익률: {score_row['누적수익률']*100:.2f}%\n"
        f"- 최대 낙폭: {score_row['최대낙폭']*100:.2f}%\n"
        f"- Sharpe: {score_row['Sharpe']:.2f}, 심리 적합도: {score_row['심리적합도']:.2f}\n"
        f"- 전략 안정성 지표: {score_row['전략안정성']:.2f}\n\n"
        f"👉 종합 판단: 이 전략은 현재 시장에 **{'잘 적합' if score_row['종합점수'] > 0.6 else '위험 요소 존재'}**합니다."
    )

# 메인 함수
def module_06_main():
    st.header("📘 6단원. AI 전략 제안 & 전환 감지")

    # 더미 입력
    fin_metrics = {"PER": 9.3, "PEG": 0.8, "매출성장률": 0.13, "ROE": 12}
    perf_metrics = {"누적수익률": 0.38, "변동성": 0.16, "Sharpe": 1.1, "최대낙폭": -0.19}
    macro_vars = {"금리": 3.25, "환율": 1310, "CPI": 3.7}
    sentiment_score = st.slider("📊 현재 시장 심리 점수", 0, 100, 55)

    strategy = suggest_strategy(fin_metrics, perf_metrics, sentiment_score, macro_vars)
    st.subheader("🤖 AI 전략 제안")
    st.success(f"추천 전략 유형: {strategy}")

    # 시드 고정
    np.random.seed(42)

    returns = pd.Series(np.random.normal(0.001, 0.02, 90)).cumsum()
    sentiment_series = pd.Series(np.random.normal(sentiment_score, 5, 90))
    macro_df = pd.DataFrame({
        "금리": np.random.normal(3.0, 0.1, 90),
        "환율": np.random.normal(1300, 10, 90),
        "CPI": np.random.normal(3.5, 0.1, 90)
    })

    shift, stability_score, reason = detect_strategy_shift(returns, sentiment_series, macro_df)
    st.subheader("📉 전략 전환 감지")
    if shift:
        st.warning(f"⚠ 전략 전환 필요 감지됨\n• 원인: {reason}\n• 안정성 지표: {stability_score:.2f}")
    else:
        st.success(f"✅ 전략 유지 가능\n• 전략 안정성 지표: {stability_score:.2f}")

    st.subheader("📊 전략 A/B/C 비교")
    dummy_results = [
        {"전략명": "A-성장형", "누적수익률": 0.42, "최대낙폭": -0.25, "Sharpe": 1.05, "심리적합도": 75, "전략안정성": 0.72},
        {"전략명": "B-가치형", "누적수익률": 0.33, "최대낙폭": -0.15, "Sharpe": 0.88, "심리적합도": 62, "전략안정성": 0.81},
        {"전략명": "C-모멘텀형", "누적수익률": 0.39, "최대낙폭": -0.21, "Sharpe": 1.12, "심리적합도": 58, "전략안정성": 0.64},
    ]
    result_df = compare_strategies(dummy_results)
    st.dataframe(result_df[["전략명", "종합점수"] + [c for c in result_df.columns if c.endswith("_norm")]])

    st.subheader("🧠 전략별 자연어 해설")
    for _, row in result_df.iterrows():
        st.markdown(explain_strategy(row["전략명"], row))

# Streamlit 클라우드용 엔트리포인트
if __name__ == "__main__":
    module_06_main()
    
import streamlit as st

# 예시 함수 (실제 로직은 별도 모듈에서 처리해야 함)
# from .strategy_generator import generate_strategy
# from .rebalance_detector import detect_rebalance_point
# from .stability_evaluator import evaluate_strategy_stability
# from .change_point_detection import detect_change_point
# from .strategy_comparator import compare_strategies

def run():
    st.subheader("📘 6단원. AI 전략 제안 & 전환 감지")
    st.markdown("“전략은 고정되지 않는다. 스스로 바꾸는 AI”")

    # 6.1 전략 제안 및 리밸런싱
    st.markdown("### ⚙️ 6.1 전략 제안 및 리밸런싱")
    st.markdown("""
    - 4단원에서 자동 생성된 포트폴리오 기반 전략 분류  
    - 가치형 / 성장형 / 안정형 / 모멘텀형 등 자동 매핑
    """)

    if st.button("📌 전략 자동 제안"):
        # strategy = generate_strategy(portfolio_data, macro_data, sentiment_score)
        st.success("AI 전략 제안이 완료되었습니다 ✅")
        st.markdown("""
        - **전략 유형**: 성장형 + 안정형 혼합  
        - **핵심 근거**: ROE 상위, PEG 0.8, 시장 심리 과열  
        - **전략 코드**: `GROWTH_21C_MIX`
        """)

    if st.button("♻️ 리밸런싱 시점 자동 감지"):
        # rebalance_needed = detect_rebalance_point(performance_metrics)
        st.info("리밸런싱 필요: **부분 재조정 권장**")
        st.markdown("""
        - 수익률 저하 구간: 최근 10일  
        - 심리 변화: 공포 전환 → 전략 부적합 감지  
        - 리밸런싱 방식: 핵심 종목 2개 교체
        """)

    st.divider()

    # 6.2 전략 전환 탐지
    st.markdown("### 🔄 6.2 전략 전환 탐지")
    st.markdown("""
    - Bayesian Change Point Detection 기반 동적 탐지  
    - 전략 안정성 지표 (Stability Index) 도입
    """)

    if st.button("📉 전략 전환 위험 감지"):
        # stability_score = evaluate_strategy_stability(strategy_data)
        # change_point = detect_change_point(performance_time_series)
        st.warning("⚠️ 전략 안정성 저하 감지됨")
        st.markdown("""
        - Stability Index: **0.26** (기준 이하)  
        - 최근 변동성 급등 + MDD 증가  
        - 전략 전환 권고: 예, **B 전략(안정형)** 전환 추천
        """)

    st.divider()

    # 6.3 전략 비교 해설
    st.markdown("### 🧠 6.3 전략 비교 해설")
    st.markdown("""
    - 전략 간 누적 수익률, 변동성, 심리 적합도 등 종합 비교  
    - 자연어 기반 전략 해설 포함
    """)

    if st.button("📊 전략 비교 실행"):
        # comparison_result = compare_strategies([A, B, C])
        st.success("전략 비교 완료 ✅")
        st.markdown("""
        | 전략 | 수익률 | 변동성 | 적합도 | 성공 확률 |
        |-------|--------|--------|--------|------------|
        | A     | 47.1%  | 중간   | 낮음   | 58.2%     |
        | B     | 42.9%  | 낮음   | 높음   | 74.5%     |
        | C     | 52.3%  | 높음   | 중간   | 66.7%     |

        **추천 전략: B (안정형 배당주 중심)**  
        > 현재 시장은 변동성이 높고 공포지수가 급등한 상태입니다. 이에 따라 B 전략이 적합합니다.
        """)

    st.info("📡 이 전략 정보는 8단원 포트 구성에 자동 전달됩니다.")