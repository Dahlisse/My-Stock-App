# scenario/__init__.py

"""
📁 scenario/__init__.py
전략 시나리오 설계 & 멀티 시뮬레이션 엔진 초기화 모듈
"""

import os
import logging

# 프로젝트 루트 디렉토리 추적
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# 시나리오 설정 저장 디렉토리
SCENARIO_CONFIG_PATH = os.path.join(ROOT_DIR, "scenario", "configs")
SIMULATION_OUTPUT_PATH = os.path.join(ROOT_DIR, "scenario", "results")

# 시나리오 로깅 설정
logger = logging.getLogger("scenario_engine")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [Scenario] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# 시나리오 실행 상태 추적 객체
SCENARIO_REGISTRY = {}

def register_scenario(name: str, config: dict):
    """
    사용자 정의 시나리오 등록
    """
    if name in SCENARIO_REGISTRY:
        logger.warning(f"⚠️ 시나리오 '{name}'는 이미 등록되어 있음. 덮어씁니다.")
    SCENARIO_REGISTRY[name] = config
    logger.info(f"✅ 시나리오 등록 완료: {name}")

def list_scenarios():
    """
    등록된 시나리오 목록 조회
    """
    return list(SCENARIO_REGISTRY.keys())

def get_scenario(name: str):
    """
    특정 시나리오 설정 조회
    """
    return SCENARIO_REGISTRY.get(name, None)

# 모듈 초기화 메시지
logger.info("📦 scenario 패키지 초기화 완료")