import streamlit as st
import broker
import config

st.set_page_config(page_title="AI Auto Trader", layout="wide")
st.title("📊 AI Auto Trading Dashboard")

# 데이터 로딩
data = broker.run_cycle()
prices = data["prices"]
signals = data["signals"]

# 실시간 가격 섹션
st.subheader("📈 실시간 가격")
cols = st.columns(len(prices))
for i, (name, price) in enumerate(prices.items()):
    cols[i].metric(name, f"{price:,} 원" if price else "수집 대기중...")

# AI 신호 섹션
st.subheader("🧠 AI 신호 및 점수")
import pandas as pd
df = pd.DataFrame(signals).T
st.table(df)

if st.button("새로고침"):
    st.rerun()
