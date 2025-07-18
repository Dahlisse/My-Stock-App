import datetime
import json
import os

# 9.1 실시간 전략 추적
def track_portfolio_performance(performance_history: dict, new_data: dict):
    """
    performance_history: {date_str: 수익률}
    new_data: {date_str: 수익률} 추가 데이터
    """
    performance_history.update(new_data)
    # 최신 날짜 기준 30일 데이터 유지
    dates = sorted(performance_history.keys())[-30:]
    performance_history = {d: performance_history[d] for d in dates}
    return performance_history

# 9.1 성과 이탈 경고
def performance_alert(performance_history: dict, threshold_drop=0.05):
    """
    수익률 급락 경고 (예: 하루 5% 이상 하락 시)
    """
    sorted_dates = sorted(performance_history.keys())
    if len(sorted_dates) < 2:
        return None

    latest = performance_history[sorted_dates[-1]]
    prev = performance_history[sorted_dates[-2]]
    drop = prev - latest
    if drop >= threshold_drop:
        return f"⚠️ 경고: 최근 하루 수익률이 {drop*100:.2f}% 하락했습니다."
    return None

# 9.2 행동 안내 내비게이션
def generate_action_guide(current_state: dict):
    """
    current_state: {
        '전략_성능': float,
        '심리_상태': str,  # 예: '과열', '침체', '보통'
        '최근_변동성': float
    }
    """
    guide = "📊 현재 시장 상황 분석 결과:\n"
    if current_state.get('심리_상태') == '과열':
        guide += "- 매수 자제 권고, 위험 분산 필요\n"
    elif current_state.get('심리_상태') == '침체':
        guide += "- 매수 기회, 포트 확대 고려\n"
    else:
        guide += "- 관망 권고, 추가 신호 대기\n"

    if current_state.get('최근_변동성', 0.0) > 0.07:
        guide += "- 변동성 증가 주의, 리스크 관리 강화\n"

    return guide

# 9.2 음성 안내 (간단 예시)
def tts_guide(text: str):
    """
    TTS 변환 및 재생 함수 예시 (구현은 플랫폼별)
    """
    print(f"[TTS 안내]: {text}")

# 9.3 사용자별 히스토리 저장 (Streamlit Cloud용 예외처리 포함)
def save_user_history(user_id: str, data: dict, base_path='./user_histories'):
    try:
        os.makedirs(base_path, exist_ok=True)
        file_path = os.path.join(base_path, f"{user_id}_history.json")

        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
        else:
            history = {}

        history.update(data)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)

        return f"✅ 사용자 {user_id} 히스토리 저장 완료."
    except Exception as e:
        return f"⚠️ 히스토리 저장 실패: {e}"

# ====================
# 테스트용 실행 예시
# ====================
if __name__ == "__main__":
    # 9.1 성과 추적
    perf_hist = {
        '2025-07-01': 1.05,
        '2025-07-02': 1.07,
        '2025-07-03': 1.10
    }
    new_perf = {'2025-07-04': 1.02}
    perf_hist = track_portfolio_performance(perf_hist, new_perf)
    print("[성과 추적 결과]", perf_hist)

    # 9.1 성과 이탈 경고
    alert_msg = performance_alert(perf_hist, threshold_drop=0.05)
    if alert_msg:
        print("[경고 메시지]", alert_msg)

    # 9.2 행동 안내
    state = {
        '전략_성능': 0.85,
        '심리_상태': '과열',
        '최근_변동성': 0.08
    }
    guide_msg = generate_action_guide(state)
    print("[행동 안내]\n", guide_msg)

    # 9.2 TTS 안내
    tts_guide(guide_msg)

    # 9.3 사용자 히스토리 저장
    user_data = {
        '2025-07-01': {'포트수익률': 1.05, '전략점수': 80},
        '2025-07-02': {'포트수익률': 1.07, '전략점수': 82},
    }
    save_msg = save_user_history('user123', user_data)
    print(save_msg)
    
import streamlit as st
import pandas as pd
import time

def run():
    st.subheader("📘 9단원. 실행 추적 & AI 내비게이션")
    st.markdown("“투자는 지속적인 흐름이다. 안내와 추적까지 포함해야 한다.”")

    # ───────────────────────────────
    st.markdown("### 📡 9.1 실시간 전략 추적")

    st.markdown("""
    - 📊 **포트 수익률**: 실시간 반영  
    - 🚨 **성과 이탈 경고**: 수익률 -5% 이상 or 변동성 급등 시  
    - ⏱️ 주요 알림만 표시 (알람 과다 방지)
    """)

    # 예시 실시간 수익률 시뮬레이션
    st.write("🔄 실시간 수익률 추적 (예시)")
    progress_bar = st.progress(0)
    for i in range(0, 101, 20):
        progress_bar.progress(i)
        time.sleep(0.1)
    st.success("현재 수익률: +3.7% | 변동성: 안정적")

    st.divider()

    # ───────────────────────────────
    st.markdown("### 🧭 9.2 행동 안내 내비게이션")

    st.markdown("""
    - 매수/매도 권고 시점 자동 감지  
    - 자연어 기반 간결 가이드  
    - ✅ 초보자용 '간단 모드' 지원  
    - 📱 Safari 대응 및 음성 안내(TTS) 옵션 포함
    """)

    st.info("예시 안내: **“지금은 매수 자제 → 2주 뒤 재진입”**")

    st.divider()

    # ───────────────────────────────
    st.markdown("### 🗂️ 9.3 사용자별 히스토리 저장")

    st.markdown("""
    - 과거 종목 구성, 전략 점수, 수익률 로그 보존  
    - 사용자 구분: 예) 나 / 배우자 / 부모님  
    - 중복 저장 방지 및 요약 위주 저장
    """)

    sample_history = pd.DataFrame({
        "날짜": ["2025-07-01", "2025-07-10"],
        "전략": ["AI 최적화형", "공격 수익형"],
        "수익률": [3.4, 5.1],
        "심리 점수": [0.78, 0.82]
    })

    st.markdown("📅 **최근 전략 기록**")
    st.dataframe(sample_history, use_container_width=True)

    st.success("사용자 히스토리는 module_24와 연동되어 심리 기반 전략 조정에 활용됩니다.")