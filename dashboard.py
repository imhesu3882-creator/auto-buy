"""
==========================================================
AI AUTO TRADER
dashboard.py (FINAL CLEAN VERSION)
----------------------------------------------------------
✔ broker.py 완전 호환
✔ Streamlit 안정 루프
✔ Render 배포 안전 구조
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

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(page_title="AI Auto Trader", layout="wide")

st.title("📊 Auto Trading Dashboard 🤖")

placeholder = st.empty()

# ==========================================================
# MAIN LOOP (STREAMLIT SAFE)
# ==========================================================

MAX_CYCLE = 10000

for i in range(MAX_CYCLE):

    cycle = run_cycle()

    prices = cycle["prices"]
    signals = cycle["signals"]
    account_state = cycle["account"]

    with placeholder.container():

        # ==========================================
        # PRICE
        # ==========================================
        st.subheader("📈 실시간 가격")

        for name, price in prices.items():
            if price is None:
                st.warning(f"{name}: 데이터 없음")
            else:
                st.write(f"**{name}** : {price:,}원")

        st.divider()

        # ==========================================
        # ACCOUNT
        # ==========================================
        st.subheader("💰 계좌 상태")

        total_asset = get_total_asset(prices)
        pnl, pnl_pct = get_total_pnl(prices)

        st.write(f"현금: {account_state['balance']:,}원")
        st.write(f"총 자산: {total_asset:,}원")
        st.write(f"손익: {pnl:+,}원 ({pnl_pct:+.2f}%)")

        st.divider()

        # ==========================================
        # POSITIONS
        # ==========================================
        st.subheader("📦 보유 종목")

        positions = get_positions()

        if not positions:
            st.info("보유 종목 없음")
        else:
            for name, pos in positions.items():
                current_price = prices.get(name, 0)

                st.write(
                    f"**{name}** | "
                    f"수량: {pos['qty']} | "
                    f"평단: {pos['avg_price']:,} | "
                    f"현재가: {current_price:,}"
                )

        st.divider()

        # ==========================================
        # TRADES
        # ==========================================
        st.subheader("🧾 최근 거래")

        trades = get_recent_trades()

        if not trades:
            st.info("거래 없음")
        else:
            st.dataframe(pd.DataFrame(trades), use_container_width=True)

        st.divider()

        # ==========================================
        # SIGNALS
        # ==========================================
        st.subheader("🧠 AI 신호")

        for name, sig in signals.items():

            color = "🟡"

            if sig["action"] == "BUY":
                color = "🟢"
            elif sig["action"] == "SELL":
                color = "🔴"

            st.write(
                f"{color} **{name}** | "
                f"{sig['action']} | "
                f"Score: {sig['score']} | "
                f"{sig['price']:,}"
            )

    # ======================================================
    # REFRESH CONTROL
    # ======================================================

    time.sleep(REFRESH_SECONDS)
