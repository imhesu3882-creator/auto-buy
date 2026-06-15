import streamlit as st
import broker
import time

st.set_page_config(page_title="AI Auto Trader", layout="wide")
st.title("📊 AI Auto Trading Dashboard")

# 화면을 계속 새로 그릴 플레이스홀더 생성
placeholder = st.empty()

while True:
    with placeholder.container():
        # 데이터 수집 (broker에서 알아서 5초마다 갱신된 값을 가져옴)
        data = broker.run_cycle()
        
        # 1. 가격 표시
        cols = st.columns(len(data["prices"]))
        for i, (name, price) in enumerate(data["prices"].items()):
            cols[i].metric(name, f"{price:,} 원" if price and price > 0 else "조회 중...")
            
        # 2. 신호 표시 (DataFrame을 쓰지 않는 안전한 텍스트 방식)
        st.subheader("🧠 AI 신호 상세")
        for name, info in data["signals"].items():
            action = info.get("action", "HOLD")
            score = info.get("score", 0)
            price = info.get("price", 0)
            st.write(f"**{name}**: {action} (점수: {score}, 현재가: {price})")
            
        st.caption(f"최종 업데이트: {time.strftime('%H:%M:%S')}")
        
    time.sleep(5) # 5초 대기 후 자동 반복
