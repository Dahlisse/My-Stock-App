import streamlit as st
import platform

def apply_responsive_layout():
    """화면 크기에 따른 레이아웃 자동 적용"""
    st.markdown("""
        <style>
            @media (max-width: 768px) {
                .block-container {
                    padding-left: 0rem;
                    padding-right: 0rem;
                }
                .stButton>button, .stSelectbox, .stTextInput {
                    font-size: 16px !important;
                }
            }
        </style>
    """, unsafe_allow_html=True)

def safari_tts_patch():
    """Safari에서 음성 안내(TTS) 미작동 이슈 대응"""
    system = platform.system()
    if system == "Darwin":
        if 'tts_enabled' not in st.session_state:
            st.session_state['tts_enabled'] = True
        st.markdown("▶️ iOS Safari 환경에서는 일부 음성 안내가 제한될 수 있습니다. 설정에서 ‘음성 안내 활성화’를 확인하세요.")

def render_navigation_guide(mode="초심자"):
    """단계별 분석 흐름 UI + TTS 시나리오"""
    if mode == "초심자":
        st.info("① 진입 신호 감지 → ② 전략 선택 → ③ 포트 구성 → ④ 실행 가이드")
        st.markdown("🧠 **설명 모드**: 자연어로 현재 상태를 안내해드립니다.")
    elif mode == "전문가":
        st.success("전략 흐름: 신호 기반 진입 → 리밸런싱 → 트레이드오프 분석")
        st.markdown("📊 **기술적/수익률 기반 분석 우선 적용**")

def fix_ui_elements():
    """전략 요약 카드, 경고 메시지 등 상단 고정"""
    st.markdown("""
        <style>
            .fixed-top-card {
                position: -webkit-sticky;
                position: sticky;
                top: 0;
                background-color: #f7f7f7;
                z-index: 999;
                padding: 10px;
                border-bottom: 1px solid #ddd;
            }
        </style>
    """, unsafe_allow_html=True)

def render_fixed_top_cards(summary_text, warning_text=None):
    """요약/경고 카드 표시"""
    st.markdown('<div class="fixed-top-card">', unsafe_allow_html=True)
    st.markdown(f"✅ **전략 요약**: {summary_text}")
    if warning_text:
        st.markdown(f"⚠️ **경고**: {warning_text}")
    st.markdown('</div>', unsafe_allow_html=True)
    st.write("")  # 간격 확보용

def responsive_layout_for_stock_count(count):
    """종목 수에 따라 레이아웃 자동 조정"""
    if count > 20:
        st.warning("⚠️ 종목 수가 많아 일부 UI가 축소되어 표시됩니다.")
        st.markdown("""
            <style>
                .stDataFrame { font-size: 12px !important; }
            </style>
        """, unsafe_allow_html=True)
        
import streamlit as st

def run():
    st.subheader("📘 13. 전략 실행 시나리오 & 리스크 대응 시뮬레이션")
    st.markdown("“전략은 예측이 아니라 대응이다. 다양한 시나리오에서 작동해야 한다.”")

    st.markdown("### ✅ 13.1 실행 시나리오 선택")
    scenario = st.selectbox("📊 시뮬레이션할 시장 시나리오를 선택하세요", [
        "금리 급등기 (긴축 모드)",
        "경기 침체기 (실적 악화)",
        "기술주 랠리",
        "인플레이션 급등",
        "전반적 조정기 (시장 전반 하락)"
    ])

    st.markdown("### ✅ 13.2 전략 반응 시뮬레이션")
    if st.button("🚀 전략 시뮬레이션 실행"):
        st.info(f"선택된 시나리오: **{scenario}**")
        st.markdown("시뮬레이션 중... (예시 결과 표시)")

        # 예시 결과
        st.markdown("""
        **전략 반응 예시**  
        - 수익률 변화: `-3.5%`  
        - 변동성 증가: `+22%`  
        - 리밸런싱 발생 여부: `발생함`  
        - 포트폴리오 조정 방식: `핵심 종목 2개 교체`  
        """)

    st.markdown("### ✅ 13.3 리스크 이벤트 대응 시뮬레이션")
    st.markdown("- 실시간 위기 발생 시 어떻게 전략이 반응하는지 시뮬레이션합니다.")

    event = st.radio("💥 발생 이벤트를 선택하세요", [
        "러시아 지정학적 충돌",
        "미국 기준금리 추가 인상",
        "S&P 500 급락 (-7%)",
        "에너지 가격 급등"
    ])

    if st.button("🧪 리스크 대응 테스트"):
        st.success(f"전략이 **'{event}'** 상황에서 자동으로 포트폴리오를 리밸런싱했습니다.")
        st.markdown("- 리스크 감지 → 고변동 종목 제외 → 방어형 종목 비중 강화")
        st.markdown("- 전략 안정성 지표: `0.46 → 0.71` (회복 감지)")

    st.markdown("### ✅ 전략 이탈 감지 & 대안 전략 전환")
    st.markdown("""
    - Stability Index가 0.35 이하로 급락할 경우,
    - 대안 전략 자동 추천: ‘안정형 가치주 중심 전략’
    """)

    if st.button("🔄 전략 전환 보기"):
        st.warning("현재 전략 안정성 지표가 임계치 이하입니다. 전략 교체가 권장됩니다.")
        st.markdown("📌 **추천 전략**: 방어형 배당주 중심 / 리밸런싱 주기 90일")