import streamlit as st
import broker
import pandas as pd

st.title("📊 AI Auto Trading Dashboard")
data = broker.run_cycle()

st.subheader("📈 실시간 가격")
cols = st.columns(len(data["prices"]))
for i, (name, price) in enumerate(data["prices"].items()):
    cols[i].metric(name, f"{price:,} 원" if price else "조회 중")

st.subheader("🧠 AI 신호 상세")
st.table(pd.DataFrame(data["signals"]).T)
