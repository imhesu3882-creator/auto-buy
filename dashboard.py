"""
==========================================================
AI AUTO TRADER
dashboard.py
----------------------------------------------------------
HTS UI (Streamlit)
==========================================================
"""

import streamlit as st
import time
import pandas as pd

from config import *
from broker import *

# ==========================================================
# 페이지 설정
# ==========================================================

st.set_page_config(
    page_title="AI Auto Trader",
    layout="wide"
)

st.title("📊 Auto Trading Dashboard 🤖")

# ==========================================================
# 자동 실행 사이클
# ==========================================================

placeholder = st.empty()

while True:

    cycle = run_cycle()

    prices = cycle["prices"]
    signals = cycle["signals"]
    account_state = cycle["account"]

    with placeholder.container():

        # ==========================================
        # 가격
        # ==========================================

        st.subheader("📈 실시간 가격")

        for name, price in prices.items():

            if price is None:
                st.error(f"{name} : 데이터 오류")
            else:
                st.write(f"**{name}** : {price:,}원")

        st.divider()

        # ==========================================
        # 계좌
        # ==========================================

        total_asset = get_total_asset(prices)

        st.subheader("💰 계좌")

        st.write(f"현금: {account_state['balance']:,}원")

        st.write(f"총 자산: {total_asset:,}원")

        pnl, pnl_pct = get_total_pnl(prices)

        st.write(f"손익: {pnl:+,}원 ({pnl_pct:+.2f}%)")

        st.divider()

        # ==========================================
        # 포지션
        # ==========================================

        st.subheader("📦 보유 종목")

        positions = get_positions()

        if len(positions) == 0:
            st.info("보유 없음")
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
        # 거래 내역
        # ==========================================

        st.subheader("🧾 거래 내역")

        trades = get_recent_trades()

        if len(trades) == 0:
            st.info("거래 없음")
        else:
            df = pd.DataFrame(trades)
            st.dataframe(df, use_container_width=True)

        st.divider()

        # ==========================================
        # AI 신호
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

    time.sleep(REFRESH_SECONDS)
  
