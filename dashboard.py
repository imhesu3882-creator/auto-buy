"""
==========================================================
AI AUTO TRADER - dashboard.py (진짜 최종 완벽본)
==========================================================
"""
import streamlit as st
import time
import pandas as pd
import re
from config import *
from broker import run_cycle, get_total_asset, get_total_pnl, get_positions, get_recent_trades

def safe_int(value, default=0):
    if value is None: return default
    try:
        if isinstance(value, (int, float)): return int(value)
        clean_val = re.sub(r'[^\d.-]', '', str(value))
        return int(float(clean_val)) if clean_val else default
    except: return default

st.set_page_config(page_title="AI Auto Trader", layout="wide")
st.title("📊 Auto Trading Dashboard 🤖")

cycle = run_cycle()
prices = cycle.get("prices", {})
signals = cycle.get("signals", {})
account_state = cycle.get("account", {"balance": 0})
clean_prices = {k: safe_int(v, None) for k, v in prices.items()}

st.subheader("📈 실시간 가격")
if not clean_prices:
    st.info("조회된 종목이 없습니다.")
else:
    cols = st.columns(len(clean_prices))
    for col, (name, price) in zip(cols, clean_prices.items()):
        with col:
            if price is None or price == 0: st.error(f"{name}: 데이터 없음")
            else: st.metric(label=name, value=f"{price:,} 원")

st.divider()
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
    if pnl > 0: st.success(f"**총 손익:** +{pnl:,} 원 (+{pnl_pct:.2f}%)")
    elif pnl < 0: st.error(f"**총 손익:** {pnl:,} 원 ({pnl_pct:.2f}%)")
    else: st.info(f"**총 손익:** 0 원 (0.00%)")

with col2:
    st.subheader("🧠 AI 신호 및 점수")
    if not signals: st.info("대기 중인 AI 신호가 없습니다.")
    else:
        for name, sig in signals.items():
            action = sig.get("action", "HOLD")
            color = "🟢 BUY" if action == "BUY" else "🔴 SELL" if action == "SELL" else "🟡 HOLD"
            score = safe_int(sig.get('score', 0))
            sig_price = safe_int(sig.get('price', 0))
            st.write(f"**{name}** | 신호: {color} | AI 점수: ` {score} 점 ` | 현재가: {sig_price:,} 원")

st.divider()
col3, col4 = st.columns(2)
with col3:
    st.subheader("📦 보유 종목")
    positions = get_positions()
    if not positions: st.info("현재 보유 중인 종목이 없습니다.")
    else:
        for name, pos in positions.items():
            current_price = safe_int(clean_prices.get(name, 0))
            avg_price = safe_int(pos.get('avg_price', 0))
            qty = safe_int(pos.get('qty', 0))
            st.write(f"**{name}** | 수량: {qty}주 | 평단: {avg_price:,} 원 | 현재가: {current_price:,} 원")

with col4:
    st.subheader("🧾 최근 거래 내역")
    trades = get_recent_trades()
    if not trades: st.info("최근 거래 내역이 없습니다.")
    else:
        df = pd.DataFrame(trades)
        st.dataframe(df, use_container_width=True, hide_index=True)

time.sleep(REFRESH_SECONDS)
st.rerun()
