import streamlit as st
import broker
import pandas as pd

st.title("📊 AI Auto Trading Dashboard")

data = broker.run_cycle()

# 1. 가격 표시
st.subheader("📈 실시간 가격")
cols = st.columns(len(data["prices"]))
for i, (name, price) in enumerate(data["prices"].items()):
    val = f"{price:,} 원" if price and price > 0 else "데이터 수집 중"
    cols[i].metric(name, val)

# 2. 신호 표 표시 (오류를 일으키는 자동 갱신 및 복잡한 변환 완전히 제거)
st.subheader("🧠 AI 신호 상세")
if data["signals"]:
    # 데이터 타입을 확실히 하기 위해 딕셔너리를 직접 가공
    df_data = []
    for name, info in data["signals"].items():
        df_data.append({
            "종목": name,
            "신호": str(info.get("action", "HOLD")),
            "점수": str(info.get("score", "0")),
            "가격": str(info.get("price", "0"))
        })
    df = pd.DataFrame(df_data)
    st.table(df)
else:
    st.write("데이터 수집 대기 중...")
