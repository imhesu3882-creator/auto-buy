"""
==========================================================
AI AUTO TRADER - broker.py (전체 코드 - 최종본)
==========================================================
"""
import time, requests, pandas as pd, yfinance as yf
import config

session = requests.Session()
ACCESS_TOKEN, TOKEN_EXPIRE = None, 0
account = {"balance": config.START_BALANCE, "positions": {}, "trades": []}
PRICE_CACHE, PRICE_CACHE_TIME, CACHE_SEC = {}, {}, 5

def is_token_valid(): return ACCESS_TOKEN is not None and time.time() < TOKEN_EXPIRE

def issue_token():
    global ACCESS_TOKEN, TOKEN_EXPIRE
    try:
        res = session.post(f"{config.BASE_URL}/oauth2/tokenP", json={"grant_type": "client_credentials", "appkey": config.APP_KEY, "appsecret": config.APP_SECRET}, timeout=10)
        data = res.json()
        ACCESS_TOKEN = data.get("access_token")
        TOKEN_EXPIRE = time.time() + int(data.get("expires_in", 0)) - 60
    except Exception as e: print("TOKEN ERROR:", e)

def get_headers():
    if not is_token_valid(): issue_token()
    return {"content-type": "application/json", "authorization": f"Bearer {ACCESS_TOKEN}", "appkey": config.APP_KEY, "appsecret": config.APP_SECRET}

def get_price(stock_code: str):
    now = time.time()
    code_str = str(stock_code).strip().zfill(6)
    if code_str in PRICE_CACHE and now - PRICE_CACHE_TIME.get(code_str, 0) < CACHE_SEC: return PRICE_CACHE[code_str]
    headers = get_headers(); headers["tr_id"] = "FHKST01010100"
    try:
        res = session.get(f"{config.BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price", headers=headers, params={"fid_cond_mrkt_div_code": "J", "fid_input_iscd": code_str}, timeout=10)
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
        p = prices.get(name)
        if p: total += p * pos["qty"]
    return total

def get_total_pnl(prices: dict):
    total = get_total_asset(prices)
    pnl = total - config.START_BALANCE
    return pnl, (pnl / config.START_BALANCE) * 100 if config.START_BALANCE > 0 else 0.0

def generate_signals(prices: dict):
    from indicators import calculate_rsi, calculate_macd, calculate_score
    signals = {}
    for name, code in config.STOCKS.items():
        price = prices.get(name)
        if not price: 
            signals[name] = {"action": "HOLD", "score": 0, "price": 0}; continue
        try:
            ticker_code = config.TICKERS.get(name, f"{str(code).zfill(6)}.KS")
            df = yf.Ticker(ticker_code).history(period="1mo", interval="1d")
            if df.empty or len(df) < 14: signals[name] = {"action": "HOLD", "score": 50, "price": price}; continue
            rsi = calculate_rsi(df)
            macd, macd_sig, hist = calculate_macd(df)
            score = calculate_score(rsi.iloc[-1], hist.iloc[-1], 1.0)
            signals[name] = {"action": "BUY" if score >= config.BUY_SCORE else "SELL" if score <= config.SELL_SCORE else "HOLD", "score": score, "price": price}
        except: signals[name] = {"action": "HOLD", "score": 0, "price": price}
    return signals

def run_cycle():
    p = get_multiple_prices(config.STOCKS)
    return {"prices": p, "signals": generate_signals(p), "account": account}
