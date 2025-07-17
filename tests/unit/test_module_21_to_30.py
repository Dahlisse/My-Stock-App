# Tests/unit/test_module_21_to_30.py

import unittest
from modules.module_21 import detect_market_phase
from modules.module_22 import rebalance_strategy_by_phase
from modules.module_23 import estimate_risk_of_ruin
from modules.module_24 import apply_tail_risk_hedge
from modules.module_25 import simulate_black_swan_events
from modules.module_26 import integrate_alternative_data
from modules.module_27 import simulate_global_rotation
from modules.module_28 import user_defined_strategy
from modules.module_29 import run_multi_scenario_simulation
from modules.module_30 import generate_self_improving_insights


class TestModules21To30(unittest.TestCase):

    def test_detect_market_phase(self):
        result = detect_market_phase("KOSPI")
        self.assertIn(result, ["bull", "bear", "correction", "sideways"])

    def test_rebalance_strategy_by_phase(self):
        portfolio = {"AAPL": 0.6, "QQQ": 0.4}
        result = rebalance_strategy_by_phase(portfolio, phase="bear")
        self.assertAlmostEqual(sum(result.values()), 1.0, places=2)
        self.assertIsInstance(result, dict)

    def test_estimate_risk_of_ruin(self):
        result = estimate_risk_of_ruin(win_rate=0.55, payoff_ratio=1.5, capital=100000, max_drawdown=0.3)
        self.assertIn("risk_of_ruin", result)
        self.assertGreaterEqual(result["risk_of_ruin"], 0.0)
        self.assertLessEqual(result["risk_of_ruin"], 1.0)

    def test_apply_tail_risk_hedge(self):
        base_portfolio = {"SPY": 0.7, "TLT": 0.3}
        result = apply_tail_risk_hedge(base_portfolio)
        self.assertTrue("hedged_portfolio" in result)
        self.assertAlmostEqual(sum(result["hedged_portfolio"].values()), 1.0, places=2)

    def test_simulate_black_swan_events(self):
        result = simulate_black_swan_events("MSFT")
        self.assertIn("impact", result)
        self.assertIsInstance(result["impact"], dict)

    def test_integrate_alternative_data(self):
        result = integrate_alternative_data("TSLA")
        self.assertIn("sentiment_score", result)
        self.assertIsInstance(result["sentiment_score"], float)

    def test_simulate_global_rotation(self):
        result = simulate_global_rotation()
        self.assertIn("rotation_map", result)
        self.assertIsInstance(result["rotation_map"], dict)

    def test_user_defined_strategy(self):
        user_input = {
            "rules": [
                {"indicator": "RSI", "condition": "<", "value": 30, "action": "buy"},
                {"indicator": "MA", "condition": ">", "value": "200MA", "action": "sell"}
            ],
            "universe": ["AAPL", "MSFT"]
        }
        result = user_defined_strategy(user_input)
        self.assertIn("strategy_output", result)
        self.assertIsInstance(result["strategy_output"], list)

    def test_run_multi_scenario_simulation(self):
        scenarios = ["bull_market", "bear_market", "recession"]
        result = run_multi_scenario_simulation(scenarios)
        self.assertTrue(all(s in result for s in scenarios))

    def test_generate_self_improving_insights(self):
        portfolio = {"AAPL": 0.5, "MSFT": 0.5}
        result = generate_self_improving_insights(portfolio)
        self.assertIn("recommendations", result)
        self.assertIsInstance(result["recommendations"], list)


if __name__ == '__main__':
    unittest.main()