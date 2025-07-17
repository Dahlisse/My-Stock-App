# module_29.py

import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from typing import List, Dict, Any

class ScenarioSimulator:
    def __init__(self, strategy_results: Dict[str, pd.DataFrame]):
        """
        strategy_results: {
            "strategy_A": pd.DataFrame (with columns: date, return, drawdown, volatility),
            "strategy_B": ...
        }
        """
        self.strategy_results = strategy_results
        self.scenario_results = {}

    def simulate_scenarios(self, scenarios: Dict[str, Dict[str, Any]]):
        """
        scenarios: {
            "High_Inflation": {"conditions": {"CPI": "high", "interest_rate": "high"}, "affected_strategies": [...]},
            ...
        }
        """
        for scenario_name, scenario in scenarios.items():
            results = {}
            for strat in scenario["affected_strategies"]:
                strat_df = self.strategy_results.get(strat)
                if strat_df is not None:
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
                    "AvgReturn": metrics["avg_return"],
                    "MDD": metrics["mdd"]
                })
        return pd.DataFrame(matrix)

    def visualize_scenario_matrix(self):
        df = self.get_scenario_matrix()
        pivot = df.pivot(index="Strategy", columns="Scenario", values="AvgReturn")
        pivot.plot(kind="bar", figsize=(12,6), title="Scenario vs Strategy Performance")
        plt.ylabel("Average Return")
        plt.tight_layout()
        plt.show()


class StrategyMixSimulator:
    def __init__(self, strategies: Dict[str, pd.DataFrame]):
        self.strategies = strategies

    def simulate_mix(self, weights: Dict[str, float]):
        returns_list = []
        for name, weight in weights.items():
            df = self.strategies[name]
            weighted_return = df['return'] * weight
            returns_list.append(weighted_return)
        combined_returns = sum(returns_list)
        cumulative_return = (1 + combined_returns).cumprod() - 1
        return cumulative_return

    def optimize_allocation(self):
        # Dummy optimization: equally weighted (replace with actual optimizer later)
        n = len(self.strategies)
        return {k: 1/n for k in self.strategies}


class EventBasedSwitcher:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_trigger(self, condition: str, from_strategy: str, to_strategy: str):
        self.graph.add_edge(from_strategy, to_strategy, label=condition)

    def visualize_strategy_map(self):
        pos = nx.spring_layout(self.graph)
        plt.figure(figsize=(10, 6))
        nx.draw(self.graph, pos, with_labels=True, node_color='skyblue', node_size=2000, font_size=10, font_weight='bold')
        labels = nx.get_edge_attributes(self.graph, 'label')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=labels, font_color='red')
        plt.title("Event-Based Strategy Flow")
        plt.show()

    def simulate_transition(self, current_strategy: str, trigger_event: str):
        for u, v, data in self.graph.edges(data=True):
            if u == current_strategy and data["label"] == trigger_event:
                return v
        return current_strategy  # No change


# Example Usage
if __name__ == "__main__":
    # Dummy strategy results
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

    # 전략별 시뮬레이션
    strategies = {
        "Strategy_A": strategy_A,
        "Strategy_B": strategy_B
    }

    # 29.1 시나리오별 전략 시뮬레이션
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

    # 29.2 전략 조합 시뮬레이션
    mix_simulator = StrategyMixSimulator(strategies)
    weights = {"Strategy_A": 0.6, "Strategy_B": 0.4}
    result = mix_simulator.simulate_mix(weights)
    result.plot(title="Mixed Strategy Cumulative Return", figsize=(10, 4))
    plt.show()

    # 29.3 이벤트 기반 전략 전환 시뮬레이션
    switcher = EventBasedSwitcher()
    switcher.add_trigger("VIX > 30", "Strategy_A", "Strategy_B")
    switcher.add_trigger("Interest Rate Hike", "Strategy_B", "Strategy_A")
    switcher.visualize_strategy_map()
    next_strategy = switcher.simulate_transition("Strategy_A", "VIX > 30")
    print("Transitioned Strategy:", next_strategy)