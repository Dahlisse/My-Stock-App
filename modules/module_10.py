# module_10.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 10.1 변동성 기반 손절선 계산
def calculate_stop_loss(price_series: pd.Series, multiplier: float = 2.0):
    """
    price_series: 시계열 종가 데이터
    multiplier: 변동성 배수로 손절선 설정
    """
    volatility = price_series.pct_change().rolling(window=20).std()
    stop_loss = price_series - multiplier * price_series * volatility
    return stop_loss

# 10.2 수익률 급락 경고 및 손절 조건 감지
def detect_stop_trigger(price_series: pd.Series, stop_loss: pd.Series):
    latest_price = price_series.iloc[-1]
    latest_stop = stop_loss.iloc[-1]

    if latest_price < latest_stop:
        return f"⚠️ 손절 신호 발생: 현재가 {latest_price:.2f}, 손절선 {latest_stop:.2f}"
    return None

# 10.3 포트 리스크 예측 (단순 분산 기반)
def portfolio_risk_analysis(returns: pd.DataFrame, weights: list):
    """
    returns: 종목별 일간 수익률 DataFrame
    weights: 각 종목 비중
    """
    cov_matrix = returns.cov()
    portfolio_var = np.dot(weights, np.dot(cov_matrix, weights))
    portfolio_std = np.sqrt(portfolio_var)
    return portfolio_std, portfolio_var

# 10.3 리스크 시각화
def visualize_risk_distribution(returns: pd.DataFrame):
    """
    각 종목의 수익률 분포 히스토그램
    """
    returns.hist(bins=50, figsize=(10, 6))
    plt.suptitle("수익률 분포 히스토그램")
    plt.tight_layout()
    plt.show()

# 10.4 슬리피지 반영 수익률 계산
def adjust_for_slippage(realized_return: float, slippage_pct: float = 0.002):
    """
    realized_return: 실제 포지션 수익률
    slippage_pct: 매매 시 발생할 수 있는 평균 슬리피지 비율
    """
    adjusted = realized_return - slippage_pct
    return round(adjusted, 4)

# 10.5 리스크 완충지대 계산
def compute_risk_buffer(price_series: pd.Series, window: int = 30, buffer_ratio: float = 0.1):
    """
    급등/급락에 대비한 최소 대응 여유 폭
    """
    recent_volatility = price_series.pct_change().rolling(window).std().iloc[-1]
    buffer_zone = buffer_ratio * recent_volatility * price_series.iloc[-1]
    return round(buffer_zone, 2)

# ========================
# 예시 실행 (테스트용)
# ========================
if __name__ == "__main__":
    # 예시 데이터 생성
    np.random.seed(42)
    dates = pd.date_range("2025-06-01", periods=60)
    price = pd.Series(np.cumsum(np.random.randn(60) * 2 + 100), index=dates)

    # 10.1 손절선 계산
    stop_loss = calculate_stop_loss(price)
    print("최근 손절선:", stop_loss.dropna().iloc[-1])

    # 10.2 손절 조건 감지
    alert = detect_stop_trigger(price, stop_loss)
    if alert:
        print(alert)

    # 10.3 포트 리스크 예측
    dummy_returns = pd.DataFrame({
        'A': np.random.normal(0.001, 0.02, 60),
        'B': np.random.normal(0.0012, 0.015, 60),
        'C': np.random.normal(0.0008, 0.01, 60),
    })
    weights = [0.4, 0.3, 0.3]
    std, var = portfolio_risk_analysis(dummy_returns, weights)
    print(f"포트폴리오 예상 표준편차: {std:.4f}, 분산: {var:.6f}")

    # 10.3 리스크 시각화
    visualize_risk_distribution(dummy_returns)

    # 10.4 슬리피지 반영 수익률
    adjusted_return = adjust_for_slippage(0.024, slippage_pct=0.003)
    print(f"슬리피지 반영 수익률: {adjusted_return*100:.2f}%")

    # 10.5 리스크 완충지대 계산
    buffer = compute_risk_buffer(price)
    print(f"리스크 완충 여유 폭: {buffer}")