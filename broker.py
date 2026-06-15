"""
==========================================================
AI AUTO TRADER
broker.py (PRODUCTION SAFE VERSION)
----------------------------------------------------------
✔ 한국투자증권 API 연동 (시세)
✔ 장중 / 장외 자동 처리 (종가 fallback)
✔ Paper Trading Engine (실매매 차단)
✔ Streamlit run_cycle 지원
✔ API 실패에도 시스템 유지
==========================================================
"""

import time
import requests
from config import *

# ==========================================================
# SESSION / STATE
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
# CACHE
# ==========================================================

PRICE_CACHE = {}
PRICE_CACHE_TIME = {}
CACHE_SEC = 1


# ==========================================================
# TOKEN
# ==========================================================

def is_token_valid():
    return ACCESS_TOKEN is not None and time.time() < TOKEN_EXPIRE


def issue_token():
    global ACCESS_TOKEN, TOKEN_EXPIRE

    url = f"{BASE_URL}/oauth2/tokenP"

    payload = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET
    }

    try:
        res = session.post(url, json=payload, timeout=10)
        data = res.json()

        ACCESS_TOKEN = data.get("access_token")
        TOKEN_EXPIRE = time.time() + int(data.get("expires_in", 0)) - 60

        if ACCESS_TOKEN:
            print("TOKEN OK")
        else:
            print("TOKEN FAIL:", data)

    except Exception as e:
        print("TOKEN ERROR:", e)


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
# PRICE ENGINE (핵심 수정)
# ==========================================================

def get_price(stock_code: str):

    now = time.time()

    if stock_code in PRICE_CACHE:
        if now - PRICE_CACHE_TIME.get(stock_code, 0) < CACHE_SEC:
            return PRICE_CACHE[stock_code]

    url = f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price"

    try:
        res = session.get(
            url,
            headers=get_headers(),
            params={
                "fid_cond_mrkt_div_code": "J",
                "fid_input_iscd": stock_code
            },
            timeout=10
        )

        data = res.json()

        # ==============================
        # 1) API 실패 체크 (핵심)
        # ==============================
        if data.get("rt_cd") != "0":
            print(f"[MARKET CLOSED / ERROR] {stock_code} : {data.get('msg1')}")

            # 장외라도 값 있으면 fallback
            if "output" in data and data["output"].get("stck_prpr"):
                price = int(data["output"]["stck_prpr"])
            else:
                return None
        else:
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
        if price is None:
            continue
        total += price * pos["qty"]

    return total


def get_total_pnl(prices: dict):

    total = get_total_asset(prices)
    pnl = total - START_BALANCE
    pnl_pct = (pnl / START_BALANCE) * 100

    return pnl, pnl_pct


# ==========================================================
# STRATEGY (SAFE DEFAULT)
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

        signals[name] = {
            "action": "HOLD",
            "score": 0,
            "price": price
        }

    return signals


# ==========================================================
# PAPER ENGINE (SAFE MODE)
# ==========================================================

def execute_trade(name: str, signal: dict):

    price = signal["price"]
    action = signal["action"]

    if price is None:
        return

    # REAL TRADING BLOCK
    if REAL_TRADING is True:
        print("REAL TRADING BLOCKED")
        return

    # BUY
    if action == "BUY":

        if account["balance"] < 100000:
            return

        qty = 1
        cost = price * qty

        account["balance"] -= cost

        if name in account["positions"]:
            pos = account["positions"][name]
            pos["qty"] += qty
            pos["avg_price"] = (pos["avg_price"] + price) / 2
        else:
            account["positions"][name] = {
                "qty": qty,
                "avg_price": price
            }

        account["trades"].append({
            "name": name,
            "action": "BUY",
            "price": price,
            "qty": qty
        })

    # SELL
    elif action == "SELL" and name in account["positions"]:

        pos = account["positions"][name]

        qty = pos["qty"]
        account["balance"] += price * qty

        del account["positions"][name]

        account["trades"].append({
            "name": name,
            "action": "SELL",
            "price": price,
            "qty": qty
        })


# ==========================================================
# MAIN CYCLE
# ==========================================================

def run_cycle():

    prices = get_multiple_prices(STOCKS)
    signals = generate_signals(prices)

    for name, sig in signals.items():
        execute_trade(name, sig)

    return {
        "prices": prices,
        "signals": signals,
        "account": account
    }
