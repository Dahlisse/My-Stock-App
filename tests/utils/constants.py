# utils/constants.py

"""
Constants used throughout the quant investment system.
Includes fixed parameters, thresholds, and config values.
"""

# Market related constants
MARKET_OPEN_HOUR = 9
MARKET_CLOSE_HOUR = 16
TRADING_DAYS_PER_YEAR = 252

# Risk thresholds
MAX_ACCEPTABLE_DRAWDOWN = 0.2  # 20%
MAX_VOLATILITY = 0.3  # 30%

# Strategy parameters
DEFAULT_TARGET_RETURN = 0.1  # 10%
DEFAULT_RISK_TOLERANCE = 'medium'

# Macroeconomic thresholds for event detection
CPI_HIGH_THRESHOLD = 3.0
UNEMPLOYMENT_HIGH_THRESHOLD = 7.0
INTEREST_RATE_HIGH_THRESHOLD = 2.5
PMI_LOW_THRESHOLD = 50.0

# Psychological index thresholds
FEAR_GREED_EXTREME_FEAR = 20
FEAR_GREED_EXTREME_GREED = 80

# Backtest simulation parameters
BACKTEST_START_DATE = '2000-01-01'
BACKTEST_END_DATE = '2024-12-31'

# Performance evaluation thresholds
SHARPE_RATIO_GOOD = 1.0
SHARPE_RATIO_EXCELLENT = 2.0

# Misc
SECONDS_IN_A_DAY = 86400