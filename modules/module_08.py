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