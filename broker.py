"""
==========================================================
AI AUTO TRADER - broker.py (종목코드 6자리 정렬 진짜 최종본)
==========================================================
"""
import time, requests, pandas as pd, yfinance as yf
from config import *
from indicators import calculate_rsi, calculate_macd, calculate_score

session = requests.Session()
ACCESS_TOKEN, TOKEN_EXPIRE = None, 0
account = {"balance": START_BALANCE, "positions": {}, "trades": []}
PRICE_CACHE, PRICE_CACHE_TIME, CACHE_SEC = {}, {}, 5

def is_token_valid(): return ACCESS_TOKEN is not None and time.time() < TOKEN_EXPIRE
def issue_token():
    global ACCESS_TOKEN, TOKEN_EXPIRE
    try:
        res = session.post(f"{BASE_URL}/oauth2/tokenP", json={"grant_type": "client_credentials", "appkey": APP_KEY, "appsecret": APP_SECRET}, timeout=10)
        data = res.json()
        ACCESS_TOKEN = data.get("access_token")
        TOKEN_EXPIRE = time.time() + int(data.get("expires_in", 0)) - 60
    except Exception as e: print("TOKEN ERROR:", e)

def get_headers():
    if not is_token_valid(): issue_token()
    return {"content-type": "application/json", "authorization": f"Bearer {ACCESS_TOKEN}", "appkey": APP_KEY, "appsecret": APP_SECRET}

def get_price(stock_code: str):
    now = time.time()
    # 종목 코드가 숫자형태로 오면 맨 앞 0이 잘리므로 반드시 문자열 6자리로 강제 고정
    code_str = str(stock_code).strip().zfill(6)
    
    if code_str in PRICE_CACHE and now - PRICE_CACHE_TIME.get(code_str, 0) < CACHE_SEC: return PRICE_CACHE[code_str]
    headers = get_headers(); headers["tr_id"] = "FHKST01010100"
    try:
        res = session.get(f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price", headers=headers, params={"fid_cond_mrkt_div_code": "J", "fid_input_iscd": code_str}, timeout=10)
        data = res.json()
        price = int(data["output"]["stck_prpr"]) if data.get("rt_cd") == "0" else int(data.get("output", {}).get("stck_prpr", 0))
        if price > 0: PRICE_CACHE[code_str], PRICE_CACHE_TIME[code_str] = price, now
        return price if price > 0 else None
    except: return None

def get_multiple_prices(stock_dict: dict): return {name: get_price(code) for name, code in stock_dict.items()}
def get_positions(): return account["positions"]
def get_recent_trades(limit=20): return account["trades"][-limit:]
def get_total_asset(prices: dict):
    total = account["balance"]
    for name, pos in account["positions"].items():
        p = prices.get(name) or prices.get(name.upper()) or prices.get(name.lower())
        if p: total += p * pos["qty"]
    return total

def get_total_pnl(prices: dict):
    total = get_total_asset(prices)
    pnl = total - START_BALANCE
    return pnl, (pnl / START_BALANCE) * 100 if START_BALANCE > 0 else 0.0

def generate_signals(prices: dict):
    signals = {}
    upper_tickers = {k.upper(): v for k, v in TICKERS.items()}
    upper_stocks = {k.upper(): v for k, v in STOCKS.items()}
    
    for name, price in prices.items():
        uname = name.upper()
        if not price: signals[name] = {"action": "HOLD", "score": 0, "price": 0}; continue
        try:
            # 야후파이낸스용 코드 정형화 (.KS 처리)
            raw_code = str(upper_stocks.get(uname)).strip().zfill(6)
            ticker = upper_tickers.get(uname, f"{raw_code}.KS")
            df = yf.Ticker(ticker).history(period="1mo", interval="1d")
            if df.empty or len(df) < 14: signals[name] = {"action": "HOLD", "score": 50, "price": price}; continue
            rsi = calculate_rsi(df)
            macd, macd_sig = calculate_macd(df)
            score = calculate_score(rsi, macd, macd_sig)
            signals[name] = {"action": "BUY" if score >= 70 else "SELL" if score <= 30 else "HOLD", "score": score, "price": price}
        except: signals[name] = {"action": "HOLD", "score": 0, "price": price}
    return signals

def run_cycle():
    p = get_multiple_prices(STOCKS)
    p_extended = {**p, **{k.upper(): v for k, v in p.items()}, **{k.lower(): v for k, v in p.items()}}
    return {"prices": p_extended, "signals": generate_signals(p), "account": account}
