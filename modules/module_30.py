import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score
from typing import List, Dict, Any
from io import BytesIO

class MetaCognitionAnalyzer:
    """
    투자자 메타인지 분석 클래스
    """

    def __init__(self, judgment_logs: pd.DataFrame):
        self.judgment_logs = judgment_logs.copy()

    def correlate_emotion_to_result(self) -> Dict[str, float]:
        corr_emotion_outcome = self.judgment_logs['emotion_score'].corr(self.judgment_logs['outcome'])
        corr_indicator_outcome = self.judgment_logs['indicator_score'].corr(self.judgment_logs['outcome'])
        corr_emotion_indicator = self.judgment_logs['emotion_score'].corr(self.judgment_logs['indicator_score'])

        return {
            "emotion_vs_outcome": round(corr_emotion_outcome, 4) if not np.isnan(corr_emotion_outcome) else 0.0,
            "indicator_vs_outcome": round(corr_indicator_outcome, 4) if not np.isnan(corr_indicator_outcome) else 0.0,
            "emotion_vs_indicator": round(corr_emotion_indicator, 4) if not np.isnan(corr_emotion_indicator) else 0.0
        }

    def classify_cognitive_bias(self) -> Dict[str, float]:
        logs = self.judgment_logs.copy()
        n = len(logs)

        if n < 2:
            return {
                "overconfidence": 0.0,
                "avoidance": 0.0,
                "short_term_fixation": 0.0,
                "uncertainty_avoidance": 0.0
            }

        # 과신도: 감정 점수와 결과가 음의 상관일수록 높음
        corr = logs['emotion_score'].corr(logs['outcome'])
        overconfidence_score = max(0, 1 - corr) if not np.isnan(corr) else 0.0

        # 회피성: 부정 감정(-0.5 이하) 비율
        avoidance_score = logs[logs['emotion_score'] < -0.5].shape[0] / n

        # 단기집착: 판단 간격이 1시간 미만인 비율
        logs['interval'] = logs['timestamp'].diff().dt.total_seconds()
        short_term_fixation = logs['interval'].lt(3600).sum() / max(n - 1, 1)

        # 불확실성 회피: 낮은 지표 점수(0.3 이하)일 때 decision_quality 평균
        low_conf = logs[logs['indicator_score'] < 0.3]
        uncertainty_avoid