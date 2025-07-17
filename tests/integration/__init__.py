# integration/__init__.py

import os
import sys
import logging
import datetime
import random
import numpy as np

# 프로젝트 루트 경로 설정 (통합 테스트 시 import 오류 방지)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# 로깅 설정
def get_logger(name: str = "integration_test") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"
        )
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        logger.addHandler(console)
    return logger

logger = get_logger()

# 고정 시드 설정 함수 (통합 테스트 일관성 확보용)
def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    logger.info(f"Seed set to: {seed}")

# 공용 테스트용 날짜 생성기
def generate_date_range(start="2022-01-01", end="2025-01-01", freq="M"):
    return list(pd.date_range(start=start, end=end, freq=freq))

# 공통 예외 메시지 처리
class IntegrationTestException(Exception):
    pass