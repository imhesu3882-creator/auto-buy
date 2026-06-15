import streamlit as st
import broker
import pandas as pd
from datetime import datetime

# 페이지 설정
st.set_page_config(page_title="AI Auto-Trading Dashboard", layout="wide")

# 디자인 테마 적용 (다크 모드 최적화)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 AI Auto-Trading Dashboard")

# 데이터 로드 (실패 시에도 프로세스 유지)
try:
    with st.spinner('데이터를 불러오는 중입니다...'):
        data = broker.run_cycle()
except Exception as e:
    st.error(f"데이터 로드 중 일시적인 지연이 발생했습니다. 잠시 후 새로고침 해주세요.")
    st.stop()

# 1. 상단 현재가 카드 레이아웃
st.subheader("📈 주요 종목 실시간 시세")
price_cols = st.columns(len(data["prices"]))
for i, (name, price) in enumerate(data["prices"].items()):
    with price_cols[i]:
        label = f"{name}"
        value = f"{price:,} 원" if price > 0 else "조회 지연"
        st.metric(label, value)

st.divider()

# 2. 하단 AI 신호 상세 표
st.subheader("🧠 AI 매매 신호 분석")
if data["signals"]:
    # 10번 넘게 검토한 에러 차단 로직: 모든 데이터를 문자열로 변환 후 DataFrame 생성
    df = pd.DataFrame(data["signals"]).T
    
    # 여기서 충돌 방지: 데이터프레임의 모든 값을 문자열(object)로 강제 고정
    df = df.astype(str)
    
    # 디자인을 위해 인덱스 이름 변경
    df.index.name = "종목명"
    
    # 표 출력 (st.table이 st.dataframe보다 배포 환경에서 훨씬 안정적입니다)
    st.table(df)
else:
    st.info("현재 분석된 신호 데이터가 없습니다.")

# 하단 정보 및 수동 갱신
st.caption(f"최종 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (지연 시 브라우저 새로고침을 해주세요)")
if st.button("🔄 데이터 수동 갱신"):
    st.rerun()
