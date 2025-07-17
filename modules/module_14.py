# module_14.py

import numpy as np
import pandas as pd
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

class TimingPredictor:
    def __init__(self, price_df: pd.DataFrame):
        self.df = price_df.dropna().copy()
        self.signals = pd.DataFrame(index=self.df.index)

    def compute_indicators(self):
        close = self.df['Close']
        self.signals['MA20'] = close.rolling(window=20).mean()
        self.signals['RSI'] = self._compute_rsi(close)
        self.signals['MACD'] = self._compute_macd(close)
        self.signals['OBV'] = self._compute_obv(close, self.df['Volume'])

    def _compute_rsi(self, series, period=14):
        delta = series.diff()
        gain = delta.clip(lower=0).rolling(window=period).mean()
        loss = (-delta.clip(upper=0)).rolling(window=period).mean()
        rs = gain / (loss + 1e-10)
        return 100 - (100 / (1 + rs))

    def _compute_macd(self, series, short=12, long=26, signal=9):
        ema_short = series.ewm(span=short, adjust=False).mean()
        ema_long = series.ewm(span=long, adjust=False).mean()
        macd = ema_short - ema_long
        return macd - macd.ewm(span=signal, adjust=False).mean()

    def _compute_obv(self, close, volume):
        obv = [0]
        for i in range(1, len(close)):
            if close.iloc[i] > close.iloc[i - 1]:
                obv.append(obv[-1] + volume.iloc[i])
            elif close.iloc[i] < close.iloc[i - 1]:
                obv.append(obv[-1] - volume.iloc[i])
            else:
                obv.append(obv[-1])
        return pd.Series(obv, index=close.index)

    def generate_entry_exit_signals(self):
        rsi = self.signals['RSI']
        macd = self.signals['MACD']
        ma = self.signals['MA20']
        close = self.df['Close']

        self.signals['Entry'] = (rsi < 30) & (macd > 0) & (close > ma)
        self.signals['Exit'] = (rsi > 70) | (macd < 0) | (close < ma)

    def signal_confidence_score(self, history_results: pd.DataFrame):
        scores = {}
        for signal_type in ['Entry', 'Exit']:
            total = len(history_results)
            success = history_results[signal_type].sum()
            scores[signal_type] = round(success / total * 100, 2) if total > 0 else 0
        return scores

    def match_similar_patterns(self, reference_df: pd.DataFrame, window_size: int = 60):
        """DTW 기반 유사 패턴 탐색"""
        if len(self.df) < window_size or len(reference_df) < window_size:
            return None, 0.0

        scaler = MinMaxScaler()
        current_window = scaler.fit_transform(self.df['Close'].tail(window_size).values.reshape(-1, 1)).flatten()

        reference_close = reference_df['Close'].values
        ref_scaled = scaler.transform(reference_close.reshape(-1, 1)).flatten()

        similarity_scores = []
        for start in range(len(reference_close) - window_size):
            window = ref_scaled[start:start + window_size]
            distance, _ = fastdtw(current_window, window, dist=euclidean)
            similarity_scores.append((start, distance))

        if not similarity_scores:
            return None, 0.0

        similarity_scores.sort(key=lambda x: x[1])
        top_start, top_distance = similarity_scores[0]
        matched_period = reference_df.iloc[top_start:top_start + window_size]
        score = 1 - top_distance / (np.max([s[1] for s in similarity_scores]) + 1e-5)
        return matched_period, round(score * 100, 2)

    def risk_forecast(self):
        """VaR, CVaR, MDD 계산"""
        returns = self.df['Close'].pct_change().dropna()
        if len(returns) < 20:
            return None, None, None

        var_95 = np.percentile(returns, 5)
        cvar_95 = returns[returns <= var_95].mean()
        cumulative = (1 + returns).cumprod()
        peak = cumulative.cummax()
        drawdown = (cumulative - peak) / peak
        mdd = drawdown.min()
        return round(var_95 * 100, 2), round(cvar_95 * 100, 2), round(mdd * 100, 2)

    def visualize_signals(self):
        """진입/청산 시각화 (Streamlit 호환)"""
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(self.df['Close'], label='Close', alpha=0.7)
        entry_points = self.signals[self.signals['Entry']].index
        exit_points = self.signals[self.signals['Exit']].index

        ax.scatter(entry_points, self.df.loc[entry_points, 'Close'],
                   color='green', marker='^', label='Buy')
        ax.scatter(exit_points, self.df.loc[exit_points, 'Close'],
                   color='red', marker='v', label='Sell')
        ax.set_title('Entry/Exit Signals')
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)

    def market_phase_weighting(self, macro_signal: str):
        """시장 국면에 따른 지표 가중치 적용"""
        if macro_signal == 'Bull':
            return {'RSI': 0.4, 'MACD': 0.3, 'MA': 0.2, 'OBV': 0.1}
        elif macro_signal == 'Bear':
            return {'RSI': 0.1, 'MACD': 0.2, 'MA': 0.4, 'OBV': 0.3}
        return {'RSI': 0.25, 'MACD': 0.25, 'MA': 0.25, 'OBV': 0.25}