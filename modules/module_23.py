# ✅ module_23.py

import datetime
import pandas as pd


class AlertCondition:
    """
    23.1 조건 기반 알림 커스터마이징
    - 손실률과 변동성 기준으로 경고 메시지 생성
    """
    def __init__(self, loss_threshold=-5.0, volatility_threshold=3.0):
        self.loss_threshold = loss_threshold
        self.volatility_threshold = volatility_threshold
        self.alert_log = []

    def evaluate(self, return_pct: float, volatility: float):
        alerts = []
        if return_pct <= self.loss_threshold:
            alerts.append(f"📉 손실 경고: 수익률 {return_pct:.2f}%")
        if volatility >= self.volatility_threshold:
            alerts.append(f"⚠️ 변동성 경고: 변동성 {volatility:.2f}%")
        return alerts

    def log_alerts(self, alerts: list):
        timestamp = datetime.datetime.now().isoformat()
        for alert in alerts:
            self.alert_log.append({"time": timestamp, "message": alert})

    def get_alert_log(self) -> pd.DataFrame:
        return pd.DataFrame(self.alert_log)


class RiskDeviationDetector:
    """
    23.2 전략 리스크 감지 & 경고 시스템
    - 추적 오차, 손실 심화, 백테스트 괴리율에 기반한 위험 감지
    """
    def __init__(self):
        self.thresholds = {
            "tracking_error": 0.08,
            "drawdown_exceed": -15.0,
            "backtest_gap": -10.0
        }

    def check(self, tracking_error: float, drawdown_pct: float, backtest_diff: float) -> list:
        messages = []
        if tracking_error > self.thresholds["tracking_error"]:
            messages.append("⚠️ 전략 괴리율 급등 → 추적 오류 가능성")
        if drawdown_pct <= self.thresholds["drawdown_exceed"]:
            messages.append(f"❗누적 손실 {drawdown_pct:.2f}% → 전략 위험군 지정")
        if backtest_diff <= self.thresholds["backtest_gap"]:
            messages.append("📉 실전 수익률이 백테스트 대비 현저히 낮음")
        return messages


class NaturalLanguageNotifier:
    """
    23.3 사용자 언어 기반 요약 알림 시스템
    - 초심자 / 전문가 모드에 따라 요약 문구 출력
    """
    def __init__(self, mode: str = "초심자"):
        self.mode = mode

    def generate_summary(self, today_return: float, drawdown: float, rebalance_day_left: int) -> str:
        if self.mode == "초심자":
            return (
                f"오늘 전략 수익률은 {today_return:.2f}%입니다. "
                f"누적 손실은 {drawdown:.2f}%이며, "
                f"다음 리밸런싱은 {rebalance_day_left}일 후입니다."
            )
        elif self.mode == "전문가":
            return (
                f"[요약] +{today_return:.2f}% | DD: {drawdown:.2f}% | "
                f"Rebal T-{rebalance_day_left}일"
            )
        else:
            return "알 수 없는 모드입니다."


# 🔄 전체 실행 함수 예시
def run_module_23(
    today_return: float,
    volatility: float,
    drawdown_pct: float,
    tracking_error: float,
    backtest_gap: float,
    rebalance_day_left: int,
    user_mode: str = "초심자"
) -> dict:
    alerts = []

    # 1. 조건 기반 경고 평가 및 기록
    condition_checker = AlertCondition()
    condition_alerts = condition_checker.evaluate(today_return, volatility)
    condition_checker.log_alerts(condition_alerts)
    alerts.extend(condition_alerts)

    # 2. 리스크 기반 이상 감지
    risk_detector = RiskDeviationDetector()
    risk_alerts = risk_detector.check(tracking_error, drawdown_pct, backtest_gap)
    alerts.extend(risk_alerts)

    # 3. 자연어 요약 생성
    notifier = NaturalLanguageNotifier(mode=user_mode)
    summary = notifier.generate_summary(today_return, drawdown_pct, rebalance_day_left)

    return {
        "alerts": alerts,
        "summary": summary,
        "alert_log": condition_checker.get_alert_log().tail(5).to_dict(orient="records")
    }
    
import streamlit as st

def run():
    st.header("📘 23단원. 맞춤 알림 & 경고 시스템")
    st.markdown("""
    “AI는 사용자의 눈이 되어야 한다. 의사결정은 맥락에서 일어난다”

    - 23.1 조건 기반 알림 커스터마이징  
      예측 신뢰도 하락, 종목 급등락, 전략 성과 이탈 감지 시  
      조건 설정 UI 제공 (“-5% 이상 손실 시 알림” 등)  
      맥락 포함 알림: “ETF A 하락 → 전략 리밸런싱 예정”

    - 23.2 전략 리스크 감지 & 경고 시스템  
      전략 괴리율 급등, 성과 하락, 누적 손실 초과 시 경고  
      “적색경보” 전략 자동 표기  
      백업 전략 자동 전환 기능 (“전략 A 중단 → 전략 B 임시 전환”)

    - 23.3 사용자 언어 기반 요약 알림 시스템  
      자연어 요약: “오늘 전략 성과 +1.8%, 리스크 감소 중”  
      초심자/전문가 모드 선택 가능  
      음성 안내 포함: “현재 전략은 안정적입니다. 다음 리밸런싱은 2일 후.”
    """)