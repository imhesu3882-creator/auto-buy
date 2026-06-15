"""
==========================================================
 AI AUTO TRADER
 config.py (최종 완성본)
----------------------------------------------------------
 프로젝트 전체 설정 (TICKERS 및 필수 키값 포함)
==========================================================
"""

# ==========================================================
# 한국투자증권 API
# ==========================================================
# 발급받으신 모의투자 APP KEY를 입력하세요
APP_KEY = "PSJbO5Jd83iOL0JbEeg13LWg58OvdIobJorc"

# 발급받으신 모의투자 APP SECRET를 입력하세요
APP_SECRET = "yCcCYagqkZpkvMxvQtIOXFG5mp1nGXTu47cGD+5UObiX/0PjtWX1ViRvKMgaMkY1nXBa7NM8nTaR82nhgwomwunBmZOVRAvx6rfKirR87HoZajoM2wLAh36Wl7zIaU00YUBG2IBRzePyERcOWjXyJ2Qo1ID6CHRNj6leqvTqgp9NhdOc1cA="

# 실제 주문 사용 여부
REAL_TRADING = False

# ==========================================================
# API 서버
# ==========================================================
REAL_BASE_URL = "https://openapi.koreainvestment.com:9443"
VIRTUAL_BASE_URL = "https://openapivts.koreainvestment.com:29443"

BASE_URL = VIRTUAL_BASE_URL

# ==========================================================
# 투자금
# ==========================================================
START_BALANCE = 10_000_000
INVEST_PER_TRADE = 1_000_000
MIN_CASH = 500_000

# ==========================================================
# 관심종목 및 티커 설정
# ==========================================================
STOCKS = {
    "삼성전자": "005930",
    "SK하이닉스": "000660",
    "삼성전기": "009150",
    "NAVER": "035420"
}

TICKERS = {
    "삼성전자": "005930.KS",
    "SK하이닉스": "000660.KS",
    "삼성전기": "009150.KS",
    "NAVER": "035420.KS"
}

# 새로고침 주기 (초)
REFRESH_SECONDS = 5

# 로그 및 지표 설정
MAX_HISTORY = 1000
MAX_TRADES = 500

RSI_PERIOD = 14
BUY_RSI = 30
SELL_RSI = 70

MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
USE_MACD = True

MA_SHORT = 5
MA_LONG = 20
USE_MOVING_AVERAGE = True

USE_VOLUME = True
VOLUME_MULTIPLIER = 2.0

STOP_LOSS = -3.0
TAKE_PROFIT = 5.0
TRAILING_STOP = 2.0

USE_SPLIT_BUY = True
SPLIT_BUY_COUNT = 3
USE_SPLIT_SELL = True
SPLIT_SELL_COUNT = 2

ENABLE_AI_SCORE = True
BUY_SCORE = 65
SELL_SCORE = 35

SCORE_RSI = 20
SCORE_MACD = 20
SCORE_VOLUME = 15
SCORE_MA = 15
SCORE_FOREIGN = 10
SCORE_NEWS = 10
SCORE_VOLATILITY = 10

USE_NEWS = False
NEWS_SCORE = 10
USE_FOREIGNER = False

ENABLE_NOTIFICATION = False
TELEGRAM_TOKEN = ""
TELEGRAM_CHAT_ID = ""
DISCORD_WEBHOOK = ""

# Render 설정
HOST = "0.0.0.0"
PORT = 10000
DEBUG = True
VERSION = "1.0.1"
PROJECT_NAME = "AI Auto Trader"
AUTHOR = "imhesu3882"
