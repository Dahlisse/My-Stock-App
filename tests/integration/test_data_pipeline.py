# integration/test_data_pipeline.py

import unittest
import pandas as pd
from integration import logger, set_seed, IntegrationTestException

# 실제 사용하는 모듈 import
from module_01 import load_stock_metadata
from module_02 import analyze_financial_statements
from module_03 import evaluate_strategy_scores

class TestDataPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logger.info("🔍 데이터 파이프라인 통합 테스트 시작")
        set_seed(42)

        # 테스트 대상 종목 설정 (샘플)
        cls.test_symbols = ["005930", "000660", "035420"]  # 삼성전자, SK하이닉스, NAVER

        # 1단계: 메타 데이터 수집
        try:
            cls.meta_df = load_stock_metadata(cls.test_symbols)
            logger.info("✅ 1단계 메타 데이터 수집 완료")
        except Exception as e:
            raise IntegrationTestException(f"메타 데이터 수집 실패: {e}")

        # 2단계: 재무 분석
        try:
            cls.fin_df = analyze_financial_statements(cls.test_symbols)
            logger.info("✅ 2단계 재무 분석 완료")
        except Exception as e:
            raise IntegrationTestException(f"재무 분석 실패: {e}")

        # 3단계: 전략 점수 평가 (예: 밸류 + 모멘텀 + 심리 점수)
        try:
            cls.score_df = evaluate_strategy_scores(cls.test_symbols)
            logger.info("✅ 3단계 전략 점수 평가 완료")
        except Exception as e:
            raise IntegrationTestException(f"전략 점수 평가 실패: {e}")

    def test_metadata_columns(self):
        required_cols = ["symbol", "name", "sector", "market_cap"]
        for col in required_cols:
            self.assertIn(col, self.meta_df.columns, f"'{col}' 컬럼 없음")

    def test_financial_analysis_format(self):
        self.assertTrue(isinstance(self.fin_df, pd.DataFrame))
        self.assertIn("ROE", self.fin_df.columns)
        self.assertGreaterEqual(len(self.fin_df), len(self.test_symbols))

    def test_score_generation(self):
        self.assertIn("value_score", self.score_df.columns)
        self.assertIn("momentum_score", self.score_df.columns)
        self.assertIn("sentiment_score", self.score_df.columns)

    def test_data_alignment(self):
        # 모든 데이터프레임에 종목 수 일치 확인
        self.assertEqual(
            len(self.meta_df), len(self.fin_df), "데이터프레임 길이 불일치"
        )
        self.assertEqual(
            len(self.fin_df), len(self.score_df), "데이터프레임 길이 불일치"
        )

if __name__ == "__main__":
    unittest.main()