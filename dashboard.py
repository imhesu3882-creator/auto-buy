import streamlit as st
import broker

st.title("📊 Auto Trading Dashboard")
cycle = broker.run_cycle()

# prices가 딕셔너리이므로 안전하게 출력
prices = cycle["prices"]
cols = st.columns(len(prices))
for col, (name, price) in zip(cols, prices.items()):
    col.metric(name, f"{price:,} 원" if price else "데이터 없음")

st.write("### AI 신호 상세")
st.table(cycle["signals"])
