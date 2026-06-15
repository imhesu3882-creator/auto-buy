import requests, config

def get_price(code):
    url = f"{config.BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price"
    headers = {"content-type": "application/json", "authorization": "Bearer " + get_token(), "appkey": config.APP_KEY, "appsecret": config.APP_SECRET, "tr_id": "FHKST01010100"}
    res = requests.get(url, headers=headers, params={"fid_cond_mrkt_div_code": "J", "fid_input_iscd": str(code).zfill(6)})
    return int(res.json()["output"]["stck_prpr"])

def get_token():
    url = f"{config.BASE_URL}/oauth2/tokenP"
    res = requests.post(url, json={"grant_type": "client_credentials", "appkey": config.APP_KEY, "appsecret": config.APP_SECRET})
    return res.json().get("access_token", "")

def run_cycle():
    results = {"prices": {}, "signals": {}}
    for name, code in config.STOCKS.items():
        try:
            results["prices"][name] = get_price(code)
            results["signals"][name] = {"Action": "HOLD", "Score": "0", "Price": str(results["prices"][name])}
        except:
            results["prices"][name] = None
            results["signals"][name] = {"Action": "HOLD", "Score": "0", "Price": "0"}
    return results
