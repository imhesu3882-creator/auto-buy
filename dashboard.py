import streamlit as st
import broker
import pandas as pd

st.title("📊 AI Auto Trading Dashboard")
data = broker.run_cycle()

# 1. 가격 표시
cols = st.columns(len(data["prices"]))
for i, (name, price) in enumerate(data["prices"].items()):
    cols[i].metric(name, f"{price:,} 원" if price > 0 else "조회 중...")

# 2. 신호 표 표시 (에러 방지: 모든 데이터 타입을 문자열로 강제 변환)
st.subheader("🧠 AI 신호 상세")

# 여기서 딕셔너리 내부의 모든 값을 문자열로 변환하여 에러 방지
clean_signals = {
    name: {k: str(v) for k, v in info.items()} 
    for name, info in data["signals"].items()
}

df = pd.DataFrame(clean_signals).T
st.table(df)

if st.button("새로고침"):
    st.rerun()
