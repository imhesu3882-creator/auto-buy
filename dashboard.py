"""
==========================================================
AI AUTO TRADER
dashboard.py (FINAL CLEAN VERSION)
----------------------------------------------------------
✔ broker.py 완전 호환
✔ Streamlit 공식 자동 새로고침(st.rerun) 적용
✔ 서버 다운(무한 루프) 버그 완전 해결
==========================================================
"""

import streamlit as st
import time
import pandas as pd

from config import *
from broker import (
    run_cycle,
    get_total_asset,
    get_total_pnl,
    get_positions,
    get_recent_trades
)

# 페이지 기본 설정
st.set_page_config(page_title="AI Auto Trader", layout="wide")

st.title("📊 Auto Trading Dashboard 🤖")

# ==========================================================
# 데이터 처리 (1회 실행)
# ==========================================================
cycle = run_cycle()
prices = cycle["prices"]
signals = cycle["signals"]
account_state = cycle["account"]

# ==========================================================
# 화면 UI 구성
# ==========================================================

# 1. 실시간 가격 섹션 (가로 정렬로 깔끔하게)
st.subheader("📈 실시간 가격")
cols = st.columns(len(prices))
for col, (name, price) in zip(cols, prices.items()):
    with col:
        if price is None:
            st.error(f"{name}: 데이터 없음")
        else:
            st.metric(label=name, value=f"{price:,} 원")

st.divider()

# 2. 계좌 상태 섹션
col1, col2 = st.columns(2)
with col1:
    st.subheader("💰 계좌 상태")
    total_asset = get_total_asset(prices)
    pnl, pnl_pct = get_total_pnl(prices)
    
    st.write(f"**보유 현금:** {account_state['balance']:,} 원")
    st.write(f"**총 자산:** {total_asset:,} 원")
    
    # 수익률에 따라 색상 변경
    if pnl > 0:
        st.success(f"**총 손익:** +{pnl:,} 원 (+{pnl_pct:.2f}%)")
    elif pnl < 0:
        st.error(f"**총 손익:** {pnl:,} 원 ({pnl_pct:.2f}%)")
    else:
        st.info(f"**총 손익:** 0 원 (0.00%)")

with col2:
    st.subheader("🧠 AI 신호")
    for name, sig in signals.items():
        color = "🟡"
        if sig["action"] == "BUY":
            color = "🟢"
        elif sig["action"] == "SELL":
            color = "🔴"
        
        st.write(
            f"{color} **{name}** | {sig['action']} | "
            f"Score: {sig['score']} | {sig['price']:,} 원"
        )

st.divider()

# 3. 보유 종목 및 거래 내역
col3, col4 = st.columns(2)
with col3:
    st.subheader("📦 보유 종목")
    positions = get_positions()
    if not positions:
        st.info("현재 보유 중인 종목이 없습니다.")
    else:
        for name, pos in positions.items():
            current_price = prices.get(name, 0)
            st.write(
                f"**{name}** | 수량: {pos['qty']}주 | "
                f"평단: {pos['avg_price']:,.0f} 원 | 현재가: {current_price:,} 원"
            )

with col4:
    st.subheader("🧾 최근 거래 내역")
    trades = get_recent_trades()
    if not trades:
        st.info("최근 거래 내역이 없습니다.")
    else:
        df = pd.DataFrame(trades)
        st.dataframe(df, use_container_width=True, hide_index=True)

# ==========================================================
# 자동 새로고침 로직 (Streamlit 전용)
# ==========================================================
time.sleep(REFRESH_SECONDS)
st.rerun()
