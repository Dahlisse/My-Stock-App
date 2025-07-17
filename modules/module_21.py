import pandas as pd
import matplotlib.pyplot as plt
import uuid
from typing import Dict, List


class StrategyRouter:
    """
    21.1 예측 결과 → 전략 구조 자동 연동
    예측된 상승 확률에 따라 전략을 자동 라우팅한다.
    """

    def __init__(self, strategy_config: Dict[str, Dict[str, float]]):
        """
        strategy_config 예시:
        {
            "conservative": {"threshold": 0.4},
            "neutral": {"threshold": 0.6},
            "aggressive": {"threshold": 1.0}
        }
        """
        self.strategy_config = strategy_config

    def route(self, prediction_prob: float) -> str:
        """
        예측 확률 기반 전략 선택
        """
        for strategy, config in self.strategy_config.items():
            if prediction_prob <= config["threshold"]:
                return strategy
        return "aggressive"  # fallback


class UserControlInterface:
    """
    21.2 사용자 개입 조정 인터페이스
    사용자 성향에 따라 전략 가중치를 조정한다.
    """

    def __init__(self, user_preference: str = 'neutral'):
        assert user_preference in ['conservative', 'neutral', 'aggressive'], \
            "user_preference must be one of ['conservative', 'neutral', 'aggressive']"
        self.user_preference = user_preference

    def adjust_strategy_weight(self, base_weights: Dict[str, float]) -> Dict[str, float]:
        """
        사용자 성향 기반 전략 비중 조정
        """
        adjusted = base_weights.copy()
        if self.user_preference == "conservative":
            adjusted['conservative'] *= 1.3
            adjusted['aggressive'] *= 0.7
        elif self.user_preference == "aggressive":
            adjusted['aggressive'] *= 1.3
            adjusted['conservative'] *= 0.7

        total = sum(adjusted.values())
        return {k: round(v / total, 3) for k, v in adjusted.items()}


class StrategyFlowTracker:
    """
    21.3 전략 흐름 시각 내비게이션
    전략 전환 이력을 기록하고 시각화할 수 있다.
    """

    def __init__(self):
        self.flow_history: List[Dict] = []

    def record_transition(self, strategy_name: str, predicted_prob: float, confidence_level: float):
        self.flow_history.append({
            "id": str(uuid.uuid4())[:6],
            "strategy": strategy_name,
            "prob": predicted_prob,
            "confidence": confidence_level
        })

    def plot_timeline(self):
        if not self.flow_history:
            print("⚠️ 기록된 전략 이력이 없습니다.")
            return

        timeline = pd.DataFrame(self.flow_history)
        timeline["step"] = range(1, len(timeline) + 1)

        plt.figure(figsize=(12, 4))
        plt.plot(timeline["step"], timeline["prob"], marker='o', label="예측 확률", color="tab:blue")

        for i, row in timeline.iterrows():
            plt.text(row["step"], row["prob"], row["strategy"], fontsize=9, ha='center')

        plt.xlabel("전략 변경 단계")
        plt.ylabel("예측 상승 확률")
        plt.title("전략 흐름 타임라인")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def explain_flow(self) -> List[str]:
        result = []
        for record in self.flow_history:
            summary = f"전략 {record['strategy']} (예측 상승확률 {record['prob']:.2f}, 신뢰도 {record['confidence']:.2f})"
            result.append(summary)
        return result


# 🔄 전체 파이프라인 실행 함수
def run_module_21(predicted_prob: float,
                  confidence_score: float,
                  user_type: str = 'neutral') -> Dict:
    """
    predicted_prob: float (예: 0.65)
    confidence_score: float (예: 0.78)
    user_type: 'conservative', 'neutral', 'aggressive'
    """
    # 1. 전략 라우팅 기준 정의
    strategy_thresholds = {
        "conservative": {"threshold": 0.4},
        "neutral": {"threshold": 0.6},
        "aggressive": {"threshold": 1.0}
    }

    # 2. 전략 자동 선택
    router = StrategyRouter(strategy_thresholds)
    selected_strategy = router.route(predicted_prob)

    # 3. 사용자 조정 적용
    base_weights = {"conservative": 0.3, "neutral": 0.4, "aggressive": 0.3}
    control = UserControlInterface(user_type)
    adjusted_weights = control.adjust_strategy_weight(base_weights)

    # 4. 전략 흐름 기록
    tracker = StrategyFlowTracker()
    tracker.record_transition(selected_strategy, predicted_prob, confidence_score)

    # 5. 결과 리턴
    return {
        "selected_strategy": selected_strategy,
        "adjusted_weights": adjusted_weights,
        "explanation": tracker.explain_flow(),
        "flow_tracker": tracker
    }