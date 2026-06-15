"""
==========================================================
AI AUTO TRADER
indicators.py
----------------------------------------------------------
기술적 지표 계산 모듈

포함 기능
-------------------------
1. RSI
2. MACD
3. 이동평균 (SMA)
4. 거래 신호 보조
==========================================================
"""

import numpy as np
import pandas as pd

# ==========================================================
# RSI
# ==========================================================

def calculate_rsi(series: pd.Series, period: int = 14):

    delta = series.diff()

    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()

    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss

    rsi = 100 - (100 / (1 + rs))

    return rsi


# ==========================================================
# MACD
# ==========================================================

def calculate_macd(series: pd.Series,
                   fast: int = 12,
                   slow: int = 26,
                   signal: int = 9):

    ema_fast = series.ewm(span=fast).mean()

    ema_slow = series.ewm(span=slow).mean()

    macd = ema_fast - ema_slow

    signal_line = macd.ewm(span=signal).mean()

    hist = macd - signal_line

    return macd, signal_line, hist


# ==========================================================
# 이동평균
# ==========================================================

def moving_average(series: pd.Series, window: int):

    return series.rolling(window=window).mean()


# ==========================================================
# 골든크로스 / 데드크로스
# ==========================================================

def crossover(short_ma, long_ma):

    if len(short_ma) < 2 or len(long_ma) < 2:
        return None

    if short_ma.iloc[-2] < long_ma.iloc[-2] and short_ma.iloc[-1] > long_ma.iloc[-1]:
        return "golden_cross"

    if short_ma.iloc[-2] > long_ma.iloc[-2] and short_ma.iloc[-1] < long_ma.iloc[-1]:
        return "dead_cross"

    return None


# ==========================================================
# 종합 점수 계산 (AI용)
# ==========================================================

def calculate_score(rsi, macd_hist, volume_ratio):

    score = 50  # 기본값

    # RSI
    if rsi < 30:
        score += 20
    elif rsi > 70:
        score -= 20

    # MACD
    if macd_hist > 0:
        score += 15
    else:
        score -= 15

    # 거래량
    if volume_ratio > 2:
        score += 15

    return max(0, min(100, score))
