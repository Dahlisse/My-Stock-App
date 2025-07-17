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
        try:
            new_row = {
                'date': pd.to_datetime(date),
                'FearGreed': float(fear_greed),
                'VIX': float(vix),
                'ShortRatio': float(short_ratio),
                'NewsSentiment': float(news_sentiment)
            }
            self.sentiment_history = pd.concat(
                [self.sentiment_history, pd.DataFrame([new_row])],
                ignore_index=True
            ).dropna().sort_values(by="date")
        except Exception as e:
            print(f"[오류] 심리 데이터 업데이트 실패: {e}")

    def classify_sentiment_phase(self):
        """
        공포 → 중립 → 탐욕 구간 분류 (0~100 스케일 기반)
        """
        if self.sentiment_history.empty:
            return "📭 데이터 없음"

        fg_index = self.sentiment_history['FearGreed'].iloc[-1]
        if fg_index < 30:
            return f"현재 심리 국면: 😨 공포 ({fg_index}점)"
        elif fg_index < 60:
            return f"현재 심리 국면: 😐 중립 ({fg_index}점)"
        else:
            # 탐욕 여부 판단 + 이행 속도 감지
            if len(self.sentiment_history) > 1:
                prev_fg = self.sentiment_history['FearGreed'].iloc[-2]
                delta = fg_index - prev_fg
            else:
                delta = 0
            return f"현재 심리 국면: 😎 탐욕 ({fg_index}점, 변화율 {round(delta, 2)})"

    def get_sentiment_timeseries(self):
        if self.sentiment_history.empty:
            return pd.DataFrame()
        return self.sentiment_history.set_index('date').sort_index()


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
        elif '중립' in phase_label and '탐욕' not in phase_label:
            return self.mapping['중립']
        else:
            return self.mapping['탐욕']

    def compute_fit_scores(self, strategy_name, history_df):
        """
        전략별 심리 국면 적합도 계산 (단순 스케일링 기반)
        """
        if history_df.empty or 'FearGreed' not in history_df.columns:
            return "📭 심리 데이터 부족"

        try:
            scaled_data = MinMaxScaler().fit_transform(
                history_df[['FearGreed', 'VIX', 'ShortRatio']].fillna(0)
            )
            avg_score = np.mean(scaled_data)

            phase_score = {
                '방어형': 1 - avg_score,
                '절대수익형': 0.9 - avg_score * 0.5,
                '중립형': 1 - abs(avg_score - 0.5),
                '퀀트모멘텀': avg_score * 0.8,
                '모멘텀': avg_score,
                '초단타형': min(1.0, avg_score * 1.2)
            }

            score = round(phase_score.get(strategy_name, 0), 2)
            return f"📊 전략 '{strategy_name}' → 심리 적합도: {score}"
        except Exception as e:
            return f"⚠️ 적합도 계산 오류: {e}"


class SentimentSurgeDetector:
    """
    25.3 심리 과열/침체 경고 시스템
    """

    def __init__(self):
        self.keyword_log = pd.DataFrame()

    def update_keyword_counts(self, date, keyword_counts: dict):
        try:
            row = {'date': pd.to_datetime(date)}
            row.update({k: int(v) for k, v in keyword_counts.items()})
            self.keyword_log = pd.concat(
                [self.keyword_log, pd.DataFrame([row])],
                ignore_index=True
            ).fillna(0).sort_values(by="date")
        except Exception as e:
            print(f"[오류] 키워드 카운트 업데이트 실패: {e}")

    def detect_overheat_or_fear(self, threshold=2.0):
        """
        키워드 급등 탐지 (예: 빚투, 영끌, 대박 등)
        """
        if self.keyword_log.shape[0] < 2:
            return "📭 키워드 데이터 부족"

        try:
            recent = self.keyword_log.tail(2)
            diffs = recent.iloc[1][1:] / (recent.iloc[0][1:] + 1e-6)
            alert_keywords = diffs[diffs > threshold].index.tolist()

            if alert_keywords:
                return f"🚨 과열 신호 감지: {', '.join(alert_keywords)} 키워드 급증"
            return "이상 없음"
        except Exception as e:
            return f"⚠️ 과열 감지 오류: {e}"

    def generate_strategy_suspension_advice(self, news_sentiment_score, vix_value):
        """
        과열 또는 공포 상황에 따른 전략 중단 권고
        """
        try:
            if news_sentiment_score > 0.8 and vix_value < 15:
                return "⚠️ 시장 과열: 단타 전략 일시 보류 권장"
            elif news_sentiment_score < 0.2 and vix_value > 30:
                return "⚠️ 시장 공포: 고위험 전략 리밸런싱 권고"
            else:
                return "✅ 전략 유지 가능"
        except Exception as e:
            return f"⚠️ 전략 판단 오류: {e}"