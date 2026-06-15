import time
import requests
import pandas as pd
from config import *

# ==========================================================
# GLOBAL STATE
# ==========================================================

session = requests.Session()

ACCESS_TOKEN = None
TOKEN_EXPIRE = 0

account = {
    "balance": START_BALANCE,
    "positions": {},
    "trades": []
}

# ==========================================================
# TOKEN
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

    res = session.post(url, json=payload, timeout=10)
    res.raise_for_status()

    data = res.json()

    ACCESS_TOKEN = data["access_token"]
    TOKEN_EXPIRE = time.time() + int(data["expires_in"]) - 60

    print("✅ TOKEN 발급 완료")


def get_headers():
    if not is_token_valid():
        issue_token()

    return {
        "content-type": "application/json",
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
    }

# ==========================================================
# STOCK DATA
# ==========================================================

PRICE_CACHE = {}
PRICE_CACHE_TIME = {}
CACHE_SEC = 1


def get_price(stock_code: str):

    now = time.time()

    if stock_code in PRICE_CACHE:
        if now - PRICE_CACHE_TIME[stock_code] < CACHE_SEC:
            return PRICE_CACHE[stock_code]

    url = f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price"

    params = {
        "fid_cond_mrkt_div_code": "J",
        "fid_input_iscd": stock_code
    }

    try:
        res = session.get(url, headers=get_headers(), params=params, timeout=10)
        data = res.json()

        price = int(data["output"]["stck_prpr"])

        PRICE_CACHE[stock_code] = price
        PRICE_CACHE_TIME[stock_code] = now

        return price

    except Exception as e:
        print("PRICE ERROR:", e)
        return None


def get_multiple_prices(stock_dict: dict):
    return {name: get_price(code) for name, code in stock_dict.items()}

# ==========================================================
# ACCOUNT
# ==========================================================

def get_positions():
    return account["positions"]


def get_recent_trades(limit=20):
    return account["trades"][-limit:]


def get_total_asset(prices: dict):

    total = account["balance"]

    for name, pos in account["positions"].items():
        price = prices.get(name)
        if price:
            total += price * pos["qty"]

    return total


def get_total_pnl(prices: dict):

    total_asset = get_total_asset(prices)

    pnl = total_asset - START_BALANCE
    pnl_pct = (pnl / START_BALANCE) * 100

    return pnl, pnl_pct

# ==========================================================
# CORE LOGIC (AI 자리)
# ==========================================================

def generate_signals(prices: dict):

    signals = {}

    for name, price in prices.items():

        if price is None:
            signals[name] = {
                "action": "HOLD",
                "score": 0,
                "price": 0
            }
            continue

        # 🔥 여기서 AI/전략 넣으면 됨 (현재는 더미)
        signals[name] = {
            "action": "HOLD",
            "score": 0.0,
            "price": price
        }

    return signals

# ==========================================================
# MAIN CYCLE
# ==========================================================

def run_cycle():

    prices = get_multiple_prices(STOCKS)

    signals = generate_signals(prices)

    return {
        "prices": prices,
        "signals": signals,
        "account": account
    }
