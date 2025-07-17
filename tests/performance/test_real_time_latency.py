import unittest
import time
from module_11 import real_time_data_feed, strategy_executor  # 가정: 실시간 데이터 및 실행 모듈 임포트

class TestRealTimeLatency(unittest.TestCase):
    def setUp(self):
        # 실시간 데이터 피드 초기화
        self.data_feed = real_time_data_feed.RealTimeFeed(source="test_source")
        self.executor = strategy_executor.StrategyExecutor()

    def test_latency_under_threshold(self):
        # 실시간 데이터 이벤트 수신 시뮬레이션
        start_time = time.time()
        event = self.data_feed.get_next_event()
        processing_result = self.executor.process_event(event)
        end_time = time.time()
        latency = end_time - start_time
        
        # 실시간 처리 지연은 0.5초 이내여야 함
        self.assertLessEqual(latency, 0.5, f"Real-time processing latency too high: {latency} seconds")
        
        # 처리 결과가 정상인지 확인 (예: True)
        self.assertTrue(processing_result)

if __name__ == "__main__":
    unittest.main()