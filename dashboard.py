import streamlit as st
import broker

st.set_page_config(page_title="AI Auto Trader", layout="wide")
st.title("📊 AI Auto Trading Dashboard")

cycle = broker.run_cycle()
prices = cycle["prices"]

st.subheader("📈 실시간 가격")
cols = st.columns(len(prices))
for col, (name, price) in zip(cols, prices.items()):
    col.metric(name, f"{price:,} 원" if price else "조회 대기중")

st.subheader("🧠 AI 신호 및 점수")
st.table(cycle["signals"])
