# regression/test_model_drift.py

"""
📁 regression/test_model_drift.py
전략 예측 모델의 드리프트(Drift) 여부 회귀 테스트
- 동일 입력에 대해 예측 결과가 의미 없이 바뀌었는지 감지
"""

import os
import json
import numpy as np
import pytest
from sklearn.metrics import mean_squared_error
from regression import ROOT_DIR, logger, DEFAULT_TEST_ENV
from modules.module_14 import predict_entry_exit_points  # 예: 진입/청산 전략 예측기

# 기준 예측 결과 저장 경로
REFERENCE_DIR = os.path.join(ROOT_DIR, "reference_outputs")
CURRENT_DIR = os.path.join(ROOT_DIR, "current_outputs")

# 테스트용 입력 (고정된 시계열 데이터 예시)
STATIC_INPUT_PATH = os.path.join(ROOT_DIR, "test_assets", "static_market_input.json")


@pytest.mark.parametrize("model_name", ["entry_exit_predictor"])
def test_model_drift(model_name):
    """
    고정 입력에 대한 예측 결과가 기준과 다르게 바뀌었는지 회귀 테스트.
    """
    logger.info(f"🧠 모델 드리프트 테스트 시작: [{model_name}]")

    # Step 1: 입력 데이터 로드
    with open(STATIC_INPUT_PATH, "r") as f:
        input_data = json.load(f)

    # Step 2: 현재 모델 예측
    current_preds = predict_entry_exit_points(input_data=input_data)
    current_output_path = os.path.join(CURRENT_DIR, f"{model_name}_preds.json")
    with open(current_output_path, "w") as f:
        json.dump(current_preds, f, indent=2)

    # Step 3: 기준 예측 결과 로드
    reference_path = os.path.join(REFERENCE_DIR, f"{model_name}_preds.json")
    assert os.path.exists(reference_path), f"📂 기준 예측 없음: {reference_path}"
    with open(reference_path, "r") as f:
        reference_preds = json.load(f)

    # Step 4: 예측 결과 비교 (예: 예측된 진입 시점)
    keys_to_compare = ["entry_signals", "exit_signals"]
    tolerance = DEFAULT_TEST_ENV["drift_tolerance"]

    for key in keys_to_compare:
        current = np.array(current_preds.get(key, []))
        reference = np.array(reference_preds.get(key, []))

        mse = mean_squared_error(reference, current)
        assert mse < tolerance, (
            f"📉 예측 모델 드리프트 감지됨 [{model_name} - {key}]\n"
            f"MSE: {mse:.6f} > 허용값 {tolerance}"
        )

    logger.info(f"✅ 모델 드리프트 없음 확인: [{model_name}] 예측 일관성 유지")