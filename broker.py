"""
==========================================================
AI AUTO TRADER
broker.py
----------------------------------------------------------
한국투자증권 API

기능
-----------------------------------------
1. Access Token 관리
2. 실시간 현재가 조회
3. 일봉 조회
4. 분봉 조회
5. 거래량 조회
6. 여러 종목 조회
7. API 오류 복구
==========================================================
"""

import time
import requests
import pandas as pd

from config import *

# 전역 변수

ACCESS_TOKEN = None

TOKEN_EXPIRE = 0

SESSION = requests.Session()

# 토큰 확인

def token_valid():

    global ACCESS_TOKEN
    global TOKEN_EXPIRE

    if ACCESS_TOKEN is None:
        return False

    if time.time() >= TOKEN_EXPIRE:
        return False

    return True

# Access Token 발급

def issue_token():

    global ACCESS_TOKEN
    global TOKEN_EXPIRE

    url = f"{BASE_URL}/oauth2/tokenP"

    body = {

        "grant_type": "client_credentials",

        "appkey": APP_KEY,

        "appsecret": APP_SECRET

    }

    headers = {

        "content-type": "application/json"

    }

    response = SESSION.post(

        url,

        json=body,

        headers=headers,

        timeout=10

    )

    response.raise_for_status()

    result = response.json()

    ACCESS_TOKEN = result["access_token"]

    TOKEN_EXPIRE = time.time() + int(result["expires_in"]) - 60

    print("✅ Access Token 발급 완료")

    return ACCESS_TOKEN

# AI AUTO TRADER
# broker.py (2/8)
# API 공통 레이어 + 헤더 + 시세 기본 구조

import time
import requests

from config import *

# 세션

session = requests.Session()

ACCESS_TOKEN = None
TOKEN_EXPIRE = 0

# 토큰 체크

def is_token_valid():

    global ACCESS_TOKEN, TOKEN_EXPIRE

    if ACCESS_TOKEN is None:
        return False

    if time.time() >= TOKEN_EXPIRE:
        return False

    return True

# API 헤더 생성

def get_headers():

    if not is_token_valid():
        issue_token()

    return {
        "content-type": "application/json",
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
    }

# 토큰 발급 (기본)

def issue_token():

    global ACCESS_TOKEN, TOKEN_EXPIRE

    url = f"{BASE_URL}/oauth2/tokenP"

    payload = {

        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET

    }

    res = session.post(url, json=payload, timeout=10)

    if res.status_code != 200:
        raise Exception(f"Token Error: {res.text}")

    data = res.json()

    ACCESS_TOKEN = data["access_token"]
    TOKEN_EXPIRE = time.time() + int(data["expires_in"]) - 60

    print("✅ 토큰 발급 완료")

# AI AUTO TRADER
# broker.py (3/8)
# 실시간 현재가 조회 시스템

import time

# 캐시 (API 호출 제한 방지)

PRICE_CACHE = {}
PRICE_CACHE_TIME = {}

CACHE_SEC = 1  # 1초 캐싱

# 단일 종목 현재가 조회

def get_price(stock_code: str):

    now = time.time()

    # 캐시 확인
    if stock_code in PRICE_CACHE:
        if now - PRICE_CACHE_TIME.get(stock_code, 0) < CACHE_SEC:
            return PRICE_CACHE[stock_code]

    url = f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price"

    headers = get_headers()

    params = {
        "fid_cond_mrkt_div_code": "J",
        "fid_input_iscd": stock_code
    }

    try:

        res = session.get(url, headers=headers, params=params, timeout=10)

        data = res.json()

        price = int(data["output"]["stck_prpr"])

        PRICE_CACHE[stock_code] = price
        PRICE_CACHE_TIME[stock_code] = now

        return price

    except Exception as e:
        print(f"❌ 가격 조회 실패 {stock_code}: {e}")
        return None

# 여러 종목 한번에 조회

def get_multiple_prices(stock_dict: dict):

    result = {}

    for name, code in stock_dict.items():

        price = get_price(code)

        result[name] = price

    return result

