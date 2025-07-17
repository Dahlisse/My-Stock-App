# module_05.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import random
from wordcloud import WordCloud
from datetime import datetime, timedelta

# 시드 고정 (재현 가능성 확보)
np.random.seed(42)
random.seed(42)

# 5.1 뉴스·감성 분석 (더미 기반)
def simulate_news_sentiment(n=50):
    keywords = ["금리", "환율", "전쟁", "성장", "리세션", "수출", "반도체", "ETF", "테슬라", "연준"]
    sentiment_scores = np.random.normal(loc=0.1, scale=0.5, size=n)
    summary = []
    keyword_freq = {}

    for i in range(n):
        score = sentiment_scores[i]
        keyword = random.choice(keywords)
        keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
        sentiment = "긍정" if score > 0.1 else "부정" if score < -0.1 else "중립"
        summary.append({
            "뉴스": f"{keyword} 관련 뉴스 제목 {i+1}",
            "감성": sentiment,
            "점수": float(score)
        })
    return pd.DataFrame(summary), keyword_freq

def plot_wordcloud(keyword_freq):
    wc = WordCloud(background_color='white', width=800, height=300, font_path=None)
    wc.generate_from_frequencies(keyword_freq)
    plt.figure(figsize=(10, 3))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout()
    st.pyplot(plt.gcf())
    plt.clf()  # 중첩 방지

# 5.2 수급 및 외부 변수 (더미)
def simulate_macro_variables():
    today = datetime.today()
    dates = pd.date_range(end=today, periods=90)

    data = {
        "금리": np.random.normal(3.0, 0.2, len(dates)),
        "환율": np.random.normal(1300, 20, len(dates)),
        "유가": np.random.normal(75, 5, len(dates)),
        "CPI": np.random.normal(3.5, 0.3, len(dates)),
        "Fear-Greed Index": np.random.uniform(0, 100, len(dates))
    }
    return pd.DataFrame(data, index=dates)

def plot_macro_time_series(df):
    st.subheader("📊 매크로 변수 시계열")
    for col in df.columns:
        st.line_chart(df[[col]])

# 5.3 심리 점수화
def compute_sentiment_score(news_df, macro_df):
    try:
        pos_ratio = (news_df['감성'] == '긍정').mean()
        fear_index = float(macro_df['Fear-Greed Index'].iloc[-1])
        vol_spike = np.std(macro_df['유가']) > 7 or np.std(macro_df['환율']) > 25

        base_score = pos_ratio * 100 - fear_index * 0.3
        score = max(0, min(100, base_score - 10 if vol_spike else base_score))
        label = "과열" if score > 70 else "침체" if score < 30 else "중립"
    except Exception as e:
        score = 50.0
        label = "중립"
        st.error(f"심리 점수 계산 오류: {e}")
    return score, label

# 전체 모듈 실행
def run():
    st.header("📘 5단원. 시장 심리 및 외부 요인 분석")

    # 5.1 뉴스 감성 분석
    st.subheader("📰 뉴스 키워드 및 감성 분석")
    news_df, keyword_freq = simulate_news_sentiment()
    st.dataframe(news_df.head(10))
    st.write("📌 키워드 기반 WordCloud")
    plot_wordcloud(keyword_freq)

    # 5.2 수급 및 매크로 변수
    st.subheader("📈 수급 및 외부 변수 시계열")
    macro_df = simulate_macro_variables()
    plot_macro_time_series(macro_df)

    # 5.3 심리 점수화
    st.subheader("💡 시장 심리 스코어링")
    score, label = compute_sentiment_score(news_df, macro_df)
    st.metric("시장 심리 민감도 점수", f"{score:.2f} / 100")
    st.write(f"군중 심리 상태 판단: **{label} 상태**")

    # 메시지 출력
    if label == "과열":
        st.warning("⚠ 현재 시장은 과열 상태로 판단됩니다. 방어적 전략을 고려하세요.")
    elif label == "침체":
        st.info("📉 현재 시장은 침체 분위기입니다. 안정형 전략이 적합할 수 있습니다.")
    else:
        st.success("시장 심리가 안정적이며 중립적입니다.")

    return score