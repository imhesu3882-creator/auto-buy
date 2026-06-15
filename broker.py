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

    res = session.post(url, json={
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET
    }, timeout=10)

    res.raise_for_status()
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
# PRICE
# ==========================================================

def get_price(code):
    now = time.time()

    if code in PRICE_CACHE:
        if now - PRICE_CACHE_TIME.get(code, 0) < CACHE_SEC:
            return PRICE_CACHE[code]

    url = f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price"

    try:
        res = session.get(url, headers=get_headers(), params={
            "fid_cond_mrkt_div_code": "J",
            "fid_input_iscd": code
        }, timeout=10)

        data = res.json()

        if "output" not in data:
            return None

        price = int(data["output"]["stck_prpr"])

        PRICE_CACHE[code] = price
        PRICE_CACHE_TIME[code] = now

        return price

    except:
        return None


def get_multiple_prices(stock_dict):
    return {k: get_price(v) for k, v in stock_dict.items()}

# ==========================================================
# ACCOUNT
# ==========================================================

def get_positions():
    return account["positions"]


def get_recent_trades(limit=20):
    return account["trades"][-limit:]


def get_total_asset(prices):
    total = account["balance"]

    for name, pos in account["positions"].items():
        price = prices.get(name)
        if price:
            total += price * pos["qty"]

    return total


def get_total_pnl(prices):
    total = get_total_asset(prices)
    pnl = total - START_BALANCE
    return pnl, pnl / START_BALANCE * 100

# ==========================================================
# STRATEGY (RSI 간단 버전)
# ==========================================================

def generate_signals(prices):
    signals = {}

    for name, price in prices.items():

        if price is None:
            signals[name] = {"action": "HOLD", "score": 0, "price": 0}
            continue

        # 아주 단순 전략 (확장 가능)
        if price % 2 == 0:
            action = "BUY"
            score = 70
        else:
            action = "SELL"
            score = 40

        signals[name] = {
            "action": action,
            "score": score,
            "price": price
        }

    return signals

# ==========================================================
# PAPER TRADING ENGINE (핵심)
# ==========================================================

def execute_trade(name, signal):

    price = signal["price"]
    action = signal["action"]

    if price is None:
        return

    # BUY
    if action == "BUY" and account["balance"] >= 100000:
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
    if action == "SELL" and name in account["positions"]:
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

    # 자동매매 실행 (시뮬레이션)
    for name, sig in signals.items():
        execute_trade(name, sig)

    return {
        "prices": prices,
        "signals": signals,
        "account": account
    }
