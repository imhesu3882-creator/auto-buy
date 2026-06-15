import streamlit as st
import broker
import pandas as pd
from datetime import datetime

# 페이지 설정
st.set_page_config(page_title="AI Auto-Trading Dashboard", layout="wide")

# 디자인 설정
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 AI Auto-Trading Dashboard")

# 데이터 로드 예외 처리
try:
    with st.spinner('데이터를 불러오는 중입니다...'):
        data = broker.run_cycle()
except Exception as e:
    st.error("데이터 로드 중 지연이 발생했습니다. 새로고침 해주세요.")
    st.stop()

# 1. 상단 가격 카드
st.subheader("📈 주요 종목 실시간 시세")
price_cols = st.columns(len(data["prices"]))
for i, (name, price) in enumerate(data["prices"].items()):
    with price_cols[i]:
        label = f"{name}"
        value = f"{price:,} 원" if price > 0 else "조회 지연"
        st.metric(label, value)

st.divider()

# 2. 하단 AI 신호 표 (에러 차단 로직)
st.subheader("🧠 AI 매매 신호 분석")
if data["signals"]:
    df = pd.DataFrame(data["signals"]).T
    # 모든 데이터를 문자열로 변환하여 ArrowTypeError 원천 봉쇄
    df = df.astype(str)
    df.index.name = "종목명"
    st.table(df)
else:
    st.info("데이터를 수집 중입니다.")

st.caption(f"최종 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if st.button("🔄 데이터 수동 갱신"):
    st.rerun()
