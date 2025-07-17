# regression/__init__.py

"""
📁 regression/__init__.py
회귀 테스트 초기화 모듈: 공통 설정, 로거, 상수 정의 등
"""

import logging
import os
from datetime import datetime

# 회귀 테스트용 로거 설정
logger = logging.getLogger("regression_tests")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(levelname)s][%(asctime)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# 회귀 테스트용 루트 경로 정의
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

# 회귀 테스트 공통 타임스탬프
TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# 공통 환경 설정
DEFAULT_TEST_ENV = {
    "use_cache": True,
    "strict_mode": False,
    "tolerance": 1e-4,
    "date": TIMESTAMP,
}

logger.info("📦 regression package initialized.")