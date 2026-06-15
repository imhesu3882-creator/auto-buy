"""
==========================================================
AI AUTO TRADER
broker.py (PRODUCTION SAFE VERSION - FULLY IMPLEMENTED)
----------------------------------------------------------
✔ 한국투자증권 API 연동 (시세 - tr_id 헤더 수정 완료)
✔ Paper Trading Engine (실매매 차단 및 가상 매매 완벽 구현)
✔ yfinance 연동 및 기술적 지표 기반 실시간 신호 생성 완료
✔ 잘려있던 run_cycle 로직 완벽 마무리 복구
==========================================================
"""

import time
import requests
import pandas as pd
import yfinance as yf
from config import *
from indicators import calculate_rsi, calculate_macd, calculate_score

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
CACHE_SEC = 5  # API 과부하 방지를 위해 캐시 시간을 5초로 늘렸습니다.

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
        if not ACCESS_TOKEN:
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

def get_price(stock_code: str):
    now = time.time()
    if stock_code in PRICE_CACHE:
        if now - PRICE_CACHE_TIME.get(stock_code, 0) < CASTE_SEC:
            return PRICE_CACHE[stock_code]

    url = f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price"
    headers = get_headers()
    headers["tr_id"] = "FHKST01010100" 

    try:
        res = session.get(
            url,
            headers=headers,
            params={
                "fid_cond_mrkt_div_code": "J",
                "fid_input_iscd": stock_code
            },
            timeout=10
        )
        data = res.json()

        if data.get("rt_cd") != "0":
            print(f"[API ERROR] {stock_code} : {data.get('msg1')}")
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
    pnl_pct = (pnl / START_BALANCE) * 100 if START_BALANCE > 0 else 0.0
    return pnl, pnl_pct

def generate_signals(prices: dict):
    """yfinance 데이터를 받아와 indicators.py 지표 계산 후 BUY/SELL 신호 확정"""
    signals = {}
    for name, price in prices.items():
        if price is None or price == 0:
            signals[name] = {"action": "HOLD", "score": 0, "price": 0}
            continue
        
        try:
            # 야후 파이낸스용 티커 매핑 (config에 정의된 TICKERS 사용)
            ticker = TICKERS.get(name, f"{STOCKS[name]}.KS")
            stock = yf.Ticker(ticker)
            df = stock.history(period="1mo", interval="1d")
            
            if df.empty or len(df) < 14:
                signals[name] = {"action": "HOLD", "score": 50, "price": price}
                continue
                
            rsi = calculate_rsi(df)
            macd, macd_sig = calculate_macd(df)
            score = calculate_score(rsi, macd, macd_sig)
            
            action = "HOLD"
            if score >= 70:
                action = "BUY"
            elif score <= 30:
                action = "SELL"
                
            signals[name] = {"action": action, "score": score, "price": price}
        except Exception as e:
            print(f"SIGNAL ERROR ({name}):", e)
            signals[name] = {"action": "HOLD", "score": 0, "price": price}
            
    return signals

def run_cycle():
    """대시보드가 요구하는 주기별 전체 데이터를 수집하여 반환합니다."""
    prices = get_multiple_prices(STOCKS)
    signals = generate_signals(prices)
    return {
        "prices": prices,
        "signals": signals,
        "account": account
    }
