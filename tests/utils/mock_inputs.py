# utils/mock_inputs.py

"""
Mock input data for testing purposes across modules.
Includes sample data structures and example input values.
"""

def get_mock_stock_data():
    return {
        'AAPL': {'price': 150.0, 'volume': 1000000, 'sector': 'Technology'},
        'MSFT': {'price': 280.5, 'volume': 800000, 'sector': 'Technology'},
        'TSLA': {'price': 720.2, 'volume': 1200000, 'sector': 'Automotive'},
    }

def get_mock_macro_data():
    return {
        'CPI': 2.1,
        'Unemployment_Rate': 4.2,
        'Interest_Rate': 0.75,
        'PMI': 52.5,
        'USD_KRW': 1185.7,
    }

def get_mock_strategy_params():
    return {
        'target_return': 0.12,
        'max_drawdown': 0.15,
        'risk_tolerance': 'medium',
        'indicators': ['RSI', 'MACD', 'OBV'],
    }

def get_mock_user_preferences():
    return {
        'investment_style': 'growth',
        'risk_aversion': 0.3,
        'preferred_sectors': ['Technology', 'Healthcare'],
        'trade_frequency': 'weekly',
    }