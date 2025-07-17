# integration/test_visual_reporting.py

import unittest
import os
from integration import logger, IntegrationTestException
from module_07 import generate_visual_report

class TestVisualReporting(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logger.info("📊 전략 시각화 및 리포트 자동 생성 테스트 시작")

        cls.sample_strategy_result = {
            "strategy_name": "GrowthMomentum",
            "cumulative_return": [1.0, 1.02, 1.05, 1.12],
            "drawdowns": [0.0, 0.01, 0.03, 0.02],
            "dates": ["2024-01-01", "2024-02-01", "2024-03-01", "2024-04-01"],
            "sharpe_ratio": 1.45,
            "max_drawdown": 0.05
        }

        try:
            cls.report_path = generate_visual_report(cls.sample_strategy_result, save_path="temp_report.png")
            logger.info(f"✅ 시각 리포트 생성 성공: {cls.report_path}")
        except Exception as e:
            raise IntegrationTestException(f"리포트 생성 실패: {e}")

    def test_report_file_created(self):
        self.assertTrue(os.path.exists(self.report_path), f"리포트 파일이 존재하지 않음: {self.report_path}")

    def test_report_file_format(self):
        self.assertTrue(self.report_path.endswith(".png"), "리포트 파일 확장자가 .png가 아님")

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.report_path):
            os.remove(cls.report_path)
            logger.info("🧹 테스트 완료 후 임시 리포트 파일 삭제")

if __name__ == "__main__":
    unittest.main()