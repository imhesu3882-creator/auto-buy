import streamlit as st
import broker
import pandas as pd

st.title("📊 AI Auto Trading Dashboard")
data = broker.run_cycle()

# 1. 가격 표시
cols = st.columns(len(data["prices"]))
for i, (name, price) in enumerate(data["prices"].items()):
    cols[i].metric(name, f"{price:,} 원" if price > 0 else "조회 중...")

# 2. 신호 표 표시 (st.table 대신 st.dataframe 사용)
st.subheader("🧠 AI 신호 상세")

# 데이터를 DataFrame으로 변환
df = pd.DataFrame(data["signals"]).T

# 데이터프레임 형식으로 출력 (에러 방지에 훨씬 강함)
st.dataframe(df, use_container_width=True)

if st.button("새로고침"):
    st.rerun()
