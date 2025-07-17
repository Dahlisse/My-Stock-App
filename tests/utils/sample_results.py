# utils/sample_results.py

"""
Sample results and mock outputs for testing and development purposes.
Used to simulate realistic outputs without running full computations.
"""

sample_portfolio = {
    'AAPL': 0.25,
    'MSFT': 0.20,
    'GOOG': 0.15,
    'AMZN': 0.10,
    'TSLA': 0.10,
    'JNJ': 0.10,
    'V': 0.10,
}

sample_backtest_summary = {
    'start_date': '2018-01-01',
    'end_date': '2023-12-31',
    'total_return': 0.85,
    'annualized_return': 0.12,
    'max_drawdown': -0.15,
    'sharpe_ratio': 1.35,
    'calmar_ratio': 0.80,
    'volatility': 0.18,
}

sample_strategy_performance = {
    'strategy_name': 'Momentum Growth',
    'cagr': 0.14,
    'max_drawdown': -0.13,
    'sharpe_ratio': 1.4,
    'win_rate': 0.62,
    'average_return_per_trade': 0.015,
    'trade_count': 120,
}

sample_market_sentiment = {
    'fear_greed_index': 55,
    'vix': 18.5,
    'short_interest_ratio': 0.12,
    'news_sentiment_score': 0.03,
}

sample_user_feedback = {
    'user_id': 'test_user',
    'strategy_used': 'Value + Dividend',
    'feedback_score': 4.2,
    'comments': 'Stable performance, less volatility than expected.',
    'date': '2025-07-15',
}