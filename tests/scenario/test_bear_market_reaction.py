import pytest
from scenario.multi_simulation_engine import run_scenario_simulation
from scenario.scenario_config_loader import load_scenario_config
from scenario.result_aggregator import aggregate_results

@pytest.fixture
def bear_market_config():
    """
    약세장(하락장) 시나리오 구성
    - 금리 상승
    - 주가지수 하락
    - 공포 심리 극대화
    """
    return {
        "scenario_name": "bear_market",
        "macro_conditions": {
            "interest_rate": "rising",
            "stock_index": "declining",
            "volatility_index": "high",
            "investor_sentiment": "fear"
        },
        "strategies": ["defensive_etf", "gold_hedge", "short_index"],
        "simulation_period": {
            "start": "2020-01-01",
            "end": "2020-06-30"
        }
    }

def test_bear_market_simulation_runs(bear_market_config):
    config = load_scenario_config(bear_market_config)
    results = run_scenario_simulation(config)
    assert isinstance(results, dict)
    assert "defensive_etf" in results
    assert "gold_hedge" in results

def test_bear_market_strategy_resilience(bear_market_config):
    config = load_scenario_config(bear_market_config)
    results = run_scenario_simulation(config)

    for strategy, metrics in results.items():
        assert metrics["max_drawdown"] < 0.15, f"{strategy} drawdown too high"
        assert metrics["volatility"] < 0.25, f"{strategy} too volatile"
        assert metrics["return"] > -0.1, f"{strategy} return too poor in bear market"

def test_bear_market_result_aggregation(bear_market_config):
    config = load_scenario_config(bear_market_config)
    raw_results = run_scenario_simulation(config)
    aggregated = aggregate_results(raw_results)

    assert "average_return" in aggregated
    assert aggregated["average_return"] > -0.05
    assert aggregated["max_drawdown"] < 0.2