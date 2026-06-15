import requests
import config

def get_token():
    try:
        url = f"{config.BASE_URL}/oauth2/tokenP"
        body = {
            "grant_type": "client_credentials",
            "appkey": config.APP_KEY,
            "appsecret": config.APP_SECRET
        }
        # 타임아웃을 설정해 지연 시 무한 대기를 방지합니다.
        res = requests.post(url, json=body, timeout=5)
        return res.json().get("access_token", "")
    except:
        return ""

def get_price(code, token):
    if not token: return 0
    try:
        url = f"{config.BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price"
        headers = {
            "content-type": "application/json",
            "authorization": f"Bearer {token}",
            "appkey": config.APP_KEY,
            "appsecret": config.APP_SECRET,
            "tr_id": "FHKST01010100"
        }
        params = {"fid_cond_mrkt_div_code": "J", "fid_input_iscd": str(code).zfill(6)}
        res = requests.get(url, headers=headers, params=params, timeout=5)
        return int(res.json()["output"]["stck_prpr"])
    except:
        return 0

def run_cycle():
    token = get_token()
    results = {"prices": {}, "signals": {}}
    
    for name, code in config.STOCKS.items():
        price = get_price(code, token)
        results["prices"][name] = price
        
        # 데이터가 없을 때도 구조를 유지하여 대시보드 충돌 방지
        results["signals"][name] = {
            "종목코드": str(code),
            "현재가": f"{price:,}원" if price > 0 else "조회 지연",
            "AI신호": "HOLD", # 실제 AI 로직 연결 전 기본값
            "상태": "정상" if price > 0 else "연결 확인 필요"
        }
    return results
