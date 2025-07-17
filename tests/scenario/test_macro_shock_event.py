import pytest
from scenario.multi_simulation_engine import run_scenario_simulation
from scenario.scenario_config_loader import load_scenario_config
from scenario.result_aggregator import aggregate_results

@pytest.fixture
def macro_shock_config():
    """
    매크로 충격 이벤트 시나리오 구성
    - 금리 급등
    - 환율 급변동
    - 유가 급락
    """
    return {
        "scenario_name": "macro_shock_event",
        "macro_conditions": {
            "interest_rate": "spike",
            "exchange_rate": "volatile",
            "oil_price": "sharp_decline"
        },
        "strategies": ["risk_off", "cash_hold", "commodity_hedge"],
        "simulation_period": {
            "start": "2021-03-01",
            "end": "2021-09-30"
        }
    }

def test_macro_shock_simulation_runs(macro_shock_config):
    config = load_scenario_config(macro_shock_config)
    results = run_scenario_simulation(config)
    assert isinstance(results, dict)
    for strategy in macro_shock_config["strategies"]:
        assert strategy in results

def test_macro_shock_strategy_drawdown(macro_shock_config):
    config = load_scenario_config(macro_shock_config)
    results = run_scenario_simulation(config)
    for strategy, metrics in results.items():
        # 급격한 매크로 충격이지만 전략별 최대 손실 20% 이하 허용
        assert metrics["max_drawdown"] <= 0.2, f"{strategy} drawdown too high"
        # 변동성은 최대 30%까지 허용
        assert metrics["volatility"] <= 0.3, f"{strategy} volatility too high"

def test_macro_shock_result_aggregation(macro_shock_config):
    config = load_scenario_config(macro_shock_config)
    raw_results = run_scenario_simulation(config)
    aggregated = aggregate_results(raw_results)
    assert "average_return" in aggregated
    assert aggregated["average_return"] >= -0.1  # 충격기 손실 10% 이내 기대
    assert aggregated["max_drawdown"] <= 0.25