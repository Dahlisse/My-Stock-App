# module_21.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import uuid

class StrategyRouter:
    """
    21.1 예측 결과 → 전략 구조 자동 연동
    """
    def __init__(self, strategy_config):
        """
        strategy_config: dict
            예시:
            {
                "conservative": {"threshold": 0.3},
                "neutral": {"threshold": 0.5},
                "aggressive": {"threshold": 0.7}
            }
        """
        self.strategy_config = strategy_config

    def route(self, prediction_prob):
        """
        prediction_prob: float (예: 예측된 상승 확률)

        Returns:
            추천 전략 이름
        """
        for strategy, config in self.strategy_config.items():
            if prediction_prob <= config["threshold"]:
                return strategy
        return "aggressive"


class UserControlInterface:
    """
    21.2 사용자 개입 조정 인터페이스
    """
    def __init__(self, user_preference='neutral'):
        self.user_preference = user_preference  # conservative, neutral, aggressive

    def adjust_strategy_weight(self, base_weights):
        """
        base_weights: dict[strategy] = float

        Returns:
            조정된 strategy weights
        """
        if self.user_preference == "conservative":
            base_weights['conservative'] *= 1.3
            base_weights['aggressive'] *= 0.7
        elif self.user_preference == "aggressive":
            base_weights['aggressive'] *= 1.3
            base_weights['conservative'] *= 0.7
        total = sum(base_weights.values())
        return {k: round(v/total, 3) for k, v in base_weights.items()}


class StrategyFlowTracker:
    """
    21.3 전략 흐름 시각 내비게이션
    """
    def __init__(self):
        self.flow_history = []

    def record_transition(self, strategy_name, predicted_prob, confidence_level):
        self.flow_history.append({
            "id": str(uuid.uuid4())[:6],
            "strategy": strategy_name,
            "prob": predicted_prob,
            "confidence": confidence_level
        })

    def plot_timeline(self):
        if not self.flow_history:
            print("기록된 전략 이력이 없습니다.")
            return

        timeline = pd.DataFrame(self.flow_history)
        timeline["step"] = range(1, len(timeline)+1)

        plt.figure(figsize=(12, 4))
        plt.plot(timeline["step"], timeline["prob"], marker='o', label="예측 확률")
        for i, row in timeline.iterrows():
            plt.text(row["step"], row["prob"], row["strategy"], fontsize=9, ha='center')
        plt.xlabel("전략 변경 단계")
        plt.ylabel("예측 상승 확률")
        plt.title("전략 흐름 타임라인")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def explain_flow(self):
        result = []
        for record in self.flow_history:
            summary = f"전략 {record['strategy']} (예측 상승확률 {record['prob']:.2f}, 신뢰도 {record['confidence']})"
            result.append(summary)
        return result


# 🔄 전체 파이프라인 실행 함수
def run_module_21(predicted_prob, confidence_score, user_type='neutral'):
    """
    predicted_prob: float (예: 예측된 상승 확률)
    confidence_score: float (0~1 예측 신뢰도)
    user_type: 'conservative', 'neutral', 'aggressive'
    """
    # 전략 기준 설정
    strategy_thresholds = {
        "conservative": {"threshold": 0.4},
        "neutral": {"threshold": 0.6},
        "aggressive": {"threshold": 1.0}
    }

    # 전략 선택
    router = StrategyRouter(strategy_thresholds)
    strategy_selected = router.route(predicted_prob)

    # 사용자 조정 가중치 반영
    base_weights = {"conservative": 0.3, "neutral": 0.4, "aggressive": 0.3}
    control = UserControlInterface(user_type)
    adjusted_weights = control.adjust_strategy_weight(base_weights)

    # 전략 흐름 기록
    tracker = StrategyFlowTracker()
    tracker.record_transition(strategy_selected, predicted_prob, confidence_score)

    return {
        "selected_strategy": strategy_selected,
        "adjusted_weights": adjusted_weights,
        "explanation": tracker.explain_flow(),
        "flow_tracker": tracker
    }