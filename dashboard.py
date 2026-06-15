import streamlit as st
import broker

st.title("📊 AI Auto Trading Dashboard")
data = broker.run_cycle()

# 1. 가격 표시
cols = st.columns(len(data["prices"]))
for i, (name, price) in enumerate(data["prices"].items()):
    cols[i].metric(name, f"{price:,} 원" if price and price > 0 else "조회 중...")

# 2. 신호 표시 (DataFrame 절대 금지 - 에러 원인 제거)
st.subheader("🧠 AI 신호 상세")
for name, info in data["signals"].items():
    action = info.get("action", "HOLD")
    score = info.get("score", 0)
    price = info.get("price", 0)
    
    # 텍스트와 이모지로 직접 구성 (표 에러 완전 차단)
    st.write(f"**{name}**: {action} (점수: {score}, 현재가: {price})")

if st.button("새로고침"):
    st.rerun()
