# module_24.py

import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


class InvestorPsychologyTracker:
    """
    24.1 사용자 행동 로그 & 판단 추적
    """

    def __init__(self):
        self.logs = []

    def record_action(self, action_type, strategy, market_condition, pnl, risk_change):
        self.logs.append({
            "timestamp": datetime.now(),
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
        사용자 행동의 편향 분석: 과신도, 손실 회피 경향 등 수치화
        """
        df = self.get_behavior_df()
        if df.empty:
            return {"message": "로그가 없습니다."}

        overconfidence = (df[df["pnl"] > 0]["action_type"] == "추가매수").mean()
        loss_aversion = (df[df["pnl"] < 0]["action_type"] == "매도").mean()
        high_frequency = df["timestamp"].diff().mean().total_seconds()

        return {
            "과신도": round(overconfidence * 100, 2),
            "손실 회피 경향": round(loss_aversion * 100, 2),
            "행동 빈도성": round(86400 / high_frequency, 2) if high_frequency else 0
        }

    def generate_heatmap_matrix(self):
        """
        24.2 판단 히트맵: 성공/실패 판단 구간 구조화
        """
        df = self.get_behavior_df()
        if df.empty:
            return pd.DataFrame()

        df['date'] = df['timestamp'].dt.date
        df['correct_decision'] = df['pnl'] > 0
        heatmap = df.groupby(['date', 'strategy'])['correct_decision'].mean().unstack(fill_value=0)
        return heatmap


class PsychologicalReportGenerator:
    """
    24.2 성향 분류 및 피드백 카드 생성
    """

    def classify_investor_type(self, behavior_metrics):
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
        전략 변경 빈도 ↔ 수익률 간 상관 구조 분석
        """
        if df.empty:
            return "데이터 부족"

        df['date'] = df['timestamp'].dt.date
        change_counts = df.groupby('date')['strategy'].nunique()
        daily_pnl = df.groupby('date')['pnl'].sum()
        merged = pd.merge(change_counts, daily_pnl, left_index=True, right_index=True)
        corr = merged.corr().iloc[0, 1]

        return f"전략 변경 빈도와 수익률의 상관계수: {round(corr, 3)}"


class StrategyRecommendationEngine:
    """
    24.3 심리 기반 전략 제어 추천
    """

    def recommend_based_on_mistakes(self, df):
        if df.empty:
            return "추천 불가: 로그 없음"

        # 실수 패턴: 진입 직후 손실
        df['entry_loss'] = (df['pnl'] < 0) & (df['action_type'] == "진입")
        entry_loss_rate = df['entry_loss'].mean()

        if entry_loss_rate > 0.5:
            return "과도한 조기 진입 경향 → '분할매수 전략' 추천"
        elif (df['pnl'] > 0).mean() < 0.3:
            return "전략 신뢰도 낮음 → '저변동 자산 비중 확대' 추천"
        else:
            return "현재 전략 유지 가능"

    def ghost_investor_replay(self, df, days_ago=14):
        """
        고스트 투자자 기능: 2주 전 판단 재현
        """
        if df.empty:
            return pd.DataFrame()

        cutoff = datetime.now() - pd.Timedelta(days=days_ago)
        replay_df = df[df['timestamp'] < cutoff]
        return replay_df.tail(10)  # 최근 10건 재현