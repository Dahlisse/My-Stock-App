import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class InvestmentRoutinePlanner:
    """
    27.1 일일/주간 루틴 설계 템플릿 제공
    """

    def __init__(self, profile: dict):
        # 기본값 제공
        default_profile = {'성향': '중립형', '리밸런싱주기': '월간', '가용시간': '15분'}
        self.profile = {**default_profile, **profile}

    def suggest_routine(self) -> dict:
        """
        사용자 성향 기반 전략 루틴 자동 제안
        """
        suggestions = []

        if self.profile.get('리밸런싱주기') == '주간':
            suggestions.append("📆 매주 수요일 오전 9시: 전략 리밸런싱 검토")

        if self.profile.get('가용시간') == '30분':
            suggestions.append("⏱️ 매일 오전 8시 30분: 시장 점검 (뉴스/선물/VIX)")

        if self.profile.get('성향') == '보수형':
            suggestions.append("🔍 매주 금요일 오후 6시: 감정 점검 + 포트 리뷰")

        routine_structure = [
            "1️⃣ 시장 점검",
            "2️⃣ 전략 진단",
            "3️⃣ 감정 점검",
            "4️⃣ 포트 점검"
        ]

        return {
            "루틴 제안": suggestions,
            "루틴 구성": routine_structure
        }


class HabitEvaluator:
    """
    27.2 투자 습관 리포트 & 루틴 성실도 평가
    """

    def __init__(self, log_df: pd.DataFrame):
        """
        log_df: 실제 행동 로그 데이터
        columns: ['date', 'action_type', 'strategy_changed', 'daily_reviewed', 'gain_loss']
        """
        required_columns = {'date', 'action_type', 'strategy_changed', 'daily_reviewed', 'gain_loss'}
        if not required_columns.issubset(set(log_df.columns)):
            raise ValueError(f"log_df에는 다음 컬럼들이 필요합니다: {required_columns}")
        self.log_df = log_df.copy()

    def evaluate_consistency(self) -> float:
        """
        전략 유지율 계산 (1 - 전략 변경 비율)
        """
        total_days = len(self.log_df)
        if total_days == 0:
            return 0.0

        changes = self.log_df['strategy_changed'].sum()
        maintenance_ratio = 1 - (changes / total_days)
        return round(maintenance_ratio, 3)

    def detect_behavior_drift(self) -> float:
        """
        수익 대비 행동 일치율 (corr)
        """
        try:
            correlation = self.log_df['daily_reviewed'].corr(self.log_df['gain_loss'])
            return round(correlation, 3) if not np.isnan(correlation) else 0.0
        except Exception:
            return 0.0

    def generate_report(self) -> list:
        """
        루틴 평가 리포트 (텍스트 리스트 형태)
        """
        strategy_maintenance = self.evaluate_consistency()
        behavior_correlation = self.detect_behavior_drift()

        report = []
        report.append(f"📊 전략 유지율: {strategy_maintenance * 100:.1f}%")
        if strategy_maintenance < 0.7:
            report.append("⚠️ 전략 변경 빈도 높음 → 감정 투자 우려")

        report.append(f"📈 행동 vs 성과 상관도: {behavior_correlation}")
        if behavior_correlation < 0.3:
            report.append("⚠️ 루틴과 성과 간 일치도 낮음 → 점검 필요")

        return report


class GrowthCoach:
    """
    27.3 성장 챌린지 & 자기 피드백 코치 시스템
    """

    def __init__(self, diary_logs: list):
        """
        diary_logs: 투자 감정일지 로그 (list of dict)
        Example: [{'date': '2025-07-01', 'emotion': '불안', 'entry': '급락에 당황...'}, ...]
        """
        if not isinstance(diary_logs, list):
            raise ValueError("diary_logs는 리스트 형태여야 합니다.")
        self.diary_logs = diary_logs

    def suggest_challenges(self) -> list:
        """
        성장 챌린지 제안
        """
        return [
            "🎯 30일 연속 전략 유지",
            "🧠 감정 기록 20회 이상 달성",
            "📒 리밸런싱 주기 지키기"
        ]

    def generate_feedback(self) -> list:
        """
        감정-성과 간 행동 차이 분석
        """
        tips = []
        for log in self.diary_logs:
            entry = log.get('entry', '')
            emotion = log.get('emotion', '')

            if "급등 따라잡기" in entry:
                tips.append("📌 과열 시 조급 진입은 수익률 저하로 이어질 수 있습니다.")
            if emotion == "불안":
                tips.append("🧘 감정이 격해질 때는 진입보다 관망을 고려해보세요.")

        if not tips:
            tips.append("✅ 감정 일지에서 특별한 이상은 감지되지 않았습니다.")

        return tips