import streamlit as st
import broker
import pandas as pd

# 1. 자동 새로고침 설정 (웹페이지를 5초마다 새로고침)
st.set_page_config(page_title="AI Auto Trader", layout="wide")
st.markdown("""
    <meta http-equiv="refresh" content="5">
    <style>
    .stMetric { background-color: #161b22; padding: 20px; border-radius: 15px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 AI Auto Trading Dashboard")

# 2. 데이터 수집
data = broker.run_cycle()

# 3. 메트릭 디자인 복구 (이쁘게!)
st.subheader("📈 실시간 가격")
cols = st.columns(len(data["prices"]))
for i, (name, price) in enumerate(data["prices"].items()):
    cols[i].metric(name, f"{price:,} 원" if price and price > 0 else "조회 중...")

# 4. 데이터프레임 대신 '스트림릿 스타일 표' 사용 (타입 오류 방지)
st.subheader("🧠 AI 신호 상세")
df = pd.DataFrame(data["signals"]).T
# 'Action' 컬럼만 이모지 추가하여 디자인 살리기
if 'action' in df.columns:
    df['action'] = df['action'].apply(lambda x: f"🟢 {x}" if x == 'BUY' else f"🔴 {x}" if x == 'SELL' else f"⚪ {x}")

st.table(df)

st.caption("5초마다 자동 갱신 중입니다.")
