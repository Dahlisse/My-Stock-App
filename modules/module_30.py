# module_30.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score
from typing import List, Dict, Any

class MetaCognitionAnalyzer:
    """
    투자자 메타인지 분석 클래스
    - 판단 시점 감정, 지표, 성과 간 상관관계 분석
    - 판단 오류 유형 분류 (과신형, 회피형, 단기집착형, 불확실성 회피형 등)
    - 메타인지 리포트 생성
    """

    def __init__(self, judgment_logs: pd.DataFrame):
        """
        judgment_logs: DataFrame with columns
          - timestamp, emotion_score, indicator_score, outcome, decision_quality 등
        """
        self.judgment_logs = judgment_logs

    def correlate_emotion_to_result(self) -> Dict[str, float]:
        corr_emotion_outcome = self.judgment_logs['emotion_score'].corr(self.judgment_logs['outcome'])
        corr_indicator_outcome = self.judgment_logs['indicator_score'].corr(self.judgment_logs['outcome'])
        corr_emotion_indicator = self.judgment_logs['emotion_score'].corr(self.judgment_logs['indicator_score'])

        return {
            "emotion_vs_outcome": corr_emotion_outcome,
            "indicator_vs_outcome": corr_indicator_outcome,
            "emotion_vs_indicator": corr_emotion_indicator
        }

    def classify_cognitive_bias(self) -> Dict[str, float]:
        """
        단순 예시: 판단 편향 점수 산출 (0~1 scale)
        - 과신도: emotion_score와 실제 성과의 부정적 상관관계 시 높음
        - 회피성: 높은 부정 감정 빈도 비율
        - 단기집착: 단기간 내 판단 빈도수 과다
        - 불확실성 회피: 낮은 지표 점수 시 행동 회피 비율
        """
        logs = self.judgment_logs

        overconfidence_score = max(0, 1 - logs['emotion_score'].corr(logs['outcome']))  # 역상관일수록 과신
        avoidance_score = logs[logs['emotion_score'] < -0.5].shape[0] / len(logs)  # 부정감정 비율
        short_term_fixation = logs['timestamp'].diff().dt.total_seconds().lt(3600).mean()  # 1시간 내 연속 판단 비율
        uncertainty_avoidance = logs[logs['indicator_score'] < 0.3]['decision_quality'].mean()  # 낮은 지표 때 낮은 결정 질

        return {
            "overconfidence": round(overconfidence_score, 3),
            "avoidance": round(avoidance_score, 3),
            "short_term_fixation": round(short_term_fixation, 3),
            "uncertainty_avoidance": round(uncertainty_avoidance, 3)
        }

    def generate_meta_report(self) -> Dict[str, Any]:
        correlations = self.correlate_emotion_to_result()
        biases = self.classify_cognitive_bias()

        report = {
            "summary": "투자 판단의 감정과 결과 간 상관관계 분석 및 인지 편향 진단 결과입니다.",
            "correlations": correlations,
            "cognitive_bias_scores": biases,
            "interpretation": []
        }

        # 해석 예시
        if correlations['emotion_vs_outcome'] < 0:
            report["interpretation"].append("감정 점수가 높을수록 실제 성과가 저조한 경향이 있습니다. 감정 통제 강화가 필요합니다.")
        else:
            report["interpretation"].append("감정 점수가 성과에 긍정적 영향을 미치고 있습니다.")

        if biases['overconfidence'] > 0.5:
            report["interpretation"].append("과신 성향이 높아 손실 위험에 노출될 수 있습니다.")
        if biases['avoidance'] > 0.3:
            report["interpretation"].append("회피 성향이 높아 기회 포착이 어려울 수 있습니다.")

        return report


class GrowthTracker:
    """
    투자자 성장 지수 및 트래커
    - 판단 일관성, 전략 유지력, 감정 통제력 등 지표 시계열 추적
    - 성장 곡선 시각화 제공
    """

    def __init__(self, behavior_logs: pd.DataFrame):
        """
        behavior_logs: DataFrame with columns
          - timestamp, consistency_score, strategy_adherence, emotion_control 등
        """
        self.behavior_logs = behavior_logs

    def latest_growth_metrics(self) -> Dict[str, float]:
        latest = self.behavior_logs.iloc[-1]
        return {
            "judgment_consistency": latest['consistency_score'],
            "strategy_maintenance": latest['strategy_adherence'],
            "emotion_control": latest['emotion_control']
        }

    def plot_growth_curve(self):
        plt.figure(figsize=(10, 5))
        plt.plot(self.behavior_logs['timestamp'], self.behavior_logs['consistency_score'], label='Judgment Consistency')
        plt.plot(self.behavior_logs['timestamp'], self.behavior_logs['strategy_adherence'], label='Strategy Maintenance')
        plt.plot(self.behavior_logs['timestamp'], self.behavior_logs['emotion_control'], label='Emotion Control')
        plt.title('투자자 성장 지수 추이')
        plt.xlabel('시간')
        plt.ylabel('지수')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        return plt


class SelfLearningLoop:
    """
    투자자 자기주도 퀀트 메타학습 루프
    - 전략 개선 추천
    - 투자 철학 자동 생성 및 카드화
    """

    def __init__(self, strategy_loops: List[Dict[str, Any]], user_profile: Dict[str, Any]):
        self.strategy_loops = strategy_loops
        self.user_profile = user_profile

    def recommend_improvement(self) -> Dict[str, Any]:
        improvements = []
        for loop in self.strategy_loops:
            if loop['success_rate'] < 0.6:
                improvements.append({
                    "strategy": loop['strategy_name'],
                    "recommendation": "진입 조건 완화 권장",
                    "expected_gain": "+2.1%"
                })
            elif loop['drawdown'] > 0.15:
                improvements.append({
                    "strategy": loop['strategy_name'],
                    "recommendation": "손절 기준 강화 권장",
                    "expected_gain": "리스크 감소"
                })
        return {"improvements": improvements}

    def create_strategy_philosophy(self) -> str:
        profile = self.user_profile
        if profile.get("risk_tolerance", "medium") == "low":
            return "보수형 투자자: 리스크 최소화 및 안정적 수익 우선"
        elif profile.get("risk_tolerance") == "high":
            return "공격형 투자자: 높은 수익률 추구, 변동성 감수"
        else:
            return "중립형 투자자: 균형 잡힌 성장과 안정성 추구"

    def cardify_philosophy(self) -> Dict[str, Any]:
        philosophy = self.create_strategy_philosophy()
        card = {
            "title": "투자자 전략 철학",
            "content": philosophy,
            "recommendations": self.recommend_improvement()['improvements']
        }
        return card


def run_meta_learning_module(judgment_logs: pd.DataFrame, behavior_logs: pd.DataFrame, strategy_loops: List[Dict[str, Any]], user_profile: Dict[str, Any]) -> Dict[str, Any]:
    meta_analyzer = MetaCognitionAnalyzer(judgment_logs)
    growth_tracker = GrowthTracker(behavior_logs)
    self_learning = SelfLearningLoop(strategy_loops, user_profile)

    meta_report = meta_analyzer.generate_meta_report()
    latest_growth = growth_tracker.latest_growth_metrics()
    growth_fig = growth_tracker.plot_growth_curve()
    recommendations = self_learning.recommend_improvement()
    philosophy_card = self_learning.cardify_philosophy()

    return {
        "meta_report": meta_report,
        "latest_growth": latest_growth,
        "growth_figure": growth_fig,
        "recommendations": recommendations,
        "strategy_philosophy_card": philosophy_card
    }