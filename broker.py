import time, requests, pandas as pd, yfinance as yf
import config

session = requests.Session()
ACCESS_TOKEN, TOKEN_EXPIRE = None, 0

def get_headers():
    global ACCESS_TOKEN, TOKEN_EXPIRE
    if ACCESS_TOKEN is None or time.time() >= TOKEN_EXPIRE:
        try:
            res = session.post(f"{config.BASE_URL}/oauth2/tokenP", json={"grant_type": "client_credentials", "appkey": config.APP_KEY, "appsecret": config.APP_SECRET}, timeout=5)
            data = res.json()
            ACCESS_TOKEN = data.get("access_token")
            TOKEN_EXPIRE = time.time() + int(data.get("expires_in", 3600)) - 60
        except: return {}
    return {"content-type": "application/json", "authorization": f"Bearer {ACCESS_TOKEN}", "appkey": config.APP_KEY, "appsecret": config.APP_SECRET}

def get_price(code):
    try:
        headers = get_headers()
        headers["tr_id"] = "FHKST01010100"
        res = session.get(f"{config.BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price", headers=headers, params={"fid_cond_mrkt_div_code": "J", "fid_input_iscd": str(code).zfill(6)}, timeout=5)
        return int(res.json()["output"]["stck_prpr"])
    except: return None

def run_cycle():
    from indicators import calculate_rsi, calculate_macd, calculate_score
    results = {"prices": {}, "signals": {}}
    for name, code in config.STOCKS.items():
        price = get_price(code)
        results["prices"][name] = price
        try:
            df = yf.Ticker(config.TICKERS[name]).history(period="1mo", interval="1d")
            if not df.empty:
                rsi = calculate_rsi(df)
                _, _, hist = calculate_macd(df)
                score = calculate_score(rsi.iloc[-1], hist.iloc[-1], 1.0)
                results["signals"][name] = {"action": "BUY" if score >= config.BUY_SCORE else "SELL" if score <= config.SELL_SCORE else "HOLD", "score": round(score, 1), "price": price}
            else:
                results["signals"][name] = {"action": "HOLD", "score": 0, "price": price}
        except:
            results["signals"][name] = {"action": "HOLD", "score": 0, "price": price}
    return results
