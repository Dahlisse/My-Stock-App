import unittest
import time
from module_11 import backtest_engine  # 가정: 11단원의 백테스트 엔진 모듈 임포트

class TestBacktestSpeed(unittest.TestCase):
    def setUp(self):
        # 테스트에 사용할 전략 및 데이터 초기화
        self.strategy = backtest_engine.Strategy("test_strategy")
        self.data = backtest_engine.load_historical_data("sample_data.csv")

    def test_backtest_execution_time(self):
        start_time = time.time()
        results = backtest_engine.run_backtest(self.strategy, self.data)
        end_time = time.time()
        duration = end_time - start_time
        
        # 백테스트 실행 시간이 10초 이내인지 검증 (예시 기준)
        self.assertLessEqual(duration, 10, f"Backtest execution took too long: {duration} seconds")
        
        # 결과가 None이 아니어야 함
        self.assertIsNotNone(results)

if __name__ == "__main__":
    unittest.main()