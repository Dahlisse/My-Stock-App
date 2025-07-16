# module_15.py

import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity

# 매크로 데이터 수집 예시 (API 연동은 app.py 또는 secrets.toml에서 처리 예정)
def fetch_macro_data():
    # 여기는 예시용 데이터로 대체 (실제론 API 사용)
    data = {
        'date': pd.date_range(end=datetime.today(), periods=180, freq='D'),
        'interest_rate': np.random.uniform(1.0, 5.0, size=180),
        'cpi': np.random.uniform(1.5, 6.0, size=180),
        'oil_price': np.random.uniform(60, 120, size=180),
        'usd_krw': np.random.uniform(1100, 1400, size=180),
    }
    return pd.DataFrame(data)

# 최근 시점 데이터 점수화 (0~1 정규화)
def score_macro_variables(df, user_profile=None):
    recent = df.iloc[-30:].copy()
    scaler = MinMaxScaler()
    normed = scaler.fit_transform(recent[['interest_rate', 'cpi', 'oil_price', 'usd_krw']])
    scores = dict(zip(['interest_rate', 'cpi', 'oil_price', 'usd_krw'], normed[-1]))

    # 사용자 성향 가중치 반영
    if user_profile:
        if user_profile.get('risk_aversion') == 'high':
            scores['interest_rate'] *= 1.2  # 보수형: 금리에 민감
        if user_profile.get('sensitivity') == 'inflation':
            scores['cpi'] *= 1.3
    return scores

# 변수 조합 기반 시나리오 인식
def interpret_macro_conditions(scores):
    ir = scores['interest_rate']
    cpi = scores['cpi']
    if ir > 0.7 and cpi > 0.7:
        return "긴축 시나리오", "금리와 인플레이션이 모두 높은 국면 → 가치주 중심 전략 적합"
    elif ir > 0.7 and cpi < 0.4:
        return "제한적 긴축", "금리는 높지만 인플레이션은 안정 → 배당·고정수익 전략 유효"
    elif ir < 0.3 and cpi > 0.6:
        return "인플레이션 위험", "저금리-고CPI → 원자재/리얼에셋 비중 확대 필요"
    else:
        return "중립 또는 혼조", "매크로 변화가 뚜렷하지 않음 → 전략 유지 or 보수적 전환 권장"

# 과거 유사 시장 국면 인식
def detect_similar_market(df, current_vector):
    historical_scenarios = {
        '2008_crisis': [0.9, 0.8, 0.7, 0.6],
        '2011_euro': [0.7, 0.7, 0.6, 0.5],
        '2020_covid': [0.3, 0.9, 0.4, 0.7]
    }
    similarities = {
        year: cosine_similarity([current_vector], [vec])[0][0]
        for year, vec in historical_scenarios.items()
    }
    best_match = max(similarities, key=similarities.get)
    return best_match, similarities[best_match]

# 전략 매핑 함수
def recommend_strategy(scores):
    if scores['interest_rate'] > 0.7 and scores['cpi'] > 0.7:
        return "가치주 전략", "금리와 CPI가 높아 방어적 가치주 중심 포트가 유리합니다."
    elif scores['cpi'] > 0.7 and scores['oil_price'] > 0.6:
        return "원자재 중심 전략", "원자재 가격과 인플레이션 급등 구간입니다."
    elif scores['usd_krw'] > 0.8:
        return "수출 중심 전략", "환율 급등기 → 수출주 중심 전략이 유리합니다."
    else:
        return "중립 전략", "현 시점에서는 공격/수비 전략을 명확히 구분하기 어렵습니다."

# 최종 통합 해석 함수
def macro_analysis_pipeline(user_profile=None):
    df = fetch_macro_data()
    scores = score_macro_variables(df, user_profile)
    scenario_name, scenario_explanation = interpret_macro_conditions(scores)
    current_vector = list(scores.values())
    match_name, match_score = detect_similar_market(df, current_vector)
    strategy, strategy_comment = recommend_strategy(scores)

    return {
        'macro_scores': scores,
        'scenario': scenario_name,
        'scenario_explanation': scenario_explanation,
        'similar_past': match_name,
        'similarity_score': round(match_score, 3),
        'recommended_strategy': strategy,
        'strategy_explanation': strategy_comment
    }