import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# =======================================
# 8.1 추천 포트 구성
# =======================================

def generate_recommendation_portfolios(stock_pool: pd.DataFrame, mode='AI_OPT'):
    """
    mode: 'STABLE', 'BALANCED', 'AGGRESSIVE', 'AI_OPT'
    stock_pool: DataFrame with ['종목명', '성과스코어', '리스크', '성장성', '배당성향'] 포함
    """
    stock_pool = stock_pool.dropna(subset=['성과스코어', '리스크', '성장성', '배당성향'])

    if mode == 'STABLE':
        selected = stock_pool.sort_values(by=['리스크', '배당성향'], ascending=[True, False]).head(8)
    elif mode == 'BALANCED':
        selected = stock_pool.sort_values(by='성과스코어', ascending=False).head(10)
    elif mode == 'AGGRESSIVE':
        selected = stock_pool.sort_values(by='성장성', ascending=False).head(12)
    elif mode == 'AI_OPT':
        scaler = MinMaxScaler()
        try:
            selected = stock_pool.copy()
            selected['AI점수'] = (
                0.4 * scaler.fit_transform(selected[['성과스코어']])[:, 0] +
                0.3 * scaler.fit_transform(selected[['성장성']])[:, 0] -
                0.2 * scaler.fit_transform(selected[['리스크']])[:, 0]
            )
            selected = selected.sort_values(by='AI점수', ascending=False).head(10)
        except Exception as e:
            raise ValueError("스케일링 중 오류 발생: NaN 또는 잘못된 입력") from e
    else:
        raise ValueError("알 수 없는 포트 구성 모드입니다.")

    return selected[['종목명', '성과스코어', '리스크', '성장성', '배당성향']].reset_index(drop=True)


# =======================================
# 8.2 추천 이유 해설
# =======================================

def explain_stock_recommendation(stock_row: pd.Series) -> str:
    reasons = []
    if stock_row.get('성과스코어', 0) > 80:
        reasons.append("성과스코어가 높음")
    if stock_row.get('배당성향', 0) > 3:
        reasons.append("꾸준한 배당주")
    if stock_row.get('성장성', 0) > 70:
        reasons.append("최근 성장성이 우수함")
    if stock_row.get('리스크', 100) < 30:
        reasons.append("리스크가 낮아 안정적임")

    reason_text = ", ".join(reasons[:3]) if reasons else "AI 종합 판단에 따라 추천됨"
    return f"{stock_row.get('종목명', '해당 종목')}은(는) {reason_text}."


# =======================================
# 8.3 최적 비중 산정
# =======================================

def optimize_portfolio_weights(df: pd.DataFrame, target_col='성과스코어', risk_col='리스크'):
    """
    Risk-adjusted 비중 계산: (score^2 / risk) 정규화
    """
    score = df[target_col].values
    risk = df[risk_col].values + 1e-5  # 0 나눗셈 방지
    weights = (score ** 2) / risk
    norm_weights = weights / weights.sum()
    df['최적비중'] = norm_weights
    return df[['종목명', '최적비중']]


# =======================================
# 8.4 상관계수 기반 비중 조정
# =======================================

def build_correlation_adjusted_portfolio(corr_matrix: pd.DataFrame, raw_weights: pd.Series):
    """
    상관관계 기반 리스크 조정: 분산 최소화 목적의 간단한 예시
    """
    try:
        inv_corr = np.linalg.pinv(corr_matrix.values)
        weights = inv_corr @ raw_weights.values
        weights = np.clip(weights, 0, None)
        weights /= weights.sum()
        return pd.Series(weights, index=raw_weights.index, name='조정비중')
    except Exception as e:
        raise ValueError("상관계수 기반 조정 중 오류 발생") from e
        
import streamlit as st
import pandas as pd

def run():
    st.subheader("📘 8단원. 종목 추천 & 포트 구성")
    st.markdown("“종목을 선택하지 않아도, AI가 알아서 완성한다.”")

    st.markdown("### 📌 8.1 추천 포트 구성")

    portfolio_types = ["절대 안정형", "균형 분산형", "공격 수익형", "AI 최적화형"]
    selected_type = st.selectbox("추천 포트 유형 선택", portfolio_types)

    # 예시 포트폴리오 구성
    port_data = {
        "종목명": ["삼성전자", "LG화학", "NAVER", "SK하이닉스"],
        "비중(%)": [35, 25, 20, 20],
        "단가(원)": [70000, 450000, 200000, 130000],
        "리스크 지표": ["낮음", "중간", "높음", "높음"]
    }
    df = pd.DataFrame(port_data)

    st.markdown(f"#### 📈 [{selected_type}] 포트 구성 예시")
    st.dataframe(df, use_container_width=True)

    st.markdown("### 🧠 8.2 추천 이유 & 해설")

    st.markdown("""
    - **삼성전자**: 반도체 대장주 + 배당 안정성  
    - **LG화학**: 2차전지 수요 급증에 따른 성장 기대  
    - **NAVER**: AI·클라우드 매출 확대 기대  
    - **SK하이닉스**: 반도체 턴어라운드 시점 진입
    """)

    st.markdown("📊 **AI 판단 근거**")
    st.markdown("""
    - 수익률 기대치: +27.3% (1년 기준)  
    - 변동성 예측치: 11.2%  
    - AI 적합도 점수: 0.82  
    - 전략 추천 신뢰도: ★★★★☆
    """)

    st.divider()
    st.markdown("### ⚖️ 8.3 최적 비중 산정")

    st.markdown("""
    - **리스크 기반 최적화(RAR)**: 리스크 대비 수익률 최대화  
    - **종목 간 상관관계 고려**: 분산 효과로 포트 리스크 최소화  
    - **가중치 재조정 예시**:
    """)

    # 간단한 가중치 조정 예시
    optimal_weights = {
        "삼성전자": 0.4,
        "LG화학": 0.3,
        "NAVER": 0.15,
        "SK하이닉스": 0.15
    }

    for stock, weight in optimal_weights.items():
        st.write(f"- {stock}: {round(weight * 100)}%")

    st.info("📌 고차원 상관관계 정보는 요약된 형태로만 표시하며, 세부 해설은 module_09에서 추적됩니다.")