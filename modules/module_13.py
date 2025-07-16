# module_13.py

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
    if platform.system() == "Darwin":
        st.session_state['tts_enabled'] = True  # Safari용 플래그
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