# AI AUTO TRADER
# broker.py (4/8)
# OHLCV / 캔들 데이터 / 기술적 분석용 데이터

import pandas as pd

# 일봉 데이터

def get_daily_chart(stock_code: str, count: int = 100):

    url = f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"

    headers = get_headers()

    params = {
        "fid_cond_mrkt_div_code": "J",
        "fid_input_iscd": stock_code,
        "fid_period_div_code": "D",
        "fid_org_adj_prc": "1"
    }

    try:

        res = session.get(url, headers=headers, params=params, timeout=10)

        data = res.json()["output2"]

        df = pd.DataFrame(data)

        df = df.rename(columns={

            "stck_bsop_date": "date",
            "stck_oprc": "open",
            "stck_hgpr": "high",
            "stck_lwpr": "low",
            "stck_clpr": "close",
            "acml_vol": "volume"

        })

        df = df.astype({

            "open": float,
            "high": float,
            "low": float,
            "close": float,
            "volume": float

        })

        df = df.tail(count)

        return df

    except Exception as e:

        print(f"❌ 일봉 조회 실패 {stock_code}: {e}")
        return pd.DataFrame()

# 분봉 데이터 (1분봉)

def get_minute_chart(stock_code: str, count: int = 100):

    url = f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-time-itemchartprice"

    headers = get_headers()

    params = {
        "fid_cond_mrkt_div_code": "J",
        "fid_input_iscd": stock_code,
        "fid_pw_data_incu_yn": "N"
    }

    try:

        res = session.get(url, headers=headers, params=params, timeout=10)

        data = res.json()["output2"]

        df = pd.DataFrame(data)

        df = df.rename(columns={

            "stck_cntg_hour": "time",
            "stck_oprc": "open",
            "stck_hgpr": "high",
            "stck_lwpr": "low",
            "stck_prpr": "close",
            "cntg_vol": "volume"

        })

        df = df.astype({

            "open": float,
            "high": float,
            "low": float,
            "close": float,
            "volume": float

        })

        df = df.tail(count)

        return df

    except Exception as e:

        print(f"❌ 분봉 조회 실패 {stock_code}: {e}")
        return pd.DataFrame()

# AI AUTO TRADER
# broker.py (5/8)
# 멀티 종목 데이터 처리 + 안정화 레이어

import time
import pandas as pd

# 멀티 종목 캔들 데이터 수집

def get_all_daily_charts(stock_dict: dict, count: int = 100):

    result = {}

    for name, code in stock_dict.items():

        df = get_daily_chart(code, count)

        result[name] = df

        time.sleep(0.1)  # API 과부하 방지

    return result

# 멀티 종목 현재가 + 캔들 통합

def get_full_market_data(stock_dict: dict):

    prices = {}
    charts = {}

    for name, code in stock_dict.items():

        # 현재가
        price = get_price(code)

        # 캔들
        df = get_daily_chart(code, 60)

        prices[name] = price
        charts[name] = df

        time.sleep(0.1)

    return prices, charts

# 안전 호출 래퍼

def safe_call(func, *args, retry=3, delay=0.5, default=None):

    for i in range(retry):

        try:
            return func(*args)

        except Exception as e:
            print(f"⚠️ retry {i+1}/{retry} - {e}")
            time.sleep(delay)

    return default

# 안정화된 가격 조회

def safe_get_price(stock_code: str):

    return safe_call(get_price, stock_code, default=None)

# 안정화된 일봉 조회

def safe_get_daily(stock_code: str):

    return safe_call(get_daily_chart, stock_code, default=pd.DataFrame())

# AI AUTO TRADER
# broker.py (5/8)
# 멀티 종목 데이터 처리 + 안정화 레이어

import time
import pandas as pd

# 멀티 종목 캔들 데이터 수집

def get_all_daily_charts(stock_dict: dict, count: int = 100):

    result = {}

    for name, code in stock_dict.items():

        df = get_daily_chart(code, count)

        result[name] = df

        time.sleep(0.1)  # API 과부하 방지

    return result

