# modules_device_detector.py

from device_detector import DeviceDetector
from user_agents import parse
import streamlit as st


def detect_device_info(user_agent: str) -> dict:
    """
    사용자 User-Agent 문자열을 바탕으로 장치 정보 분석
    """
    device = DeviceDetector(user_agent).parse()
    user_agent_parsed = parse(user_agent)

    device_info = {
        "device_type": device.device_type(),  # mobile / tablet / desktop / smarttv / console / car / camera / portable media player
        "os_name": device.os_name(),          # Windows / Android / iOS / etc.
        "os_version": device.os_version(),
        "browser_name": device.client_name(),
        "browser_version": device.client_version(),
        "is_mobile": user_agent_parsed.is_mobile,
        "is_tablet": user_agent_parsed.is_tablet,
        "is_pc": user_agent_parsed.is_pc,
        "is_touch_capable": user_agent_parsed.is_touch_capable,
        "brand": device.brand_name(),         # Apple, Samsung, etc.
        "model": device.model()
    }

    return device_info


def get_device_class(device_info: dict) -> str:
    """
    장치 정보에 기반한 사용자 분류
    - UI/UX 최적화 또는 행동 기반 전략 제안에 사용 가능
    """
    if device_info["is_mobile"]:
        return "mobile"
    elif device_info["is_tablet"]:
        return "tablet"
    elif device_info["is_pc"]:
        return "desktop"
    else:
        return "unknown"


def render_device_banner(device_info: dict):
    """
    Streamlit 상단에 사용자 장치 요약 정보를 표시
    - 전략 시각화, 디버깅 시 유저 환경 고려를 위함
    """
    st.markdown("#### 📱 사용자 장치 정보 요약")
    cols = st.columns(2)
    cols[0].markdown(f"**장치 유형:** {device_info['device_type']}")
    cols[0].markdown(f"**운영 체제:** {device_info['os_name']} {device_info['os_version']}")
    cols[0].markdown(f"**브라우저:** {device_info['browser_name']} {device_info['browser_version']}")
    cols[1].markdown(f"**터치 지원:** {'O' if device_info['is_touch_capable'] else 'X'}")
    cols[1].markdown(f"**브랜드/모델:** {device_info['brand']} {device_info['model']}")
    st.markdown("---")


def device_adjusted_strategy(device_info: dict) -> str:
    """
    장치에 따라 추천되는 전략 조정 방향을 안내 (30단원 자기지능 루프용)
    - 모바일: 간결한 전략, 터치 기반 시각화
    - 데스크탑: 복합전략, 시나리오 병렬 분석
    """
    if device_info["is_mobile"]:
        return "📲 간단하고 직관적인 시각화 중심 전략 권장 (모바일 환경 최적화)"
    elif device_info["is_pc"]:
        return "🖥️ 복합 조건 기반 전략 분석 가능 (데스크탑 환경 최적화)"
    elif device_info["is_tablet"]:
        return "📟 터치 기반 상호작용 전략 설정 추천 (태블릿)"
    else:
        return "⚙️ 환경 미확인 - 표준 전략으로 진행합니다."


# ✅ 앱 상단에서 사용할 통합 실행 예시 함수
def run_device_detector():
    user_agent = st.session_state.get("user_agent", None)
    if user_agent is None:
        # 개발 환경 또는 수동 입력 fallback
        user_agent = st.text_input("User Agent 입력", value=st.request_headers.get("User-Agent", "unknown"))

    device_info = detect_device_info(user_agent)
    render_device_banner(device_info)
    strategy_hint = device_adjusted_strategy(device_info)
    st.success(f"💡 전략 UX 권장: {strategy_hint}")