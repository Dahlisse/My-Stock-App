import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

from datetime import datetime


class MacroDataManager:
    """
    19.1 경제지표 시계열 수집 및 구조화
    """
    def __init__(self):
        self.indicators = {}

    def load_macro_data(self):
        self.indicators['interest_rate'] = self.mock_data('interest_rate')
        self.indicators['cpi'] = self.mock_data('cpi')
        self.indicators['unemployment'] = self.mock_data('unemployment')
        self.indicators['oil'] = self.mock_data('oil')
        self.indicators['pmis'] = self.mock_data('pmis')
        self.indicators['exchange_rate'] = self.mock_data('exchange_rate')
        return self.indicators

    def mock_data(self, name):
        np.random.seed(hash(name) % 99999)
        date_range = pd.date_range(start="2015-01-01", periods=100, freq='M')
        values = np.random.normal(loc=2.0, scale=1.0, size=len(date_range))
        return pd.Series(values, index=date_range, name=name)

    def compute_yoy_changes(self):
        yoy_changes = {}
        for name, series in self.indicators.items():
            yoy = series.pct_change(12).dropna()
            yoy_changes[name] = yoy
        return pd.DataFrame(yoy_changes)


class MacroEventTagger:
    """
    19.1 이벤트 클러스터링 및 자동 태깅
    """
    def __init__(self, n_clusters=4):
        self.cluster_model = KMeans(n_clusters=n_clusters, random_state=42)

    def tag_macro_events(self, df_yoy_changes):
        scaler = StandardScaler()
        scaled = scaler.fit_transform(df_yoy_changes)
        clusters = self.cluster_model.fit_predict(scaled)

        df_yoy_changes = df_yoy_changes.copy()
        df_yoy_changes['macro_cluster'] = clusters
        df_yoy_changes['macro_tag'] = df_yoy_changes['macro_cluster'].map(
            self._name_clusters(df_yoy_changes)
        )

        return df_yoy_changes

    def _name_clusters(self, df):
        mapping = {}
        for cluster_id in df['macro_cluster'].unique():
            sample = df[df['macro_cluster'] == cluster_id].mean()
            if sample.get('cpi', 0) > 0.03 and sample.get('interest_rate', 0) > 0.03:
                mapping[cluster_id] = '긴축'
            elif sample.get('cpi', 0) < 0 and sample.get('unemployment', 0) > 0.02:
                mapping[cluster_id] = '스태그플레이션'
            elif sample.get('oil', 0) > 0.05:
                mapping[cluster_id] = '인플레 + 유가상승'
            else:
                mapping[cluster_id] = '중립'
        return mapping


class MacroDrivenStrategySelector:
    """
    19.2 매크로 기반 전략 분기 시스템
    """
    def __init__(self):
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)

    def train_classifier(self, df_macro, labels, strategy_label_col='label'):
        X = df_macro.drop(columns=['macro_cluster', 'macro_tag'], errors='ignore')
        y = labels[strategy_label_col] if isinstance(labels, pd.DataFrame) else labels
        self.classifier.fit(X, y)

    def predict_strategy(self, df_macro_latest):
        X_latest = df_macro_latest.drop(columns=['macro_cluster', 'macro_tag'], errors='ignore')
        return self.classifier.predict(X_latest)[0]


class CrisisResilienceAnalyzer:
    """
    19.3 과거 위기 복원 테스트
    """
    def __init__(self, price_data):
        self.price_data = price_data

    def simulate_crisis_impact(self, crisis_periods):
        result = {}

        for name, (start, end) in crisis_periods.items():
            if start not in self.price_data.index or end not in self.price_data.index:
                result[name] = {
                    '최대 하락률': "데이터 없음",
                    '복구 기간': "측정 불가"
                }
                continue

            sliced = self.price_data.loc[start:end]
            drop = sliced.pct_change().cumsum().min()
            recovery = self._compute_recovery_duration(sliced)
            result[name] = {
                '최대 하락률': f"{drop:.2%}",
                '복구 기간': recovery
            }

        return pd.DataFrame(result).T

    def _compute_recovery_duration(self, data):
        try:
            base = data.iloc[0]
            cum_return = (data / base) - 1
            peak = cum_return.cummax()
            drawdown = cum_return - peak

            for i in range(1, len(drawdown)):
                if drawdown.iloc[i] == 0:
                    return f"{i}일"
            return "미복구"
        except Exception:
            return "오류"


# 🔄 전체 통합 실행 함수
def run_module_19(price_data, labels):
    manager = MacroDataManager()
    tagger = MacroEventTagger()
    selector = MacroDrivenStrategySelector()
    crisis = CrisisResilienceAnalyzer(price_data)

    macro_df = manager.load_macro_data()
    yoy_df = manager.compute_yoy_changes()
    tagged_df = tagger.tag_macro_events(yoy_df)
    selector.train_classifier(tagged_df, labels)

    current_macro = tagged_df.tail(1)
    predicted_strategy = selector.predict_strategy(current_macro)

    crisis_periods = {
        '리먼': ('2008-09-01', '2009-03-01'),
        '코로나': ('2020-02-01', '2020-08-01'),
        'SVB': ('2023-03-01', '2023-06-01')
    }

    crisis_results = crisis.simulate_crisis_impact(price_data)

    return {
        '매크로 태깅': tagged_df.tail(3),
        '추천 전략': predicted_strategy,
        '위기 복원력': crisis_results
    }
    
import streamlit as st

def run():
    st.header("📘 19단원. 매크로 기반 전략 적응 시스템")
    st.markdown("""
    “시장보다 한 걸음 먼저 움직이게 하라.”

    - 19.1 경제지표 시계열 수집 및 구조화  
      금리, CPI, 실업률, 환율, 유가, PMI 등  
      전년 대비 변화율 동태적 이벤트 감지  
      이벤트 클러스터링 (예: 스태그플레이션 태깅)

    - 19.2 매크로 기반 전략 분기 시스템  
      조건 기반 분기 (금리↑, CPI↑ → 전략A)  
      머신러닝 + 수작업 정책 병행 Hybrid 구조  
      예: “PMI 하락→위험회피 전략 가동”

    - 19.3 과거 위기 복원 테스트  
      리먼, 코로나, SVB 위기 시기 데이터 복원  
      전략별 복원력 및 회복 속도 그래프  
      예: “전략A 코로나 하락 -19% → 6개월 내 복구”
    """)