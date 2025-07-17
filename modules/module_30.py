import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score
from typing import List, Dict, Any
from io import BytesIO
import base64


class MetaCognitionAnalyzer:
    def __init__(self, judgment_logs: pd.DataFrame):
        self.logs = judgment_logs.copy()

    def correlate_emotion_to_result(self) -> Dict[str, float]:
        try:
            emo_vs_out = self.logs['emotion_score'].corr(self.logs['outcome'])
        except Exception:
            emo_vs_out = np.nan

        try:
            ind_vs_out = self.logs['indicator_score'].corr(self.logs['outcome'])
        except Exception:
            ind_vs_out = np.nan

        try:
            emo_vs_ind = self.logs['emotion_score'].corr(self.logs['indicator_score'])
        except Exception:
            emo_vs_ind = np.nan

        return {
            "emotion_vs_outcome": emo_vs_out,
            "indicator_vs_outcome": ind_vs_out,
            "emotion_vs_indicator": emo_vs_ind
        }

    def classify_cognitive_bias(self) -> Dict[str, float]:
        logs = self.logs
        total = len(logs)

        try:
            overconfidence = max(0.0, 1.0 - logs['emotion_score'].corr(logs['outcome']))
        except Exception:
            overconfidence = 0.0

        avoidance = logs[logs['emotion_score'] < -0.5].shape[0] / max(1, total)

        try:
            short_term_fix = logs['timestamp'].diff().dt.total_seconds().lt(3600).mean()
        except Exception:
            short_term_fix = 0.0

        try:
            filt = logs[logs['indicator_score'] < 0.3]
            uncertainty_avoid = filt['decision_quality'].mean() if not filt.empty else 0.0
        except Exception:
            uncertainty_avoid = 0.0

        return {
            "overconfidence": round(overconfidence, 3),
            "avoidance": round(avoidance, 3),
            "short_term_fixation": round(short_term_fix, 3),
            "uncertainty_avoidance": round(uncertainty_avoid, 3)
        }

    def generate_meta_report(self) -> Dict[str, Any]:
        corr = self.correlate_emotion_to_result()
        bias = self.classify_cognitive_bias()

        interpretation = []
        if corr.get('emotion_vs_outcome', 0) < 0:
            interpretation.append("감정 점수가 높을수록 성과가 낮은 경향이 있습니다.")
        else:
            interpretation.append("감정 점수가 성과에 긍정적인 영향을 주고 있습니다.")

        if bias['overconfidence'] > 0.5:
            interpretation.append("과신 경향이 높아 주의가 필요합니다.")
        if bias['avoidance'] > 0.3:
            interpretation.append("회피 성향이 뚜렷해 기회 손실 가능성이 있습니다.")

        return {
            "summary": "감정/지표/성과의 상관관계 및 인지 편향 진단",
            "correlations": corr,
            "bias_scores": bias,
            "insights": interpretation
        }


class GrowthTracker:
    def __init__(self, behavior_logs: pd.DataFrame):
        self.logs = behavior_logs.copy()

    def latest_growth_metrics(self) -> Dict[str, float]:
        try:
            latest = self.logs.iloc[-1]
            return {
                "judgment_consistency": round(latest['consistency_score'], 3),
                "strategy_adherence": round(latest['strategy_adherence'], 3),
                "emotion_control": round(latest['emotion_control'], 3)
            }
        except Exception:
            return {
                "judgment_consistency": 0.0,
                "strategy_adherence": 0.0,
                "emotion_control": 0.0
            }

    def plot_growth_curve(self) -> str:
        try:
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(self.logs['timestamp'], self.logs['consistency_score'], label='일관성')
            ax.plot(self.logs['timestamp'], self.logs['strategy_adherence'], label='전략 유지력')
            ax.plot(self.logs['timestamp'], self.logs['emotion_control'], label='감정 통제력')

            ax.set_title("투자자 성장 지표")
            ax.legend()
            ax.grid(True)

            buf = BytesIO()
            plt.tight_layout()
            plt.savefig(buf, format='png')
            buf.seek(0)
            encoded = base64.b64encode(buf.read()).decode('utf-8')
            plt.close(fig)
            return f"data:image/png;base64,{encoded}"
        except Exception:
            return ""


class SelfLearningLoop:
    def __init__(self, strategy_loops: List[Dict[str, Any]], user_profile: Dict[str, Any]):
        self.loops = strategy_loops
        self.profile = user_profile

    def recommend_improvement(self) -> Dict[str, Any]:
        output = []
        for loop in self.loops:
            name = loop.get("strategy_name", "알 수 없음")
            sr = loop.get("success_rate", 1.0)
            dd = loop.get("drawdown", 0.0)

            if sr < 0.6:
                output.append({
                    "strategy": name,
                    "recommendation": "진입 조건 완화",
                    "expected_effect": "+2.1% 수익률"
                })
            if dd > 0.15:
                output.append({
                    "strategy": name,
                    "recommendation": "손절 기준 강화",
                    "expected_effect": "리스크 감소"
                })
        return {"recommendations": output}

    def cardify_philosophy(self) -> Dict[str, Any]:
        rt = self.profile.get("risk_tolerance", "medium")
        if rt == "low":
            desc = "보수형: 안정성과 리스크 관리 중시"
        elif rt == "high":
            desc = "공격형: 수익률 극대화, 변동성 감수"
        else:
            desc = "중립형: 수익과 안정의 균형 추구"

        return {
            "title": "투자자 철학 카드",
            "description": desc,
            "recommendations": self.recommend_improvement().get("recommendations", [])
        }


def run_meta_learning_module(
    judgment_logs: pd.DataFrame,
    behavior_logs: pd.DataFrame,
    strategy_loops: List[Dict[str, Any]],
    user_profile: Dict[str, Any]
) -> Dict[str, Any]:
    analyzer = MetaCognitionAnalyzer(judgment_logs)
    tracker = GrowthTracker(behavior_logs)
    loop = SelfLearningLoop(strategy_loops, user_profile)

    return {
        "meta_report": analyzer.generate_meta_report(),
        "growth_metrics": tracker.latest_growth_metrics(),
        "growth_curve_image": tracker.plot_growth_curve(),
        "recommendations": loop.recommend_improvement(),
        "philosophy_card": loop.cardify_philosophy()
    }