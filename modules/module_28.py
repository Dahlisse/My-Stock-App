import streamlit as st
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import uuid
import json
import os
import warnings

# ==========================================
# 1. 전략 설계 인터페이스
# ==========================================
def strategy_builder_ui():
    st.title("📘 자기주도 퀀트 전략 생성 시스템")

    st.subheader("✅ 1단계: 전략 조건 설정")
    selected_indicators = st.multiselect(
        "사용할 지표를 선택하세요",
        ["RSI", "MACD", "SMA(20)", "EMA(50)", "볼린저 밴드", "OBV", "ATR"]
    )

    entry_cond = st.text_input("진입 조건 (예: RSI < 30 and MACD > 0)")
    exit_cond = st.text_input("청산 조건 (예: RSI > 70 or MACD < 0)")

    st.subheader("✅ 2단계: 전략 목표 입력")
    target_return = st.slider("목표 수익률 (%)", 1, 100, 15)
    max_drawdown = st.slider("최대 허용 손실 (%)", 1, 50, 20)

    return {
        "indicators": selected_indicators,
        "entry": entry_cond.strip(),
        "exit": exit_cond.strip(),
        "target": target_return,
        "drawdown": max_drawdown
    }

# ==========================================
# 2. 전략 복잡도 해석 및 시각화
# ==========================================
def visualize_strategy_logic(entry, exit):
    if not entry or not exit:
        st.info("📌 전략 조건을 입력해야 시각화가 가능합니다.")
        return

    G = nx.DiGraph()
    G.add_node("START")
    G.add_node("ENTRY")
    G.add_node("EXIT")
    G.add_edge("START", "ENTRY", label=entry)
    G.add_edge("ENTRY", "EXIT", label=exit)

    pos = nx.spring_layout(G)
    plt.figure(figsize=(8, 4))
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=3000, font_size=10)
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        st.pyplot(plt.gcf())
    plt.clf()

# ==========================================
# 3. 자동 조건 검증 및 경고 시스템
# ==========================================
def check_condition_validity(entry_cond):
    if not entry_cond:
        st.info("📌 진입 조건을 입력하면 복잡도 검토가 가능합니다.")
        return

    logic_depth = entry_cond.lower().count("and") + entry_cond.lower().count("or") + 1
    if logic_depth >= 4:
        st.warning(f"⚠️ 조건이 복잡할 수 있습니다. 진입 가능성 {max(5, 5 * (6 - logic_depth))}% 이하로 예상됨")

# ==========================================
# 4. AI 기반 전략 보완 시스템
# ==========================================
def suggest_improvements(strategy):
    suggestions = []

    if not strategy["exit"]:
        suggestions.append("청산 조건이 비어 있습니다. 기본적인 Exit 전략을 추가하세요.")
    elif "stop" not in strategy["exit"].lower():
        suggestions.append("Stop loss 조건 추가를 고려해보세요.")

    if strategy["target"] > 30 and strategy["drawdown"] < 10:
        suggestions.append("목표 수익률 대비 허용 손실폭이 작을 수 있습니다.")

    if suggestions:
        st.subheader("🤖 AI 전략 보완 제안")
        for s in suggestions:
            st.info(f"💡 {s}")
    else:
        st.success("🎉 현재 전략은 전반적으로 균형 잡혀 있습니다.")

# ==========================================
# 5. 전략 저장 및 재사용 기능
# ==========================================
def save_strategy(strategy):
    try:
        os.makedirs("saved_strategies", exist_ok=True)
        filename = f"saved_strategies/strategy_{uuid.uuid4().hex[:6]}.json"
        with open(filename, "w") as f:
            json.dump(strategy, f, indent=4)
        st.success(f"✅ 전략이 저장되었습니다: {filename}")
    except Exception as e:
        st.error(f"❌ 저장 중 오류 발생: {e}")

# ==========================================
# Main Entrypoint
# ==========================================
def run_self_driven_strategy_designer():
    strategy = strategy_builder_ui()

    st.subheader("🧠 전략 논리 시각화")
    visualize_strategy_logic(strategy["entry"], strategy["exit"])

    st.subheader("🔍 조건 복잡도 검토")
    check_condition_validity(strategy["entry"])

    suggest_improvements(strategy)

    if st.button("📥 전략 저장"):
        save_strategy(strategy)