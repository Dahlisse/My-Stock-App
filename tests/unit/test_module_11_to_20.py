# Tests/unit/test_module_11_to_20.py

import unittest
from modules.module_11 import run_high_speed_backtest
from modules.module_12 import simulate_risk_factors
from modules.module_13 import calculate_risk_score
from modules.module_14 import predict_entry_exit_points
from modules.module_15 import adapt_strategy_with_macro
from modules.module_16 import adjust_portfolio_automatically
from modules.module_17 import build_multi_factor_model
from modules.module_18 import monitor_real_time_signals
from modules.module_19 import macro_event_triggered_strategy
from modules.module_20 import manage_position_dynamically


class TestModules11To20(unittest.TestCase):

    def test_run_high_speed_backtest(self):
        sample_portfolio = {"AAPL": 0.5, "MSFT": 0.5}
        result = run_high_speed_backtest(sample_portfolio, years=3)
        self.assertIn("performance", result)
        self.assertGreaterEqual(result["performance"]["cagr"], -1)

    def test_simulate_risk_factors(self):
        result = simulate_risk_factors("AAPL", horizon_months=12)
        self.assertIn("VaR", result)
        self.assertLess(result["VaR"], 0)

    def test_calculate_risk_score(self):
        result = calculate_risk_score("TSLA")
        self.assertIn("score", result)
        self.assertGreaterEqual(result["score"], 0)
        self.assertLessEqual(result["score"], 100)

    def test_predict_entry_exit_points(self):
        result = predict_entry_exit_points("GOOG")
        self.assertIn("entry_signal", result)
        self.assertIn(result["entry_signal"], ["buy", "hold", "sell"])

    def test_adapt_strategy_with_macro(self):
        macro_event = {
            "cpi": 3.5,
            "pmi": 48,
            "usdkrw": 1320
        }
        strategy_output = adapt_strategy_with_macro(macro_event)
        self.assertIn("recommended_strategy", strategy_output)

    def test_adjust_portfolio_automatically(self):
        portfolio = {"AAPL": 0.3, "GOOG": 0.3, "TSLA": 0.4}
        result = adjust_portfolio_automatically(portfolio)
        self.assertAlmostEqual(sum(result.values()), 1.0, places=2)

    def test_build_multi_factor_model(self):
        result = build_multi_factor_model("NVDA")
        self.assertIn("factors", result)
        self.assertTrue(isinstance(result["factors"], dict))

    def test_monitor_real_time_signals(self):
        result = monitor_real_time_signals("AMZN")
        self.assertIn("alerts", result)
        self.assertIsInstance(result["alerts"], list)

    def test_macro_event_triggered_strategy(self):
        macro_input = {"inflation": "high", "growth": "low"}
        result = macro_event_triggered_strategy(macro_input)
        self.assertIn("strategy", result)

    def test_manage_position_dynamically(self):
        position = {"AAPL": {"weight": 0.5, "trend": "up"}}
        result = manage_position_dynamically(position)
        self.assertIn("adjustment", result)
        self.assertIsInstance(result["adjustment"], dict)


if __name__ == '__main__':
    unittest.main()