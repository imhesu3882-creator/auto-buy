import streamlit as st
import broker
import pandas as pd
from datetime import datetime

# 페이지 설정
st.set_page_config(page_title="AI Auto-Trading Dashboard", layout="wide")

# 디자인 설정: 다크 모드 제거, 폰트 사이즈 대폭 상향
st.markdown("""
    <style>
    /* 배경을 밝게 수정 */
    .main { background-color: #ffffff; color: #000000; }
    
    /* 폰트 및 카드 스타일 */
    .stMetric { background-color: #f0f2f6; padding: 25px; border-radius: 15px; border: 2px solid #e0e0e0; }
    div[data-testid="stMetricValue"] { font-size: 40px !important; color: #000000; font-weight: bold; }
    div[data-testid="stMetricLabel"] { font-size: 20px !important; color: #333333; }
    
    /* 헤더 및 텍스트 크게 */
    h1 { font-size: 50px !important; color: #000000 !important; }
    h2 { font-size: 35px !important; color: #333333 !important; }
    
    /* 표 폰트 크게 */
    table { font-size: 20px !important; }
    thead tr th { font-size: 22px !important; }
    tbody tr td { font-size: 20px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 AI Auto-Trading Dashboard")

# 데이터 로드 예외 처리
try:
    with st.spinner('데이터를 불러오는 중입니다...'):
        data = broker.run_cycle()
except Exception as e:
    st.error("데이터 로드 중 지연이 발생했습니다.")
    st.stop()

# 1. 상단 가격 카드 (글자 크기 증대)
st.subheader("📈 주요 종목 실시간 시세")
price_cols = st.columns(len(data["prices"]))
for i, (name, price) in enumerate(data["prices"].items()):
    with price_cols[i]:
        # '조회 지연' 상태일 때 폰트를 더 크게 표시
        value_text = f"{price:,} 원" if price > 0 else "조회 지연"
        st.metric(label=name, value=value_text)

st.divider()

# 2. 하단 AI 신호 표 (표 폰트 증대)
st.subheader("🧠 AI 매매 신호 분석")
if data["signals"]:
    df = pd.DataFrame(data["signals"]).T
    df = df.astype(str)
    df.index.name = "종목명"
    st.table(df)
else:
    st.info("데이터를 수집 중입니다.")

st.caption(f"최종 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if st.button("🔄 데이터 수동 갱신"):
    st.rerun()