# 멀티 종목 현재가 + 캔들 통합

def get_full_market_data(stock_dict: dict):

    prices = {}
    charts = {}

    for name, code in stock_dict.items():

        # 현재가
        price = get_price(code)

        # 캔들
        df = get_daily_chart(code, 60)

        prices[name] = price
        charts[name] = df

        time.sleep(0.1)

    return prices, charts

# 안전 호출 래퍼

def safe_call(func, *args, retry=3, delay=0.5, default=None):

    for i in range(retry):

        try:
            return func(*args)

        except Exception as e:
            print(f"⚠️ retry {i+1}/{retry} - {e}")
            time.sleep(delay)

    return default

# 안정화된 가격 조회

def safe_get_price(stock_code: str):

    return safe_call(get_price, stock_code, default=None)

# 안정화된 일봉 조회

def safe_get_daily(stock_code: str):

    return safe_call(get_daily_chart, stock_code, default=pd.DataFrame())

# AI AUTO TRADER
# broker.py (7/8)
# 포트폴리오 분석 / 손익 계산 / 평가 시스템
# 종목별 평가 손익

def get_position_pnl(current_prices: dict):

    result = {}

    for name, pos in account["positions"].items():

        price = current_prices.get(name)

        if price is None:
            continue

        buy_price = pos["avg_price"]
        qty = pos["qty"]

        pnl = (price - buy_price) * qty
        pnl_pct = ((price - buy_price) / buy_price) * 100

        result[name] = {

            "qty": qty,
            "avg_price": buy_price,
            "current_price": price,
            "pnl": pnl,
            "pnl_pct": pnl_pct

        }

    return result

# 총 손익

def get_total_pnl(current_prices: dict):

    total_asset = get_total_asset(current_prices)

    pnl = total_asset - START_BALANCE

    pnl_pct = (pnl / START_BALANCE) * 100

    return pnl, pnl_pct

# 포트폴리오 요약

def get_portfolio_summary(current_prices: dict):

    pnl, pnl_pct = get_total_pnl(current_prices)

    return {

        "balance": account["balance"],

        "total_asset": get_total_asset(current_prices),

        "pnl": pnl,

        "pnl_pct": pnl_pct,

        "positions_count": len(account["positions"]),

        "trade_count": len(account["trades"])

    }

# 최근 거래 N개

def get_recent_trades(limit: int = 20):

    return account["trades"][-limit:]

# 보유 종목 리스트

def get_positions():

    return account["positions"]

# AI AUTO TRADER
# broker.py (7/8)
# 포트폴리오 분석 / 손익 계산 / 평가 시스템
# 종목별 평가 손익

def get_position_pnl(current_prices: dict):

    result = {}

    for name, pos in account["positions"].items():

        price = current_prices.get(name)

        if price is None:
            continue

        buy_price = pos["avg_price"]
        qty = pos["qty"]

        pnl = (price - buy_price) * qty
        pnl_pct = ((price - buy_price) / buy_price) * 100

        result[name] = {

            "qty": qty,
            "avg_price": buy_price,
            "current_price": price,
            "pnl": pnl,
            "pnl_pct": pnl_pct

        }

    return result

# 총 손익

def get_total_pnl(current_prices: dict):

    total_asset = get_total_asset(current_prices)

    pnl = total_asset - START_BALANCE

    pnl_pct = (pnl / START_BALANCE) * 100

    return pnl, pnl_pct

# 포트폴리오 요약

def get_portfolio_summary(current_prices: dict):

    pnl, pnl_pct = get_total_pnl(current_prices)

    return {

        "balance": account["balance"],

        "total_asset": get_total_asset(current_prices),

        "pnl": pnl,

        "pnl_pct": pnl_pct,

        "positions_count": len(account["positions"]),

        "trade_count": len(account["trades"])

    }

# 최근 거래 N개

def get_recent_trades(limit: int = 20):

    return account["trades"][-limit:]

# 보유 종목 리스트

def get_positions():

    return account["positions"]
