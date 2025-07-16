# module_14.py

import numpy as np
import pandas as pd
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import seaborn as sns

class TimingPredictor:
    def __init__(self, price_df: pd.DataFrame):
        self.df = price_df.copy()
        self.signals = pd.DataFrame(index=self.df.index)

    def compute_indicators(self):
        close = self.df['Close']
        self.signals['MA20'] = close.rolling(window=20).mean()
        self.signals['RSI'] = self._compute_rsi(close, 14)
        self.signals['MACD'] = self._compute_macd(close)
        self.signals['OBV'] = self._compute_obv(close, self.df['Volume'])

    def _compute_rsi(self, series, period=14):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
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
            if close[i] > close[i - 1]:
                obv.append(obv[-1] + volume[i])
            elif close[i] < close[i - 1]:
                obv.append(obv[-1] - volume[i])
            else:
                obv.append(obv[-1])
        return pd.Series(obv, index=close.index)

    def generate_entry_exit_signals(self):
        rsi = self.signals['RSI']
        macd = self.signals['MACD']
        ma = self.signals['MA20']
        close = self.df['Close']

        conditions = (
            (rsi < 30) & (macd > 0) & (close > ma)
        )
        self.signals['Entry'] = conditions

        exit_conditions = (
            (rsi > 70) | (macd < 0) | (close < ma)
        )
        self.signals['Exit'] = exit_conditions

    def signal_confidence_score(self, history_results: pd.DataFrame):
        """신호 발생 조건들의 과거 성과 통계를 기반으로 신뢰도 계산"""
        scores = {}
        for signal_type in ['Entry', 'Exit']:
            total = len(history_results)
            success = history_results[signal_type].sum()
            scores[signal_type] = round(success / total * 100, 2) if total > 0 else 0
        return scores

    def match_similar_patterns(self, reference_df: pd.DataFrame):
        """DTW 기반 과거 유사 구간 탐색"""
        scaler = MinMaxScaler()
        current_window = scaler.fit_transform(self.df['Close'].tail(60).values.reshape(-1, 1)).flatten()
        similarity_scores = []

        for start in range(len(reference_df) - 60):
            window = reference_df['Close'].iloc[start:start+60].values
            window_scaled = scaler.transform(window.reshape(-1, 1)).flatten()
            distance, _ = fastdtw(current_window, window_scaled, dist=euclidean)
            similarity_scores.append((start, distance))

        similarity_scores.sort(key=lambda x: x[1])
        top_match_idx, top_distance = similarity_scores[0]
        matched_period = reference_df.iloc[top_match_idx:top_match_idx+60]
        return matched_period, 1 - top_distance / np.max([s[1] for s in similarity_scores])

    def risk_forecast(self):
        """VaR, CVaR, MDD 계산"""
        returns = self.df['Close'].pct_change().dropna()
        var_95 = np.percentile(returns, 5)
        cvar_95 = returns[returns <= var_95].mean()
        cumulative = (1 + returns).cumprod()
        peak = cumulative.cummax()
        drawdown = (cumulative - peak) / peak
        mdd = drawdown.min()
        return round(var_95 * 100, 2), round(cvar_95 * 100, 2), round(mdd * 100, 2)

    def visualize_signals(self):
        """진입/청산 시점 시각화"""
        plt.figure(figsize=(14, 6))
        plt.plot(self.df['Close'], label='Close Price', alpha=0.7)
        plt.scatter(self.signals[self.signals['Entry']].index,
                    self.df['Close'][self.signals['Entry']], marker='^', color='green', label='Buy Signal')
        plt.scatter(self.signals[self.signals['Exit']].index,
                    self.df['Close'][self.signals['Exit']], marker='v', color='red', label='Sell Signal')
        plt.legend()
        plt.title('Entry & Exit Timing Signals')
        plt.tight_layout()
        plt.grid()
        plt.show()

    def market_phase_weighting(self, macro_signal: str):
        """시장 국면 인식 기반 지표 가중치 조정 예시"""
        if macro_signal == 'Bull':
            weight = {'RSI': 0.4, 'MACD': 0.3, 'MA': 0.2, 'OBV': 0.1}
        elif macro_signal == 'Bear':
            weight = {'RSI': 0.1, 'MACD': 0.2, 'MA': 0.4, 'OBV': 0.3}
        else:
            weight = {'RSI': 0.25, 'MACD': 0.25, 'MA': 0.25, 'OBV': 0.25}
        return weight