# module_20.py

import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volume import OnBalanceVolumeIndicator
from ta.volatility import BollingerBands


class EntryExitLabeler:
    """
    20.1 진입/청산 라벨링 구조 정교화
    """
    def __init__(self, window=5):
        self.window = window

    def generate_labels(self, price_series: pd.Series):
        future_returns = price_series.shift(-self.window) / price_series - 1
        entry_label = (future_returns > 0.03).astype(int)
        exit_label = (future_returns < -0.03).astype(int)
        return pd.DataFrame({
            'entry_label': entry_label,
            'exit_label': exit_label
        })


class TechnicalFeatureGenerator:
    """
    기술적 지표 기반 피처 생성
    """
    def __init__(self, df):
        self.df = df.copy()

    def generate_features(self):
        self.df['rsi'] = RSIIndicator(close=self.df['close']).rsi()
        macd = MACD(close=self.df['close'])
        self.df['macd'] = macd.macd()
        self.df['macd_signal'] = macd.macd_signal()
        self.df['obv'] = OnBalanceVolumeIndicator(close=self.df['close'], volume=self.df['volume']).on_balance_volume()
        bb = BollingerBands(close=self.df['close'])
        self.df['bb_high'] = bb.bollinger_hband()
        self.df['bb_low'] = bb.bollinger_lband()

        return self.df.dropna()


class EntryExitPredictor:
    """
    20.2 예측 모델 구조 비교 및 선택 가이드
    """
    def __init__(self):
        self.entry_model = GradientBoostingClassifier()
        self.exit_model = GradientBoostingClassifier()

    def train(self, X, y_entry, y_exit):
        self.entry_model.fit(X, y_entry)
        self.exit_model.fit(X, y_exit)

    def predict(self, X):
        entry_prob = self.entry_model.predict_proba(X)[:, 1]
        exit_prob = self.exit_model.predict_proba(X)[:, 1]
        return entry_prob, exit_prob

    def evaluate(self, X_test, y_test_entry, y_test_exit):
        y_pred_entry = self.entry_model.predict(X_test)
        y_pred_exit = self.exit_model.predict(X_test)
        return {
            'entry': classification_report(y_test_entry, y_pred_entry, output_dict=True),
            'exit': classification_report(y_test_exit, y_pred_exit, output_dict=True)
        }


class PredictionAnalyzer:
    """
    20.3 예측 vs 실현 결과 해석 시스템
    """
    def __init__(self, price_data):
        self.price = price_data

    def evaluate_return_profile(self, signals, window=5):
        entry_signals = signals['entry_prob'] > 0.6
        exit_signals = signals['exit_prob'] > 0.6

        returns = self.price.pct_change(periods=window).shift(-window)
        entry_returns = returns[entry_signals]
        exit_returns = returns[exit_signals]

        return {
            'entry': {
                'mean_return': entry_returns.mean(),
                'success_rate': (entry_returns > 0).mean()
            },
            'exit': {
                'mean_return': exit_returns.mean(),
                'success_rate': (exit_returns < 0).mean()
            }
        }


# 🔄 전체 파이프라인 실행 함수
def run_module_20(df):
    """
    df: DataFrame with ['close', 'volume']
    """
    labeler = EntryExitLabeler()
    features_df = TechnicalFeatureGenerator(df).generate_features()
    labels = labeler.generate_labels(features_df['close'])

    # 병합
    data = features_df.join(labels).dropna()
    X = data[['rsi', 'macd', 'macd_signal', 'obv', 'bb_high', 'bb_low']]
    y_entry = data['entry_label']
    y_exit = data['exit_label']

    X_train, X_test, y_entry_train, y_entry_test, y_exit_train, y_exit_test = train_test_split(
        X, y_entry, y_exit, test_size=0.2, random_state=42
    )

    predictor = EntryExitPredictor()
    predictor.train(X_train, y_entry_train, y_exit_train)

    evaluation = predictor.evaluate(X_test, y_entry_test, y_exit_test)

    entry_prob, exit_prob = predictor.predict(X_test)
    signal_df = pd.DataFrame({'entry_prob': entry_prob, 'exit_prob': exit_prob}, index=X_test.index)

    analyzer = PredictionAnalyzer(df['close'].loc[X_test.index])
    return_analysis = analyzer.evaluate_return_profile(signal_df)

    return {
        'entry_exit_report': evaluation,
        'return_analysis': return_analysis,
        'predicted_signals': signal_df
    }
    
import streamlit as st

def run():
    st.header("📘 20단원. 진입/청산 예측 모델링 시스템")
    st.markdown("""
    “시간이 곧 수익이다. 예측은 기회보다 정확도다.”

    - 20.1 진입/청산 라벨링 구조 정교화  
      기술지표 기반 라벨링 (MACD, RSI 등)  
      지연/누수 방지, 실거래 시점 반영  
      가격 행동 기반 비정형 라벨 추가

    - 20.2 예측 모델 구조 비교 및 선택 가이드  
      트리(XGBoost), 순환(LSTM), Transformer 비교  
      전략 실행 기준 평가 (정확도 + 수익률)  
      슬리피지, 거래비용 포함 손익률 계산

    - 20.3 예측 vs 실현 결과 해석 시스템  
      예측 성공 확률 vs 실제 수익 비교  
      보유 기간별 평균 기대 수익 분석  
      실패 케이스 분류 (시장 왜곡 등)  
      피드백 데이터 자동 생성 및 학습 루프 설계
    """)