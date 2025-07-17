# tests/unit/__init__.py

import logging
import sys

# 로깅 설정 (단위 테스트 전용)
logger = logging.getLogger("unit_tests")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("[UNIT TEST] %(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.debug("Unit test package initialized.")

# 테스트용 공통 설정 또는 모의(mock) 객체가 필요하다면 여기에 추가 가능
DEFAULT_TEST_CONFIG = {
    "mock_data_path": "tests/mock_data/",
    "tolerance": 1e-4,
    "run_parallel": False
}