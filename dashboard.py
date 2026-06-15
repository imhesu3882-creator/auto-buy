import time
import requests
import pandas as pd

from config import *

# ==========================================================
# 상태 (가상 계좌)
# ==========================================================

account = {
    "balance": START_BALANCE,
    "positions": {},
    "trades": []
}

ACCESS_TOKEN = None
TOKEN_EXPIRE = 0
SESSION = requests.Session()

# ==========================================================
# 토큰
# ==========================================================

def is_token_valid():
    global ACCESS_TOKEN, TOKEN_EXPIRE
    return ACCESS_TOKEN is not None and time.time() < TOKEN_EXPIRE


def issue_token():
    global ACCESS_TOKEN, TOKEN_EXPIRE

    url = f"{BASE_URL}/oauth2/tokenP"

    payload = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET
    }

    res = SESSION.post(url, json=payload, timeout=10)

    if res.status_code != 200:
        raise Exception(res.text)

    data = res.json()

    ACCESS_TOKEN = data["access_token"]
    TOKEN_EXPIRE = time.time() + int(data["expires_in"]) - 60


def get_headers():
    if not is_token_valid():
        issue_token()

    return {
        "content-type": "application/json",
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET
    }

# ==========================================================
# 가격
# ==========================================================

PRICE_CACHE = {}
PRICE_CACHE_TIME = {}
CACHE_SEC = 1


def get_price(code):
    now = time.time()

    if code in PRICE_CACHE:
        if now - PRICE_CACHE_TIME.get(code, 0) < CACHE_SEC:
            return PRICE_CACHE[code]

    url = f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price"

    try:
        res = SESSION.get(
            url,
            headers=get_headers(),
            params={
                "fid_cond_mrkt_div_code": "J",
                "fid_input_iscd": code
            },
            timeout=10
        )

        data = res.json()
        price = int(data["output"]["stck_prpr"])

        PRICE_CACHE[code] = price
        PRICE_CACHE_TIME[code] = now

        return price

    except:
        return None


def get_multiple_prices(stock_dict):
    return {k: get_price(v) for k, v in stock_dict.items()}

# ==========================================================
# 캔들
# ==========================================================

def get_daily_chart(code, count=100):
    url = f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"

    try:
        res = SESSION.get(
            url,
            headers=get_headers(),
            params={
                "fid_cond_mrkt_div_code": "J",
                "fid_input_iscd": code,
                "fid_period_div_code": "D",
                "fid_org_adj_prc": "1"
            },
            timeout=10
        )

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

        return df.tail(count)

    except:
        return pd.DataFrame()

# ==========================================================
# 포트폴리오
# ==========================================================

def get_positions():
    return account["positions"]


def get_recent_trades(limit=20):
    return account["trades"][-limit:]


def get_total_asset(prices):
    asset = account["balance"]

    for name, pos in account["positions"].items():
        price = prices.get(name)
        if price:
            asset += price * pos["qty"]

    return asset


def get_total_pnl(prices):
    total = get_total_asset(prices)
    pnl = total - START_BALANCE
    return pnl, pnl / START_BALANCE * 100

# ==========================================================
# 핵심 실행 루프 (dashboard용)
# ==========================================================

def run_cycle():
    prices = get_multiple_prices(STOCKS)

    signals = {}

    for name, code in STOCKS.items():
        price = prices.get(name)

        signals[name] = {
            "action": "HOLD",
            "score": 50,
            "price": price or 0
        }

    return {
        "prices": prices,
        "signals": signals,
        "account": account
    }
