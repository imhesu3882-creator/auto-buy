import time, requests, pandas as pd, yfinance as yf
import config

def get_token():
    url = f"{config.BASE_URL}/oauth2/tokenP"
    res = requests.post(url, json={"grant_type": "client_credentials", "appkey": config.APP_KEY, "appsecret": config.APP_SECRET})
    return res.json().get("access_token", "")

def get_price(code):
    try:
        url = f"{config.BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price"
        headers = {"content-type": "application/json", "authorization": "Bearer " + get_token(), "appkey": config.APP_KEY, "appsecret": config.APP_SECRET, "tr_id": "FHKST01010100"}
        res = requests.get(url, headers=headers, params={"fid_cond_mrkt_div_code": "J", "fid_input_iscd": str(code).zfill(6)})
        return int(res.json()["output"]["stck_prpr"])
    except: return None

def run_cycle():
    from indicators import calculate_rsi, calculate_macd, calculate_score
    results = {"prices": {}, "signals": {}}
    for name, code in config.STOCKS.items():
        p = get_price(code)
        results["prices"][name] = p if p else 0 # 0으로 고정
        try:
            df = yf.Ticker(config.TICKERS[name]).history(period="1mo", interval="1d")
            rsi = calculate_rsi(df)
            _, _, hist = calculate_macd(df)
            score = calculate_score(rsi.iloc[-1], hist.iloc[-1], 1.0)
            # 모든 값을 문자열로 변환하여 에러 방지
            results["signals"][name] = {"Action": "BUY" if score >= config.BUY_SCORE else ("SELL" if score <= config.SELL_SCORE else "HOLD"), "Score": str(round(score, 1)), "Price": str(p if p else 0)}
        except: results["signals"][name] = {"Action": "HOLD", "Score": "0", "Price": "0"}
    return results
