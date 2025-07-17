# tests/unit/test_module_01_to_10.py
import pytest

# 가상의 각 단원 모듈 import 예시
from modules import module_01, module_02, module_03, module_04, module_05, module_06, module_07, module_08, module_09, module_10

def test_module_01_basic_info():
    # 예시: 종목 메타 정보 수집 함수 테스트
    sample_ticker = "005930.KS"
    meta = module_01.get_stock_meta(sample_ticker)
    assert meta is not None
    assert "name" in meta
    assert meta["ticker"] == sample_ticker

def test_module_02_financial_analysis():
    # 예시: PER 계산 테스트
    per = module_02.calculate_per("005930.KS")
    assert per > 0
    assert isinstance(per, float)

def test_module_03_strategy_judgement():
    score = module_03.integrate_strategy_score("005930.KS")
    assert 0 <= score <= 1

def test_module_04_portfolio_construction():
    portfolio = module_04.build_portfolio(target_return=0.1)
    assert isinstance(portfolio, dict)
    assert len(portfolio) > 0

def test_module_05_market_sentiment():
    sentiment_score = module_05.get_market_sentiment_score()
    assert -1 <= sentiment_score <= 1

def test_module_06_strategy_switch():
    current_strategy = module_06.get_current_strategy()
    assert current_strategy in ["A", "B", "C"]

def test_module_07_visualization():
    fig = module_07.generate_performance_chart(["005930.KS"])
    assert fig is not None

def test_module_08_data_loader():
    data = module_08.load_historical_data("005930.KS", period="1y")
    assert data is not None
    assert len(data) > 0

def test_module_09_risk_management():
    risk_metrics = module_09.calculate_risk_metrics("005930.KS")
    assert "VaR" in risk_metrics

def test_module_10_integration():
    # 예시: 백테스트 모듈 통합 작동 테스트
    results = module_10.run_backtest(["005930.KS", "000660.KS"])
    assert "total_return" in results
    assert results["total_return"] > -1

if __name__ == "__main__":
    pytest.main()