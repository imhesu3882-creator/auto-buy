"""
==========================================================
AI AUTO TRADER
dashboard.py (FINAL BEAUTIFUL VERSION)
----------------------------------------------------------
✔ broker.py 완전 호환
✔ 문자열로 들어오는 가격 및 점수 강제 숫자 변환 추가
✔ 데이터 공백 및 쉼표 예외처리 완벽 방지
==========================================================
"""

import streamlit as st
import time
import pandas as pd
import re

from config import *
from broker import (
    run_cycle,
    get_total_asset,
    get_total_pnl,
    get_positions,
    get_recent_trades
)

# 안전하게 숫자로 변환하는 헬퍼 함수
def safe_int(value, default=0):
    if value is None:
        return default
    try:
        if isinstance(value, (int, float)):
            return int(value)
        # 문자열 내 쉼표, 공백, 줄바꿈 제거 후 숫자만 추출
        clean_val = re.sub(r'[^\d.-]', '', str(value))
        return int(float(clean_val)) if clean_val else default
    except Exception:
        return default

# 페이지 기본 설정
st.set_page_config(page_title="AI Auto Trader", layout="wide")

st.title("📊 Auto Trading Dashboard 🤖")

# ==========================================================
# 데이터 처리 (1회 실행)
# ==========================================================
cycle = run_cycle()
prices = cycle.get("prices", {})
signals = cycle.get("signals", {})
account_state = cycle.get("account", {"balance": 0})

# 데이터 강제 안전 정화 (None 방지)
clean_prices = {k: safe_int(v, None) for k, v in prices.items()}

# ==========================================================
# 화면 UI 구성
# ==========================================================

# 1. 실시간 가격 섹션
st.subheader("📈 실시간 가격")
if not clean_prices:
    st.info("조회된 종목이 없습니다.")
else:
    cols = st.columns(len(clean_prices))
    for col, (name, price) in zip(cols, clean_prices.items()):
        with col:
            if price is None or price == 0:
                st.error(f"{name}: 데이터 없음")
            else:
                st.metric(label=name, value=f"{price:,} 원")

st.divider()

# 2. 계좌 상태 섹션
col1, col2 = st.columns(2)
with col1:
    st.subheader("💰 계좌 상태")
    total_asset = safe_int(get_total_asset(clean_prices))
    pnl, pnl_pct = get_total_pnl(clean_prices)
    pnl = safe_int(pnl)
    pnl_pct = float(pnl_pct) if pnl_pct else 0.0
    balance = safe_int(account_state.get('balance', 0))
    
    st.write(f"**보유 현금:** {balance:,} 원")
    st.write(f"**총 자산:** {total_asset:,} 원")
    
    # 수익률에 따라 색상 변경
    if pnl > 0:
        st.success(f"**총 손익:** +{pnl:,} 원 (+{pnl_pct:.2f}%)")
    elif pnl < 0:
        st.error(f"**총 손익:** {pnl:,} 원 ({pnl_pct:.2f}%)")
    else:
        st.info(f"**총 손익:** 0 원 (0.00%)")

with col2:
    st.subheader("🧠 AI 신호 및 점수")
    if not signals:
        st.info("대기 중인 AI 신호가 없습니다.")
    else:
        for name, sig in signals.items():
            action = sig.get("action", "HOLD")
            color = "🟡 HOLD"
            if action == "BUY":
                color = "🟢 BUY"
            elif action == "SELL":
                color = "🔴 SELL"
            
            score = safe_int(sig.get('score', 0))
            sig_price = safe_int(sig.get('price', 0))
            
            st.write(
                f"**{name}** | 신호: {color} | "
                f"AI 점수: ` {score} 점 ` | 현재가: {sig_price:,} 원"
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
            current_price = safe_int(clean_prices.get(name, 0))
            avg_price = safe_int(pos.get('avg_price', 0))
            qty = safe_int(pos.get('qty', 0))
            st.write(
                f"**{name}** | 수량: {qty}주 | "
                f"평단: {avg_price:,} 원 | 현재가: {current_price:,} 원"
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
