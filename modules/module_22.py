# module_22.py

import datetime
import numpy as np
import pandas as pd

class AutoExecutionEngine:
    """
    22.1 전략 실행 자동화 파이프라인
    """
    def __init__(self, auto_enabled=True):
        self.auto_enabled = auto_enabled
        self.last_rebalance = None
        self.rebalance_interval_days = 7

    def should_rebalance(self, today=None):
        today = today or datetime.date.today()
        if not self.auto_enabled:
            return False
        if self.last_rebalance is None:
            return True
        delta = (today - self.last_rebalance).days
        return delta >= self.rebalance_interval_days

    def execute_rebalance(self, portfolio, strategy):
        if not self.auto_enabled:
            return portfolio
        self.last_rebalance = datetime.date.today()
        return strategy.rebalance(portfolio)  # 가정: strategy 객체가 .rebalance() 함수 보유


class RiskHedgingTrigger:
    """
    22.2 리스크 기반 회피 전략 트리거링
    """
    def __init__(self, vix_threshold=25, kospi_drop_pct=-3.0, mdd_limit=-12.0):
        self.vix_threshold = vix_threshold
        self.kospi_drop_pct = kospi_drop_pct
        self.mdd_limit = mdd_limit

    def check_trigger(self, vix_value, kospi_change_pct, expected_mdd):
        if vix_value >= self.vix_threshold:
            return "VIX 급등 감지 → 비상 전략 실행"
        if kospi_change_pct <= self.kospi_drop_pct:
            return "KOSPI 급락 감지 → 안전자산 전환"
        if expected_mdd <= self.mdd_limit:
            return f"MDD 예상 {expected_mdd}% → 전략 중단 필요"
        return None

    def emergency_assets(self):
        return {
            "cash": 0.4,
            "gold_etf": 0.3,
            "usd_etf": 0.3
        }


class StrategyTrustMonitor:
    """
    22.3 자동화 전략 신뢰도 피드백 시스템
    """
    def __init__(self):
        self.history = []

    def record(self, predicted_return, actual_return):
        error = actual_return - predicted_return
        self.history.append({
            "pred": predicted_return,
            "actual": actual_return,
            "error": error,
            "abs_error": abs(error)
        })

    def trust_report(self):
        df = pd.DataFrame(self.history)
        if df.empty:
            return "신뢰도 기록 없음"

        df["error_pct"] = df["abs_error"] / (df["pred"].replace(0, 1e-6)) * 100
        avg_error = df["error_pct"].mean()
        if avg_error > 20:
            return f"예측 실패율 {avg_error:.1f}% → 전략 재검토 필요"
        elif avg_error > 10:
            return f"예측 정확도 저하 ({avg_error:.1f}%) → 전략 조정 권장"
        else:
            return f"예측 성능 양호 (오차 {avg_error:.1f}%)"


# 🔄 전체 실행 함수 예시
def run_module_22(
    auto_engine, 
    portfolio, 
    strategy, 
    vix, 
    kospi_pct, 
    expected_mdd, 
    predicted_return, 
    actual_return,
    override_auto=False
):
    report = {}
    
    # 1. 리스크 회피 조건 점검
    hedger = RiskHedgingTrigger()
    risk_msg = hedger.check_trigger(vix, kospi_pct, expected_mdd)
    if risk_msg:
        report["emergency"] = risk_msg
        report["emergency_assets"] = hedger.emergency_assets()
        return report

    # 2. 전략 리밸런싱 조건 점검
    if auto_engine.auto_enabled or override_auto:
        if auto_engine.should_rebalance():
            portfolio = auto_engine.execute_rebalance(portfolio, strategy)
            report["rebalance"] = "자동 전략 리밸런싱 실행됨"
        else:
            report["rebalance"] = "아직 리밸런싱 조건 도달 전"
    else:
        report["rebalance"] = "자동 실행 비활성화 상태"

    # 3. 전략 신뢰도 추적
    monitor = StrategyTrustMonitor()
    monitor.record(predicted_return, actual_return)
    report["trust_feedback"] = monitor.trust_report()

    return report