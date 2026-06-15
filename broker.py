"""
==========================================================
AI AUTO TRADER
broker.py (FINAL CLEAN VERSION)
----------------------------------------------------------
✔ 한국투자증권 API 연동 (시세)
✔ Paper Trading Engine (실매매 차단)
✔ 전략 확장 구조
✔ Streamlit run_cycle 지원
==========================================================
"""

import time
import requests
from config import *

# ==========================================================
# SESSION / GLOBAL STATE
# ==========================================================

session = requests.Session()

ACCESS_TOKEN = None
TOKEN_EXPIRE = 0

account = {
    "balance": START_BALANCE,
    "positions": {},   # {name: {qty, avg_price}}
    "trades": []       # 거래 로그
}

# ==========================================================
# CACHE (API 최소화)
# ==========================================================

PRICE_CACHE = {}
PRICE_CACHE_TIME = {}
CACHE_SEC = 1

# ==========================================================
# TOKEN MANAGEMENT
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

    res = session.post(url, json=payload, timeout=10)
    res.raise_for_status()

    data = res.json()

    ACCESS_TOKEN = data["access_token"]
    TOKEN_EXPIRE = time.time() + int(data["expires_in"]) - 60

    print("✅ TOKEN ISSUED")


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
# PRICE DATA
# ==========================================================

def get_price(stock_code: str):

    now = time.time()

    # cache hit
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

        if "output" not in data:
            return None

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
# ACCOUNT SYSTEM
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

        # 기본 전략 (무조건 HOLD 기본 → 안전 구조)
        signals[name] = {
            "action": "HOLD",
            "score": 0,
            "price": price
        }

    return signals

# ==========================================================
# PAPER TRADING ENGINE (REAL SAFE MODE)
# ==========================================================

def execute_trade(name: str, signal: dict):

    price = signal["price"]
    action = signal["action"]

    if price is None:
        return

    # ======================================================
    # REAL TRADING BLOCK (절대 실행 안됨)
    # ======================================================
    if REAL_TRADING is True:
        print("🚨 REAL TRADING ENABLED - BLOCKED FOR SAFETY")
        return

    # ======================================================
    # BUY
    # ======================================================
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

    # ======================================================
    # SELL
    # ======================================================
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
# MAIN ENGINE (STREAMLIT ENTRY POINT)
# ==========================================================

def run_cycle():

    prices = get_multiple_prices(STOCKS)
    signals = generate_signals(prices)

    # execution
    for name, sig in signals.items():
        execute_trade(name, sig)

    return {
        "prices": prices,
        "signals": signals,
        "account": account
    }
