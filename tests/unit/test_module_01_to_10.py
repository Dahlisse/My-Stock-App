# tests/unit/test_module_01_to_10.py
import pytest
import datetime
from modules import module_01, module_02, module_03, module_04, module_05, module_06, module_07, module_08, module_09, module_10

@pytest.fixture
def sample_ticker():
    return "005930.KS"  # 삼성전자 예시

@pytest.fixture
def sample_date_range():
    return datetime.date(2023, 1, 1), datetime.date(2023, 6, 30)

def test_module_01_get_stock_meta(sample_ticker):
    """
    1단원: 종목 메타 정보 수집 테스트
    """
    meta = module_01.get_stock_meta(sample_ticker)
    assert meta is not None, "Meta data should not be None"
    assert isinstance(meta, dict), "Meta should be dict"
    assert "ticker" in meta and meta["ticker"] == sample_ticker
    assert "name" in meta and isinstance(meta["name"], str)
    assert "market_cap" in meta and meta["market_cap"] > 0

def test_module_02_financial_ratios(sample_ticker):
    """
    2단원: 재무지표 분석 및 이상징후 감지 테스트
    """
    financials = module_02.get_financial_statements(sample_ticker)
    assert financials is not None
    assert isinstance(financials, dict)

    per = module_02.calculate_per(financials)
    assert per > 0

    roe = module_02.calculate_roe(financials)
    assert 0 <= roe <= 100

    anomaly_flags = module_02.detect_financial_anomalies(financials)
    assert isinstance(anomaly_flags, dict)

def test_module_03_integrate_strategy_score(sample_ticker):
    """
    3단원: 종합 전략 점수 계산 테스트
    """
    score = module_03.integrate_strategy_score(sample_ticker)
    assert isinstance(score, float)
    assert 0 <= score <= 1

def test_module_04_build_portfolio():
    """
    4단원: 최적 포트폴리오 구성 테스트
    """
    target_return = 0.1
    portfolio = module_04.build_portfolio(target_return)
    assert isinstance(portfolio, dict)
    assert len(portfolio) > 0
    for ticker, weight in portfolio.items():
        assert isinstance(ticker, str)
        assert 0 < weight <= 1
    total_weight = sum(portfolio.values())
    assert abs(total_weight - 1) < 0.01

def test_module_05_get_market_sentiment_score():
    """
    5단원: 시장 심리 점수 획득 테스트
    """
    score = module_05.get_market_sentiment_score()
    assert isinstance(score, float)
    assert -1 <= score <= 1

def test_module_06_strategy_switch():
    """
    6단원: 전략 전환 감지 및 제안 테스트
    """
    current_strategy = module_06.get_current_strategy()
    assert current_strategy in ["A", "B", "C"]

    next_strategy = module_06.detect_strategy_switch()
    assert next_strategy in ["A", "B", "C", None]

def test_module_07_generate_performance_chart(sample_ticker):
    """
    7단원: 성과 차트 생성 테스트
    """
    fig = module_07.generate_performance_chart([sample_ticker])
    assert fig is not None
    assert hasattr(fig, "savefig")

def test_module_08_load_historical_data(sample_ticker, sample_date_range):
    """
    8단원: 데이터 로딩 테스트
    """
    start_date, end_date = sample_date_range
    df = module_08.load_historical_data(sample_ticker, start_date=start_date, end_date=end_date)
    assert df is not None
    assert not df.empty
    assert "Close" in df.columns
    assert df.index.min().date() >= start_date
    assert df.index.max().date() <= end_date

def test_module_09_calculate_risk_metrics(sample_ticker):
    """
    9단원: 리스크 지표 산출 테스트
    """
    metrics = module_09.calculate_risk_metrics(sample_ticker)
    assert isinstance(metrics, dict)
    assert "VaR" in metrics
    assert "CVaR" in metrics
    assert isinstance(metrics["VaR"], float)
    assert isinstance(metrics["CVaR"], float)

def test_module_10_run_backtest():
    """
    10단원: 통합 백테스트 실행 테스트
    """
    tickers = ["005930.KS", "000660.KS"]
    results = module_10.run_backtest(tickers)
    assert isinstance(results, dict)
    assert "total_return" in results
    assert isinstance(results["total_return"], float)
    assert "max_drawdown" in results
    assert isinstance(results["max_drawdown"], float)

if __name__ == "__main__":
    pytest.main()