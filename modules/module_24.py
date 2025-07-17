import pandas as pd
import numpy as np
from datetime import datetime


class InvestorPsychologyTracker:
    """
    24.1 사용자 행동 로그 & 판단 추적 시스템
    """

    def __init__(self):
        self.logs = []

    def record_action(self, action_type, strategy, market_condition, pnl, risk_change):
        """
        사용자 행동 기록
        """
        self.logs.append({
            "timestamp": pd.Timestamp.now(),
            "action_type": action_type,
            "strategy": strategy,
            "market_condition": market_condition,
            "pnl": pnl,
            "risk_change": risk_change
        })

    def get_behavior_df(self):
        return pd.DataFrame(self.logs)

    def analyze_behavioral_bias(self):
        """
        행동 편향 분석 (과신도, 손실 회피 성향, 빈도성)
        """
        df = self.get_behavior_df()
        if df.empty or len(df) < 2:
            return {"message": "로그가 부족합니다."}

        overconfidence = ((df["pnl"] > 0) & (df["action_type"] == "추가매수")).mean()
        loss_aversion = ((df["pnl"] < 0) & (df["action_type"] == "매도")).mean()

        df_sorted = df.sort_values("timestamp")
        time_diffs = df_sorted["timestamp"].diff().dropna()
        high_frequency = time_diffs.mean().total_seconds() if not time_diffs.empty else np.nan

        return {
            "과신도": round(overconfidence * 100, 2),
            "손실 회피 경향": round(loss_aversion * 100, 2),
            "행동 빈도성": round(86400 / high_frequency, 2) if high_frequency and high_frequency > 0 else 0
        }

    def generate_heatmap_matrix(self):
        """
        판단 성공/실패 히트맵 생성
        """
        df = self.get_behavior_df()
        if df.empty:
            return pd.DataFrame()

        df = df.copy()
        df["date"] = df["timestamp"].dt.date
        df["correct_decision"] = df["pnl"] > 0

        heatmap = df.groupby(["date", "strategy"])["correct_decision"].mean().unstack(fill_value=0)
        return heatmap


class PsychologicalReportGenerator:
    """
    24.2 투자자 성향 분류 및 피드백 카드 생성
    """

    def classify_investor_type(self, behavior_metrics):
        """
        과신도, 손실 회피 경향, 행동 빈도성 기반 분류
        """
        oc = behavior_metrics.get("과신도", 0)
        la = behavior_metrics.get("손실 회피 경향", 0)
        freq = behavior_metrics.get("행동 빈도성", 0)

        if oc > 70 and freq > 5:
            return "짐 사이먼스형 (공격적 + 고빈도)"
        elif la > 70:
            return "변동성 회피형 (보수적 + 손실 회피)"
        elif freq < 2:
            return "워렌 버핏형 (저빈도 + 장기 보유)"
        else:
            return "중립형 투자자"

    def correlation_analysis(self, df):
        """
        전략 변경 ↔ 수익률 상관 분석
        """
        if df.empty:
            return "데이터 부족"

        df = df.copy()
        df["date"] = df["timestamp"].dt.date
        change_counts = df.groupby("date")["strategy"].nunique()
        daily_pnl = df.groupby("date")["pnl"].sum()

        merged = pd.DataFrame({
            "change_counts": change_counts,
            "daily_pnl": daily_pnl
        }).dropna()

        if merged.empty or merged.shape[0] < 2:
            return "상관 분석 불가: 데이터 부족"

        corr = merged.corr().iloc[0, 1]
        return f"전략 변경 빈도와 수익률의 상관계수: {round(corr, 3)}"


class StrategyRecommendationEngine:
    """
    24.3 실수 패턴 기반 전략 제어 추천
    """

    def recommend_based_on_mistakes(self, df):
        """
        실수 경향 분석 → 전략 추천
        """
        if df.empty:
            return "추천 불가: 로그 없음"

        df = df.copy()
        df["entry_loss"] = (df["pnl"] < 0) & (df["action_type"] == "진입")
        entry_loss_rate = df["entry_loss"].mean()

        if entry_loss_rate > 0.5:
            return "과도한 조기 진입 경향 → '분할매수 전략' 추천"
        elif (df["pnl"] > 0).mean() < 0.3:
            return "전략 신뢰도 낮음 → '저변동 자산 비중 확대' 추천"
        else:
            return "현재 전략 유지 가능"

    def ghost_investor_replay(self, df, days_ago=14):
        """
        과거 판단 재현 기능 (2주 전 기준)
        """
        if df.empty:
            return pd.DataFrame()

        cutoff = pd.Timestamp.now() - pd.Timedelta(days=days_ago)
        replay_df = df[df["timestamp"] < cutoff]
        return replay_df.tail(10)