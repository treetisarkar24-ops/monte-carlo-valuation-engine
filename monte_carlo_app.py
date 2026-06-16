"""
Monte Carlo Valuation Engine — interactive front door.

Download the input template, fill in a company's numbers, upload it back, and the
engine runs a deterministic DCF plus a Monte Carlo simulation and shows where
today's market price sits inside the full distribution of intrinsic values.

This file is the thin web layer ONLY. It does not touch the frozen math in
engine/ — it calls excel_loader.excel_to_inputs() and the engine exactly the way
the command line does.
"""
from __future__ import annotations

import io
import json
import os
import sys

import numpy as np
import pandas as pd
import altair as alt
import streamlit as st

# --- make the frozen engine + loader importable, wherever this is deployed ---
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "engine"))
sys.path.insert(0, os.path.join(HERE, "runtime"))

from excel_loader import excel_to_inputs, TemplateError  # noqa: E402
from dcf import DCFInputs, run_dcf, compute_wacc          # noqa: E402
from mc_config import MCConfig                            # noqa: E402
from mc_engine import run_monte_carlo, summarize          # noqa: E402

TEMPLATE_PATH = os.path.join(HERE, "templates", "MC_Input_Template_v2.xlsx")
EXAMPLE_PATH = os.path.join(HERE, "templates", "filled_ko_typed.xlsx")

st.set_page_config(page_title="Monte Carlo Valuation Engine", page_icon="*", layout="centered")

st.title("Monte Carlo Valuation Engine")
st.markdown(
    "A DCF that returns a **distribution** of intrinsic values, not a single guess. "
    "Fill the template with a company's numbers, upload it, and see where today's "
    "market price sits inside the full range the fundamentals can support."
)

# ---------------------------------------------------------------- Step 1: template
st.header("1 · Get the template")
st.markdown(
    "Download the input template and fill in the **YOUR VALUE** column. "
    "Every field is labelled with its unit and a Microsoft example to copy the shape from."
)
col_a, col_b = st.columns(2)
with col_a:
    if os.path.exists(TEMPLATE_PATH):
        with open(TEMPLATE_PATH, "rb") as f:
            st.download_button(
                "Download the blank template (.xlsx)",
                data=f.read(),
                file_name="MC_Input_Template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
with col_b:
    if os.path.exists(EXAMPLE_PATH):
        with open(EXAMPLE_PATH, "rb") as f:
            st.download_button(
                "Download a filled example (Coca-Cola)",
                data=f.read(),
                file_name="MC_filled_example_KO.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

# ---------------------------------------------------------------- Step 2: upload
st.header("2 · Upload your filled template")
uploaded = st.file_uploader("Drop your filled .xlsx here", type=["xlsx"])
use_example = st.checkbox("Or just run the Coca-Cola example", value=False)

market_price = st.number_input(
    "Today's market price per share (optional) — used to locate the price inside the distribution",
    min_value=0.0, value=0.0, step=1.0,
)

n_sims = st.select_slider(
    "Number of simulations", options=[1000, 2000, 5000, 10000], value=2000,
    help="More paths = a smoother distribution but a slightly slower run.",
)

run = st.button("Run the valuation", type="primary")

# ---------------------------------------------------------------- run + results
def load_inputs():
    if uploaded is not None:
        tmp = os.path.join(HERE, "_uploaded_tmp.xlsx")
        with open(tmp, "wb") as f:
            f.write(uploaded.getbuffer())
        try:
            return excel_to_inputs(tmp)
        finally:
            os.remove(tmp)
    if use_example and os.path.exists(EXAMPLE_PATH):
        return excel_to_inputs(EXAMPLE_PATH)
    return None

if run:
    try:
        loaded = load_inputs()
    except TemplateError as exc:
        st.error(f"The template has problems:\n\n{exc}")
        st.stop()
    except Exception as exc:  # noqa: BLE001
        st.error(f"Could not read that file: {exc}")
        st.stop()

    if loaded is None:
        st.warning("Upload a filled template, or tick the Coca-Cola example box, then run.")
        st.stop()

    data, warnings = loaded
    for w in warnings:
        st.warning(w)

    inp = DCFInputs(**data)
    wacc = compute_wacc(inp)
    deterministic = run_dcf(inp)
    mp = market_price if market_price > 0 else None
    samples = run_monte_carlo(inp, MCConfig(n_simulations=int(n_sims), random_seed=42))
    summary = summarize(samples, market_price=mp)

    st.header("3 · Result")
    c1, c2, c3 = st.columns(3)
    c1.metric("WACC", f"{wacc * 100:.2f}%")
    c2.metric("Deterministic DCF", f"{deterministic:,.2f} / share")
    c3.metric("MC median", f"{summary.median:,.2f} / share")

    c4, c5, c6 = st.columns(3)
    c4.metric("P5 (low)", f"{summary.percentiles[5]:,.2f}")
    c5.metric("P95 (high)", f"{summary.percentiles[95]:,.2f}")
    c6.metric("Simulations", f"{summary.n:,}")

    if summary.market_percentile is not None:
        pct = summary.market_percentile
        verdict = "cheap" if pct < 25 else ("rich" if pct > 75 else "fairly valued")
        st.subheader("Where the market price sits")
        st.markdown(
            f"Today's price of **{mp:,.2f}** lands at the **{pct:.0f}th percentile** "
            f"of the simulated distribution — {summary.n:,} runs, and {pct:.0f}% of them "
            f"valued the company *below* today's price. On this fixture the market looks "
            f"**{verdict}** relative to the fundamentals supplied."
        )

    # distribution chart
    df = pd.DataFrame({"value": samples})
    base = alt.Chart(df).mark_bar(opacity=0.85).encode(
        alt.X("value:Q", bin=alt.Bin(maxbins=40), title="Intrinsic value per share"),
        alt.Y("count()", title="Simulations"),
    )
    layers = [base]
    rule_median = alt.Chart(pd.DataFrame({"v": [summary.median]})).mark_rule(
        color="#1D9E75", size=2
    ).encode(x="v:Q")
    layers.append(rule_median)
    if mp is not None:
        rule_market = alt.Chart(pd.DataFrame({"v": [mp]})).mark_rule(
            color="#D85A30", size=2, strokeDash=[4, 3]
        ).encode(x="v:Q")
        layers.append(rule_market)
    st.altair_chart(alt.layer(*layers).properties(height=320), use_container_width=True)
    st.caption(
        "Green line = MC median." + ("  Orange dashed line = today's market price." if mp else "")
    )

    # downloadable result
    out = {
        "inputs": data,
        "wacc": wacc,
        "deterministic_per_share": deterministic,
        "mc": {
            "n": summary.n,
            "mean": summary.mean,
            "median": summary.median,
            "std": summary.std,
            "min": summary.minimum,
            "max": summary.maximum,
            "percentiles": summary.percentiles,
            "market_price": summary.market_price,
            "market_percentile": summary.market_percentile,
        },
    }
    st.download_button(
        "Download these results (.json)",
        data=json.dumps(out, indent=2),
        file_name="mc_valuation_result.json",
        mime="application/json",
    )

st.divider()
st.caption(
    "Not investment advice. Every output is a statement about the assumptions you "
    "supplied, not a recommendation."
)
