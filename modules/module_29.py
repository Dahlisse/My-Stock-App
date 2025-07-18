import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from typing import List, Dict, Any, Optional

# 29.1 시나리오 기반 전략 성능 평가
class ScenarioSimulator:
    def __init__(self, strategy_results: Dict[str, pd.DataFrame]):
        """
        strategy_results: {
            "strategy_A": pd.DataFrame (columns: date, return, drawdown, volatility),
            ...
        }
        """
        self.strategy_results = strategy_results
        self.scenario_results: Dict[str, Dict[str, Dict[str, float]]] = {}

    def simulate_scenarios(self, scenarios: Dict[str, Dict[str, Any]]) -> None:
        """
        scenarios: {
            "High_Inflation": {"conditions": {...}, "affected_strategies": [...]},
            ...
        }
        """
        for scenario_name, scenario in scenarios.items():
            results = {}
            for strat in scenario.get("affected_strategies", []):
                strat_df = self.strategy_results.get(strat)
                if strat_df is not None and not strat_df.empty:
                    mdd = strat_df['drawdown'].max()
                    avg_return = strat_df['return'].mean()
                    results[strat] = {
                        "avg_return": avg_return,
                        "mdd": mdd
                    }
            self.scenario_results[scenario_name] = results

    def get_scenario_matrix(self) -> pd.DataFrame:
        matrix = []
        for scenario, results in self.scenario_results.items():
            for strat, metrics in results.items():
                matrix.append({
                    "Scenario": scenario,
                    "Strategy": strat,
                    "AvgReturn": metrics.get("avg_return"),
                    "MDD": metrics.get("mdd")
                })
        return pd.DataFrame(matrix)

    def visualize_scenario_matrix(self) -> None:
        df = self.get_scenario_matrix()
        if df.empty:
            print("No scenario data to visualize.")
            return
        pivot = df.pivot(index="Strategy", columns="Scenario", values="AvgReturn")
        pivot.plot(kind="bar", figsize=(12, 6), title="Scenario vs Strategy Performance")
        plt.ylabel("Average Return")
        plt.tight_layout()
        plt.show()


# 29.2 전략 혼합 시뮬레이션
class StrategyMixSimulator:
    def __init__(self, strategies: Dict[str, pd.DataFrame]):
        self.strategies = strategies

    def simulate_mix(self, weights: Dict[str, float]) -> pd.Series:
        returns_list = []
        for name, weight in weights.items():
            df = self.strategies.get(name)
            if df is None or 'return' not in df:
                raise ValueError(f"Strategy '{name}' is missing or invalid.")
            weighted_return = df['return'] * weight
            returns_list.append(weighted_return)
        combined_returns = sum(returns_list)
        cumulative_return = (1 + combined_returns).cumprod() - 1
        return cumulative_return

    def optimize_allocation(self) -> Dict[str, float]:
        # Dummy optimizer (equal weight)
        n = len(self.strategies)
        if n == 0:
            return {}
        return {k: 1.0 / n for k in self.strategies}


# 29.3 이벤트 기반 전략 전환 시스템
class EventBasedSwitcher:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_trigger(self, condition: str, from_strategy: str, to_strategy: str) -> None:
        self.graph.add_edge(from_strategy, to_strategy, label=condition)

    def visualize_strategy_map(self) -> None:
        if self.graph.number_of_nodes() == 0:
            print("No strategy transition defined.")
            return
        pos = nx.spring_layout(self.graph)
        plt.figure(figsize=(10, 6))
        nx.draw(self.graph, pos, with_labels=True, node_color='skyblue', node_size=2000, font_size=10, font_weight='bold')
        labels = nx.get_edge_attributes(self.graph, 'label')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=labels, font_color='red')
        plt.title("Event-Based Strategy Flow")
        plt.show()

    def simulate_transition(self, current_strategy: str, trigger_event: str) -> str:
        for u, v, data in self.graph.edges(data=True):
            if u == current_strategy and data.get("label") == trigger_event:
                return v
        return current_strategy


# 예제 실행 (단독 실행 시 테스트용)
if __name__ == "__main__":
    # 더미 전략 수익률 생성
    dates = pd.date_range("2023-01-01", periods=100)
    strategy_A = pd.DataFrame({
        "date": dates,
        "return": np.random.normal(0.001, 0.01, size=100),
        "drawdown": np.random.uniform(0, 0.15, size=100),
        "volatility": np.random.uniform(0.01, 0.03, size=100)
    })

    strategy_B = pd.DataFrame({
        "date": dates,
        "return": np.random.normal(0.0008, 0.008, size=100),
        "drawdown": np.random.uniform(0, 0.10, size=100),
        "volatility": np.random.uniform(0.01, 0.025, size=100)
    })

    # 전략 등록
    strategies = {
        "Strategy_A": strategy_A,
        "Strategy_B": strategy_B
    }

    # 시나리오별 전략 평가
    scenario_simulator = ScenarioSimulator(strategies)
    scenario_simulator.simulate_scenarios({
        "High_Inflation": {
            "conditions": {"CPI": "high", "interest_rate": "high"},
            "affected_strategies": ["Strategy_A", "Strategy_B"]
        },
        "Recession": {
            "conditions": {"GDP": "low", "unemployment": "high"},
            "affected_strategies": ["Strategy_B"]
        }
    })
    scenario_simulator.visualize_scenario_matrix()

    # 전략 혼합 평가
    mix_simulator = StrategyMixSimulator(strategies)
    weights = {"Strategy_A": 0.6, "Strategy_B": 0.4}
    cumulative = mix_simulator.simulate_mix(weights)
    cumulative.plot(title="Mixed Strategy Cumulative Return", figsize=(10, 4))
    plt.show()

    # 이벤트 기반 전략 전환 테스트
    switcher = EventBasedSwitcher()
    switcher.add_trigger("VIX > 30", "Strategy_A", "Strategy_B")
    switcher.add_trigger("Interest Rate Hike", "Strategy_B", "Strategy_A")
    switcher.visualize_strategy_map()
    next_strategy = switcher.simulate_transition("Strategy_A", "VIX > 30")
    print("📌 Transitioned Strategy:", next_strategy)
    
import streamlit as st

def run():
    st.header("📘 29단원. 전략 시나리오 설계 & 멀티 시뮬레이션 시스템")
    st.markdown("""
    “미래는 하나가 아니다. 모든 경우의 수에 대비하라.”

    - 29.1 멀티 시나리오 전략 시뮬레이션 엔진  
      금리, 환율, 지정학 리스크 등 시나리오 조건 정의  
      전략 × 시나리오 조합 결과 자동 시뮬레이션  
      “전략 A는 금리 상승기에서 MDD 8% → 전략 B 대체 필요”  
      시나리오 기반 민감도 매트릭스 제공

    - 29.2 복수 전략 조합 & 비중 시뮬레이션  
      전략 A+B+C 조합 백테스트  
      비중 변화 시 수익률/리스크 실시간 시각화  
      “전략군 혼합 최적 포트: A 40% + B 35% + C 25%”  
      전략 간 중복 종목 자동 제거 기능 포함

    - 29.3 사용자 정의 이벤트 기반 전략 분기 설계  
      VIX > 30 시 전략 전환 트리거 조건 정의  
      시나리오 플로우차트 생성 + 자동 실행  
      전체 전략 맵 시각화 및 전환 예측률 제공
    """)