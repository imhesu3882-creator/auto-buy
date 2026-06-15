import time, requests, pandas as pd, yfinance as yf
import config

session = requests.Session()
ACCESS_TOKEN, TOKEN_EXPIRE = None, 0

def get_headers():
    global ACCESS_TOKEN, TOKEN_EXPIRE
    if ACCESS_TOKEN is None or time.time() >= TOKEN_EXPIRE:
        res = session.post(f"{config.BASE_URL}/oauth2/tokenP", json={"grant_type": "client_credentials", "appkey": config.APP_KEY, "appsecret": config.APP_SECRET})
        data = res.json()
        ACCESS_TOKEN = data.get("access_token")
        TOKEN_EXPIRE = time.time() + int(data.get("expires_in", 3600)) - 60
    return {"content-type": "application/json", "authorization": f"Bearer {ACCESS_TOKEN}", "appkey": config.APP_KEY, "appsecret": config.APP_SECRET}

def get_price(code):
    try:
        headers = get_headers(); headers["tr_id"] = "FHKST01010100"
        res = session.get(f"{config.BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price", headers=headers, params={"fid_cond_mrkt_div_code": "J", "fid_input_iscd": code})
        return int(res.json()["output"]["stck_prpr"])
    except: return None

def run_cycle():
    from indicators import calculate_rsi, calculate_macd, calculate_score
    prices = {name: get_price(code) for name, code in config.STOCKS.items()}
    signals = {}
    for name, code in config.STOCKS.items():
        try:
            df = yf.Ticker(config.TICKERS[name]).history(period="1mo", interval="1d")
            rsi = calculate_rsi(df)
            macd, macd_sig, hist = calculate_macd(df)
            score = calculate_score(rsi.iloc[-1], hist.iloc[-1], 1.0)
            signals[name] = {"action": "BUY" if score >= config.BUY_SCORE else "SELL" if score <= config.SELL_SCORE else "HOLD", "score": score, "price": prices[name]}
        except: signals[name] = {"action": "HOLD", "score": 0, "price": prices[name]}
    return {"prices": prices, "signals": signals}
