# integration/test_macro_adaptive.py

import unittest
import pandas as pd
from integration import logger, set_seed, IntegrationTestException

# 매크로 기반 전략 적응 관련 모듈
from module_19 import (
    collect_macro_indicators,
    classify_macro_event,
    branch_strategy_by_macro_event
)

class TestMacroAdaptiveStrategy(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logger.info("📊 매크로 기반 전략 적응 시스템 테스트 시작")
        set_seed(42)

        try:
            cls.macro_df = collect_macro_indicators()
            logger.info("✅ 매크로 지표 수집 성공")
        except Exception as e:
            raise IntegrationTestException(f"매크로 지표 수집 실패: {e}")

        try:
            cls.event_info = classify_macro_event(cls.macro_df)
            logger.info("✅ 매크로 이벤트 분류 성공")
        except Exception as e:
            raise IntegrationTestException(f"매크로 이벤트 분류 실패: {e}")

        try:
            cls.branches = branch_strategy_by_macro_event(cls.event_info)
            logger.info("✅ 전략 분기 성공")
        except Exception as e:
            raise IntegrationTestException(f"전략 분기 실패: {e}")

    def test_macro_data_format(self):
        self.assertIsInstance(self.macro_df, pd.DataFrame)
        self.assertIn("CPI", self.macro_df.columns)
        self.assertIn("interest_rate", self.macro_df.columns)

    def test_macro_event_structure(self):
        self.assertIn("event_cluster", self.event_info)
        self.assertIn("tag", self.event_info)

    def test_strategy_branch_type(self):
        self.assertIsInstance(self.branches, dict)
        self.assertTrue("selected_strategy" in self.branches)
        self.assertIn(self.branches["selected_strategy"], ["defensive", "growth", "inflation_hedge"])

if __name__ == "__main__":
    unittest.main()