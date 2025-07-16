# module_19.py

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

from datetime import datetime
import yfinance as yf


class MacroDataManager:
    """
    19.1 경제지표 시계열 수집 및 구조화
    """
    def __init__(self):
        self.indicators = {}

    def load_macro_data(self):
        # 예시: 금리(CPI는 경제지표 API로 연동 가능)
        self.indicators['interest_rate'] = self.mock_data('interest_rate')
        self.indicators['cpi'] = self.mock_data('cpi')
        self.indicators['unemployment'] = self.mock_data('unemployment')
        self.indicators['oil'] = self.mock_data('oil')
        self.indicators['pmis'] = self.mock_data('pmis')
        self.indicators['exchange_rate'] = self.mock_data('exchange_rate')

        return self.indicators

    def mock_data(self, name):
        # 실제 구현 시 API 연동 또는 경제지표 DB 연동
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
    def __init__(self):
        self.cluster_model = KMeans(n_clusters=4, random_state=42)

    def tag_macro_events(self, df_yoy_changes):
        scaler = StandardScaler()
        scaled = scaler.fit_transform(df_yoy_changes)
        clusters = self.cluster_model.fit_predict(scaled)

        df_yoy_changes['macro_cluster'] = clusters

        cluster_names = self._name_clusters(df_yoy_changes)
        df_yoy_changes['macro_tag'] = df_yoy_changes['macro_cluster'].map(cluster_names)

        return df_yoy_changes

    def _name_clusters(self, df):
        # 간단한 자동 태깅 로직 (확장 가능)
        mapping = {}
        for cluster_id in df['macro_cluster'].unique():
            sample = df[df['macro_cluster'] == cluster_id].mean()
            if sample['cpi'] > 0.03 and sample['interest_rate'] > 0.03:
                mapping[cluster_id] = '긴축'
            elif sample['cpi'] < 0 and sample['unemployment'] > 0.02:
                mapping[cluster_id] = '스태그플레이션'
            elif sample['oil'] > 0.05:
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

    def train_classifier(self, df_macro, labels):
        X = df_macro.drop(columns=['macro_cluster', 'macro_tag'])
        y = labels
        self.classifier.fit(X, y)

    def predict_strategy(self, df_macro_latest):
        X_latest = df_macro_latest.drop(columns=['macro_cluster', 'macro_tag'])
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
            sliced = self.price_data.loc[start:end]
            drop = sliced.pct_change().cumsum().min()
            recovery = self._compute_recovery_duration(sliced)
            result[name] = {
                '최대 하락률': f"{drop:.2%}",
                '복구 기간': recovery
            }
        return pd.DataFrame(result).T

    def _compute_recovery_duration(self, data):
        cum_return = (data / data.iloc[0]) - 1
        peak = cum_return.cummax()
        drawdown = (cum_return - peak)

        # 복구 시점 계산
        for i in range(len(drawdown)):
            if drawdown[i] == 0:
                return f"{i}일"
        return "미복구"


# 🔄 통합 실행 함수
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