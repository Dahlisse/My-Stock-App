# integration/test_strategy_execution.py

import unittest
import pandas as pd
from integration import logger, set_seed, IntegrationTestException

# 필요한 전략 모듈 import
from module_03 import evaluate_strategy_scores
from module_04 import generate_portfolio
from module_06 import detect_market_psychology
from module_14 import predict_entry_exit_points

class TestStrategyExecution(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logger.info("🚀 전략 실행 통합 테스트 시작")
        set_seed(42)

        cls.test_symbols = ["005930", "000660", "035420"]  # 예시: 삼성전자 등

        try:
            cls.score_df = evaluate_strategy_scores(cls.test_symbols)
            logger.info("✅ 전략 점수 생성 완료")
        except Exception as e:
            raise IntegrationTestException(f"전략 점수 생성 실패: {e}")

        try:
            cls.portfolio_df = generate_portfolio(cls.score_df)
            logger.info("✅ 포트폴리오 구성 완료")
        except Exception as e:
            raise IntegrationTestException(f"포트폴리오 구성 실패: {e}")

        try:
            cls.market_psych = detect_market_psychology()
            logger.info("✅ 시장 심리 탐지 완료")
        except Exception as e:
            raise IntegrationTestException(f"시장 심리 분석 실패: {e}")

        try:
            cls.entry_exit_df = predict_entry_exit_points(cls.portfolio_df)
            logger.info("✅ 진입/청산 타이밍 예측 완료")
        except Exception as e:
            raise IntegrationTestException(f"진입/청산 예측 실패: {e}")

    def test_score_dataframe(self):
        self.assertIn("value_score", self.score_df.columns)
        self.assertIn("momentum_score", self.score_df.columns)

    def test_portfolio_structure(self):
        self.assertIn("symbol", self.portfolio_df.columns)
        self.assertIn("weight", self.portfolio_df.columns)
        self.assertTrue(all(self.portfolio_df["weight"] >= 0))

    def test_psychology_output(self):
        self.assertIn("sentiment_index", self.market_psych)
        self.assertTrue(0 <= self.market_psych["sentiment_index"] <= 100)

    def test_entry_exit_format(self):
        self.assertIn("symbol", self.entry_exit_df.columns)
        self.assertIn("entry_signal", self.entry_exit_df.columns)
        self.assertIn("exit_signal", self.entry_exit_df.columns)

if __name__ == "__main__":
    unittest.main()