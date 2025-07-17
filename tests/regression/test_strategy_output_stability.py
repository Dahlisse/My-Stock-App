# regression/test_strategy_output_stability.py

"""
📁 regression/test_strategy_output_stability.py
전략 출력의 안정성 회귀 테스트
- 전략 결과가 이전 버전과 비교해 변동이 없는지 검증
"""

import json
import os
import pytest
import pandas as pd
from regression import ROOT_DIR, logger, DEFAULT_TEST_ENV
from modules.module_07 import generate_report  # 예시: 보고서 생성 전략
from modules.module_14 import predict_entry_exit_points  # 예시: 전략 타이밍 예측

# 이전 기준 출력 결과 파일 (예: CSV, JSON 형태 저장)
REFERENCE_DIR = os.path.join(ROOT_DIR, "reference_outputs")
CURRENT_DIR = os.path.join(ROOT_DIR, "current_outputs")

# 테스트할 전략 이름 목록
STRATEGIES_TO_TEST = [
    "momentum_growth",
    "value_dividend",
    "ai_adaptive_timing",
]

@pytest.mark.parametrize("strategy_name", STRATEGIES_TO_TEST)
def test_strategy_output_stability(strategy_name):
    """
    주어진 전략의 출력이 이전 기준 결과와 일치하는지 검증.
    """
    logger.info(f"🧪 회귀 테스트 시작: 전략 [{strategy_name}]")

    # Step 1: 현재 전략 결과 생성
    current_result = generate_report(strategy_name=strategy_name, save_path=CURRENT_DIR)
    current_df = pd.read_csv(os.path.join(CURRENT_DIR, f"{strategy_name}_report.csv"))

    # Step 2: 기준 결과 로드
    reference_file = os.path.join(REFERENCE_DIR, f"{strategy_name}_report.csv")
    assert os.path.exists(reference_file), f"📂 기준 결과 없음: {reference_file}"
    reference_df = pd.read_csv(reference_file)

    # Step 3: 주요 수익률 또는 지표 비교 (기본 tolerace 허용)
    key_columns = ["total_return", "sharpe_ratio", "max_drawdown"]
    tolerance = DEFAULT_TEST_ENV["tolerance"]

    for col in key_columns:
        current_val = float(current_df[col].values[0])
        reference_val = float(reference_df[col].values[0])
        diff = abs(current_val - reference_val)

        assert diff < tolerance, (
            f"📉 전략 [{strategy_name}]의 '{col}' 수치 변경 발생\n"
            f"기준값: {reference_val}, 현재값: {current_val}, 차이: {diff}"
        )

    logger.info(f"✅ 회귀 테스트 통과: 전략 [{strategy_name}] 출력 일치")