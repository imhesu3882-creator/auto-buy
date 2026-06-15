import streamlit as st
import time
import pandas as pd

from config import *
from broker import run_cycle, get_total_asset, get_total_pnl, get_positions, get_recent_trades

st.set_page_config(page_title="AI Auto Trader", layout="wide")

st.title("📊 Auto Trading Dashboard 🤖")

placeholder = st.empty()

# ==========================================================
# Streamlit 정상 루프 (이게 핵심)
# ==========================================================

for _ in range(10000):

    cycle = run_cycle()

    prices = cycle["prices"]
    signals = cycle["signals"]
    account_state = cycle["account"]

    with placeholder.container():

        st.subheader("📈 가격")

        for name, price in prices.items():
            st.write(f"{name}: {price}")

        st.subheader("💰 계좌")

        total_asset = get_total_asset(prices)
        pnl, pnl_pct = get_total_pnl(prices)

        st.write(f"현금: {account_state['balance']}")
        st.write(f"총자산: {total_asset}")
        st.write(f"손익: {pnl} ({pnl_pct:.2f}%)")

        st.subheader("📦 포지션")
        st.write(get_positions())

        st.subheader("🧾 거래")
        st.dataframe(pd.DataFrame(get_recent_trades()))

        st.subheader("🧠 신호")
        st.write(signals)

    time.sleep(REFRESH_SECONDS)
