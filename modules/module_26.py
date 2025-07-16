# module_26.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class NonActionZoneDetector:
    """
    26.1 비매매(Non-Action) 판단 구조 설계
    """

    def __init__(self, threshold_volatility=0.25, threshold_condition=0.6, threshold_accuracy=0.55):
        self.threshold_volatility = threshold_volatility
        self.threshold_condition = threshold_condition
        self.threshold_accuracy = threshold_accuracy

    def evaluate_market(self, vix, strategy_condition_score, prediction_accuracy):
        """
        전략 조건 충족률 + 시장 위험 + 예측 정확도 기반 매매 보류 판단
        """
        result = {}
        result['VIX'] = vix
        result['ConditionScore'] = strategy_condition_score
        result['PredictionAccuracy'] = prediction_accuracy

        if vix > self.threshold_volatility and strategy_condition_score < self.threshold_condition:
            result['advice'] = "❌ 시장 변동성↑ + 조건 불충분 → 매매 보류 권고"
        elif prediction_accuracy < self.threshold_accuracy:
            result['advice'] = "⚠️ 예측 정확도 낮음 → 진입 신중 권고"
        else:
            result['advice'] = "✅ 매매 가능 구간"
        return result

    def is_non_action_zone(self, result_dict):
        return "보류" in result_dict.get("advice", "")


class OpportunityZoneDetector:
    """
    26.2 기회 밀집 구간 탐지 시스템
    """

    def __init__(self):
        self.past_patterns = []

    def register_success_pattern(self, macro, tech, sentiment):
        """
        과거 성공 전략 패턴 등록
        """
        self.past_patterns.append({
            "macro": macro,
            "tech": tech,
            "sentiment": sentiment
        })

    def match_current_conditions(self, macro, tech, sentiment):
        """
        현재 조건이 과거 성공 패턴과 얼마나 유사한지 평가 (0~1)
        """
        scores = []
        for pattern in self.past_patterns:
            m_sim = 1 - abs(macro - pattern["macro"])
            t_sim = 1 - abs(tech - pattern["tech"])
            s_sim = 1 - abs(sentiment - pattern["sentiment"])
            scores.append((m_sim + t_sim + s_sim) / 3)

        if not scores:
            return 0.0
        return round(np.mean(scores), 3)

    def advise_opportunity(self, score, threshold=0.85):
        if score > threshold:
            return f"🎯 기회 밀집 스코어 {score} → 집중 매매 전략 실행 권장"
        else:
            return f"📉 기회 스코어 {score} → 보수적 접근 권장"


class StrategyAutoControl:
    """
    26.3 자동 전환 & 대기 상태 진입 시스템
    """

    def __init__(self):
        self.state = "ACTIVE"
        self.last_suspend_date = None

    def check_auto_suspend(self, vix, trust_score, vix_threshold=30, trust_threshold=0.4):
        """
        VIX 급등 또는 전략 신뢰도 저하 시 자동 중단
        """
        if vix > vix_threshold or trust_score < trust_threshold:
            self.state = "SUSPENDED"
            self.last_suspend_date = datetime.now().date()
            return f"⚠️ 자동 매매 중단 → 조건 충족 시 재개 예정"
        return "✅ 전략 유지"

    def get_resume_forecast(self, expected_days=3, recovery_prob=0.62):
        """
        재개 가능 시점 및 확률 안내
        """
        if self.state == "SUSPENDED" and self.last_suspend_date:
            resume_date = self.last_suspend_date + timedelta(days=expected_days)
            return f"현재는 비매매 구간입니다. 진입 가능성은 {expected_days}일 후 {int(recovery_prob * 100)}%"
        return "전략은 현재 정상 작동 중입니다."