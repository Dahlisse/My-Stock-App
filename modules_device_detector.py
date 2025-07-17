# modules/modules_device_detector.py

from device_detector import DeviceDetector
from user_agents import parse
import streamlit as st


def detect_device_info(user_agent: str) -> dict:
    """
    사용자 User-Agent 문자열을 바탕으로 장치 정보 분석
    """
    try:
        device = DeviceDetector(user_agent).parse()
        user_agent_parsed = parse(user_agent)

        device_info = {
            "device_type": device.device_type() or "unknown",
            "os_name": device.os_name() or "unknown",
            "os_version": device.os_version() or "unknown",
            "browser_name": device.client_name() or "unknown",
            "browser_version": device.client_version() or "unknown",
            "is_mobile": user_agent_parsed.is_mobile,
            "is_tablet": user_agent_parsed.is_tablet,
            "is_pc": user_agent_parsed.is_pc,
            "is_touch_capable": user_agent_parsed.is_touch_capable,
            "brand": device.brand_name() or "unknown",
            "model": device.model() or "unknown"
        }

    except Exception as e:
        # 분석 실패 시 기본값 반환
        device_info = {
            "device_type": "unknown",
            "os_name": "unknown",
            "os_version": "unknown",
            "browser_name": "unknown",
            "browser_version": "unknown",
            "is_mobile": False,
            "is_tablet": False,
            "is_pc": False,
            "is_touch_capable": False,
            "brand": "unknown",
            "model": "unknown"
        }
        st.warning(f"디바이스 정보 분석 실패: {e}")

    return device_info


def get_device_class(device_info: dict) -> str:
    """
    장치 정보에 기반한 사용자 분류
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
    장치에 따라 추천되는 전략 조정 방향을 안내
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
    st.markdown("### 📡 사용자 디바이스 분석")

    user_agent_input = st.text_input(
        "User-Agent 문자열 입력 (자동 감지 실패 시 수동 입력)",
        value=st.session_state.get("user_agent", "")
    )

    if not user_agent_input:
        st.info("📌 User-Agent 문자열을 입력하거나 브라우저에서 자동 제공되도록 설정하세요.")
        return

    device_info = detect_device_info(user_agent_input)
    render_device_banner(device_info)
    strategy_hint = device_adjusted_strategy(device_info)
    st.success(f"💡 전략 UX 권장: {strategy_hint}")