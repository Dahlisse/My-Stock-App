# integration/test_ai_feedback_loop.py

import unittest
from modules.module_28 import generate_ai_feedback
from utils.logging_utils import setup_logger

logger = setup_logger("ai_feedback_test")

class TestAIFeedbackLoop(unittest.TestCase):

    def setUp(self):
        # 샘플 전략 성능 입력값 (예: 수익률, 샤프 비율, 최대 낙폭 등)
        self.sample_strategy_stats = {
            "return": 0.092,
            "sharpe_ratio": 1.42,
            "max_drawdown": -0.08,
            "volatility": 0.14
        }

    def test_generate_ai_feedback_output_type(self):
        """AI 피드백 출력 타입 확인"""
        feedback = generate_ai_feedback(self.sample_strategy_stats)
        self.assertIsInstance(feedback, dict)
        self.assertIn("summary", feedback)
        self.assertIn("improvement_suggestions", feedback)

    def test_feedback_summary_not_empty(self):
        """AI 피드백 요약이 비어 있지 않음"""
        feedback = generate_ai_feedback(self.sample_strategy_stats)
        summary = feedback.get("summary", "")
        self.assertTrue(len(summary.strip()) > 0)

    def test_feedback_suggestions_structure(self):
        """개선 제안 항목의 구조 검증"""
        feedback = generate_ai_feedback(self.sample_strategy_stats)
        suggestions = feedback.get("improvement_suggestions", [])
        self.assertIsInstance(suggestions, list)
        self.assertGreaterEqual(len(suggestions), 1)
        for suggestion in suggestions:
            self.assertIn("title", suggestion)
            self.assertIn("detail", suggestion)

    def tearDown(self):
        logger.info("TestAIFeedbackLoop 완료")

if __name__ == "__main__":
    unittest.main()