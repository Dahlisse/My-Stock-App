import pytest
from modules_custom_strategy import CustomStrategyBuilder

@pytest.fixture
def valid_user_input():
    return {
        "indicators": ["RSI", "MACD"],
        "entry_conditions": {"RSI": {"lt": 30}, "MACD": {"crossover": True}},
        "exit_conditions": {"RSI": {"gt": 70}},
        "target_return": 0.15,
        "max_drawdown": 0.1
    }

@pytest.fixture
def invalid_user_input():
    return {
        "indicators": [],
        "entry_conditions": {"RSI": {"lt": -10}},  # 잘못된 값
        "exit_conditions": {},
        "target_return": -0.5,  # 음수 수익률은 비정상
        "max_drawdown": 1.5     # 100% 초과
    }

def test_custom_strategy_build_valid(valid_user_input):
    builder = CustomStrategyBuilder()
    strategy = builder.build_strategy(valid_user_input)
    assert strategy is not None
    assert strategy.target_return == valid_user_input["target_return"]
    assert strategy.max_drawdown == valid_user_input["max_drawdown"]

def test_custom_strategy_build_invalid(invalid_user_input):
    builder = CustomStrategyBuilder()
    with pytest.raises(ValueError):
        builder.build_strategy(invalid_user_input)

def test_strategy_execution_with_custom_input(valid_user_input):
    builder = CustomStrategyBuilder()
    strategy = builder.build_strategy(valid_user_input)
    result = strategy.execute_backtest()
    assert "total_return" in result
    assert result["total_return"] <= valid_user_input["target_return"] + 0.05  # 약간 여유 있음
    assert result["max_drawdown"] <= valid_user_input["max_drawdown"] + 0.05