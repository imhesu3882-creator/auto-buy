"""
==========================================================
 AI AUTO TRADER
 config.py
----------------------------------------------------------
 프로젝트 전체 설정 (모의투자 서버 주소로 수정 완료)
==========================================================
"""

# ==========================================================
# 한국투자증권 API
# ==========================================================
# 방금 넣으셨던 모의투자 APP KEY를 다시 넣어주세요
APP_KEY = "PSJbO5Jd83iOL0JbEeg13LWg58OvdIobJorc"

# 방금 넣으셨던 모의투자 APP SECRET를 다시 넣어주세요
APP_SECRET = "yCcCYagqkZpkvMxvQtIOXFG5mp1nGXTu47cGD+5UObiX/0PjtWX1ViRvKMgaMkY1nXBa7NM8nTaR82nhgwomwunBmZOVRAvx6rfKirR87HoZajoM2wLAh36Wl7zIaU00YUBG2IBRzePyERcOWjXyJ2Qo1ID6CHRNj6leqvTqgp9NhdOc1cA="

# 실제 주문 사용 여부
# False = 가상매매만 수행 (현재 상태)
REAL_TRADING = False

# ==========================================================
# API 서버
# ==========================================================
REAL_BASE_URL = "https://openapi.koreainvestment.com:9443"
VIRTUAL_BASE_URL = "https://openapivts.koreainvestment.com:29443"

# [핵심 수정] 모의투자 키를 사용할 때는 반드시 VIRTUAL 서버 주소를 바라봐야 합니다.
BASE_URL = VIRTUAL_BASE_URL

# ==========================================================
# 투자금
# ==========================================================
START_BALANCE = 10_000_000
INVEST_PER_TRADE = 1_000_000
MIN_CASH = 500_000

# ==========================================================
# 관심종목 (종목명 : 종목코드)
# ==========================================================
STOCKS = {
    "삼성전자": "005930",
    "SK하이닉스": "000660",
    "삼성전기": "009150",
    "LG CNS": "064400"
}

# 새로고침 주기 (초)
REFRESH_SECONDS = 1

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
BUY_SCORE = 80
SELL_SCORE = 25

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
