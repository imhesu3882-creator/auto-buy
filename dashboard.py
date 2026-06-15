import streamlit as st
import broker
import pandas as pd

st.title("📊 AI Auto Trading Dashboard")
data = broker.run_cycle()

# 1. 가격 표시
cols = st.columns(len(data["prices"]))
for i, (name, price) in enumerate(data["prices"].items()):
    cols[i].metric(name, f"{price:,} 원" if price > 0 else "데이터 수집 중")

# 2. 신호 표 표시 (에러 방지)
st.subheader("🧠 AI 신호 상세")
df = pd.DataFrame(data["signals"]).T
st.table(df)

if st.button("새로고침"):
    st.rerun()
