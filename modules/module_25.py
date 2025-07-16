# module_25.py

import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler


class MarketSentimentAnalyzer:
    """
    25.1 시장 심리 지표 수집 & 시각화
    """

    def __init__(self):
        self.sentiment_history = pd.DataFrame()

    def update_sentiment_data(self, date, fear_greed, vix, short_ratio, news_sentiment):
        new_row = {
            'date': pd.to_datetime(date),
            'FearGreed': fear_greed,
            'VIX': vix,
            'ShortRatio': short_ratio,
            'NewsSentiment': news_sentiment
        }
        self.sentiment_history = pd.concat([self.sentiment_history, pd.DataFrame([new_row])], ignore_index=True)

    def classify_sentiment_phase(self):
        """
        공포 → 중립 → 탐욕 구간 분류 (0~100 스케일 기반)
        """
        if self.sentiment_history.empty:
            return "데이터 없음"

        fg_index = self.sentiment_history['FearGreed'].iloc[-1]
        if fg_index < 30:
            return "현재 심리 국면: 공포 ({}점)".format(fg_index)
        elif fg_index < 60:
            return "현재 심리 국면: 중립 ({}점)".format(fg_index)
        else:
            # 이행 추세까지 고려
            prev_fg = self.sentiment_history['FearGreed'].iloc[-2] if len(self.sentiment_history) > 1 else fg_index
            delta = fg_index - prev_fg
            return f"현재 심리 국면: 중립 → 탐욕 이행 중 ({fg_index}점, 변화율 {round(delta, 2)})"

    def get_sentiment_timeseries(self):
        return self.sentiment_history.set_index('date')


class StrategySentimentMapper:
    """
    25.2 전략-심리 적합도 매핑 시스템
    """

    def __init__(self):
        self.mapping = {
            '공포': ['방어형', '절대수익형'],
            '중립': ['중립형', '퀀트모멘텀'],
            '탐욕': ['모멘텀', '초단타형']
        }

    def map_phase_to_strategies(self, phase_label):
        if '공포' in phase_label:
            return self.mapping['공포']
        elif '중립' in phase_label and '→ 탐욕' not in phase_label:
            return self.mapping['중립']
        else:
            return self.mapping['탐욕']

    def compute_fit_scores(self, strategy_name, history_df):
        """
        전략별 심리 국면 적합도 계산 (단순 스케일링 기반)
        """
        if history_df.empty:
            return "데이터 부족"

        scaler = MinMaxScaler()
        scaled = scaler.fit_transform(history_df[['FearGreed', 'VIX', 'ShortRatio']])
        avg_score = scaled.mean(axis=0).mean()
        phase_score = {
            '방어형': 1 - avg_score,
            '절대수익형': 0.9 - avg_score * 0.5,
            '중립형': 1 - abs(avg_score - 0.5),
            '퀀트모멘텀': avg_score * 0.8,
            '모멘텀': avg_score,
            '초단타형': min(1.0, avg_score * 1.2)
        }

        return f"전략 '{strategy_name}' → 현재 심리 국면 적합도: {round(phase_score.get(strategy_name, 0), 2)}"


class SentimentSurgeDetector:
    """
    25.3 심리 과열/침체 경고 시스템
    """

    def __init__(self):
        self.keyword_log = pd.DataFrame()

    def update_keyword_counts(self, date, keyword_counts: dict):
        row = {'date': pd.to_datetime(date)}
        row.update(keyword_counts)
        self.keyword_log = pd.concat([self.keyword_log, pd.DataFrame([row])], ignore_index=True)

    def detect_overheat_or_fear(self, threshold=2.0):
        """
        빚투, 영끌, 대박 등의 급증 탐지
        """
        if len(self.keyword_log) < 2:
            return "키워드 데이터 부족"

        recent = self.keyword_log.tail(2)
        diffs = recent.iloc[1][1:] / (recent.iloc[0][1:] + 1e-6)
        alert_keywords = diffs[diffs > threshold].index.tolist()

        if alert_keywords:
            return f"⚠️ 과열 신호 감지: {', '.join(alert_keywords)} 키워드 급증"
        return "이상 없음"

    def generate_strategy_suspension_advice(self, news_sentiment_score, vix_value):
        """
        과열 or 공포 상황 시 전략 중단/보류 제안
        """
        if news_sentiment_score > 0.8 and vix_value < 15:
            return "⚠️ 시장 과열: 단타 전략 보류 권고"
        elif news_sentiment_score < 0.2 and vix_value > 30:
            return "⚠️ 시장 공포: 위험 전략 리밸런싱 권고"
        else:
            return "전략 유지 가능"