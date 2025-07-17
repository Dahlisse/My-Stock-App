import streamlit as st
import importlib
import toml
import os
from modules.modules_device_detector import detect_device
from modules import (
    module_01, module_02, module_03, module_04, module_05,
    module_06, module_07, module_08, module_09, module_10,
    module_11, module_12, module_13, module_14, module_15,
    module_16, module_17, module_18, module_19, module_20,
    module_21, module_22, module_23, module_24, module_25,
    module_26, module_27, module_28, module_29, module_30,
)

# ⬛ Config & State Initialization
config = toml.load("config.toml")
st.set_page_config(page_title="AI 전략 시스템", layout="wide")

# ⬛ 디바이스 기반 레이아웃 설정
device = detect_device()
if device == 'mobile':
    st.markdown("<style>body { font-size: 14px; }</style>", unsafe_allow_html=True)
else:
    st.markdown("<style>body { font-size: 18px; }</style>", unsafe_allow_html=True)

# ⬛ Streamlit Sidebar - 전체 단원 선택
st.sidebar.title("📚 전체 전략 모듈")
modules = {
    "1. 기본 정보 분석": module_01.run,
    "2. 재무 실적 분석": module_02.run,
    "3. 통합 전략 판단": module_03.run,
    "4. 자동 포트 구성": module_04.run,
    "5. 시장 심리 분석": module_05.run,
    "6. 전략 전환 탐지": module_06.run,
    "7. 시각화 및 보고서": module_07.run,
    "8. 자동 백테스트": module_08.run,
    "9. 리스크 분석": module_09.run,
    "10. 결과 저장 & 리포트": module_10.run,
    "11. 초고속 대규모 백테스트": module_11.run,
    "12. 전략 트리거 자동화": module_12.run,
    "13. 기술 분석 모듈": module_13.run,
    "14. 진입/청산 타이밍 예측": module_14.run,
    "15. 매크로 반영 구조": module_15.run,
    "16. ETF 전략 자동화": module_16.run,
    "17. 옵션/파생 전략": module_17.run,
    "18. AI 기반 자산배분": module_18.run,
    "19. 매크로 기반 전략 적응": module_19.run,
    "20. 환율·금리 동태 분석": module_20.run,
    "21. 유동성 사이클 감지": module_21.run,
    "22. 위기 예측 시나리오": module_22.run,
    "23. 산업 로테이션 시스템": module_23.run,
    "24. 수급 기반 매매 전략": module_24.run,
    "25. 시장 심리 사이클 추적": module_25.run,
    "26. 기회/비매매 구간 판단": module_26.run,
    "27. 투자 루틴 & 성장 피드백": module_27.run,
    "28. 자기주도 전략 생성 시스템": module_28.run,
    "29. 전략 시나리오 & 시뮬레이션": module_29.run,
    "30. 자기지능 강화 & 메타학습": module_30.run,
}
selected_module = st.sidebar.selectbox("🧩 단원 선택", list(modules.keys()))
st.sidebar.markdown("---")

# ⬛ 단원 실행
st.title("📈 AI 기반 퀀트 전략 시스템")
st.subheader(f"🔍 현재 실행 중: {selected_module}")
modules[selected_module]()

# ⬛ 하단 Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; font-size: 13px; color: gray;'>"
    "© 2025 AI Quant System | 전략은 도구일 뿐, 판단은 당신의 몫입니다."
    "</div>",
    unsafe_allow_html=True
)