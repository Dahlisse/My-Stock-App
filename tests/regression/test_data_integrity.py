# regression/test_data_integrity.py

"""
📁 regression/test_data_integrity.py
입력 데이터의 무결성 검증 테스트
- 결측값, 이상치, 포맷 불일치 등을 사전에 탐지
"""

import os
import json
import numpy as np
import pytest
from regression import ROOT_DIR, logger

# 테스트 대상 데이터 경로
TEST_DATA_PATH = os.path.join(ROOT_DIR, "test_assets", "static_market_input.json")

# 허용 가능한 컬럼 (샘플 예시)
REQUIRED_COLUMNS = {
    "timestamp",
    "open",
    "high",
    "low",
    "close",
    "volume"
}


def load_input_data(path):
    with open(path, "r") as f:
        return json.load(f)


def test_required_columns_exist():
    """
    필수 컬럼 누락 여부 확인
    """
    logger.info("🧪 입력 데이터 필수 컬럼 존재 여부 확인")
    data = load_input_data(TEST_DATA_PATH)

    for row in data:
        for col in REQUIRED_COLUMNS:
            assert col in row, f"❌ 누락된 필수 컬럼: {col}"


def test_no_missing_values():
    """
    결측값(None, '', NaN 등) 존재 여부 확인
    """
    logger.info("🧪 입력 데이터 결측값 확인")
    data = load_input_data(TEST_DATA_PATH)

    for idx, row in enumerate(data):
        for key, value in row.items():
            assert value not in [None, "", "NaN", "nan"], (
                f"❌ 결측값 발견 - 행 {idx}, 컬럼: {key}"
            )


def test_numerical_bounds():
    """
    비정상적으로 큰/작은 값이 있는지 확인
    """
    logger.info("🧪 입력 데이터 이상치 검증")
    data = load_input_data(TEST_DATA_PATH)

    for idx, row in enumerate(data):
        for field in ["open", "high", "low", "close", "volume"]:
            value = row.get(field, 0)
            try:
                val = float(value)
                assert -1e10 < val < 1e10, (
                    f"❌ 비정상 수치값 감지 - 행 {idx}, 필드 {field}, 값: {val}"
                )
            except Exception:
                raise AssertionError(f"❌ 수치 변환 실패 - 행 {idx}, 필드 {field}, 값: {value}")