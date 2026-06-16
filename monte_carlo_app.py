"""
Monte Carlo Valuation Engine — interactive front door.

Runs the REAL engine end to end: a deterministic DCF, then continuous Monte
Carlo with self-resolved convergence (z*), then the shocked engine with its own
convergence (z**), benchmarked against the folk 10,000-path convention. Draws
the distribution and BOTH convergence curves, and hands back the same templated
PDF + Excel report every visitor would get for their own company.

Thin web layer ONLY. It calls excel_loader + the frozen engine via
runtime/live_pipeline.py and the runtime report builders. No DCF / Monte Carlo /
shock / convergence logic lives here.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile

import numpy as np
import pandas as pd
import altair as alt
import streamlit as st

# --- make the frozen engine + loader + runtime builders importable ---
HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "engine")
RUNTIME = os.path.join(HERE, "runtime")
sys.path.insert(0, ENGINE)
sys.path.insert(0, RUNTIME)

from excel_loader import excel_to_inputs, TemplateError   # noqa: E402
from dcf import DCFInputs                                 # noqa: E402
import live_pipeline as lp                                # noqa: E402
import build_pdf_report                                   # noqa: E402
import build_excel_output                                 # noqa: E402

TEMPLATE_PATH = os.path.join(HERE, "templates", "MC_Input_Template_v2.xlsx")
EXAMPLE_XLSX = os.path.join(HERE, "templates", "filled_ko_typed.xlsx")

# Built-in worked examples — precomputed engine runs, loaded instantly.
EXAMPLES = {
    "Amazon (AMZN)": {
        "results": "amazon_results.json", "fixture": "amazon_fixture.json",
        "company": "Amazon.com, Inc.", "ticker": "AMZN",
        "price": 246.03, "date": "2026-06-05", "base_year": 2025,
    },
    "Coca-Cola (KO)": {
        "results": "ko_results.json", "fixture": "ko_fixture.json",
        "company": "The Coca-Cola Company", "ticker": "KO",
        "price": 82.67, "date": "2026-06-15", "base_year": 2025,
    },
}

NAVY = "#1F3A5F"
GREEN = "#1D9E75"
ORANGE = "#D85A30"

st.set_page_config(page_title="Monte Carlo Valuation Engine", page_icon="*", layout="centered")

st.title("Monte Carlo Valuation Engine")
st.markdown(
    "A DCF that returns a **distribution** of intrinsic values, not a single guess. "
    "The engine resolves its own sample size — **z\\*** for the continuous run and "
    "**z\\*\\*** once discrete shocks are layered on — instead of defaulting to the "
    "folk 10,000 paths. You get the full distribution, both convergence curves, and a "
    "downloadable PDF + Excel report."
)

# ============================================================ Step 1: template
st.header("1 · Get the template")
st.markdown(
    "Download the input template and fill in the **YOUR VALUE** column. "
    "Every field is labelled with its unit and an example to copy the shape from."
)
col_a, col_b = st.columns(2)
with col_a:
    if os.path.exists(TEMPLATE_PATH):
        with open(TEMPLATE_PATH, "rb") as f:
            st.download_button("Download the blank template (.xlsx)", data=f.read(),
                               file_name="MC_Input_Template.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
with col_b:
    if os.path.exists(EXAMPLE_XLSX):
        with open(EXAMPLE_XLSX, "rb") as f:
            st.download_button("Download a filled example (Coca-Cola)", data=f.read(),
                               file_name="MC_filled_example_KO.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ============================================================ Step 2: choose input
st.header("2 · Choose what to value")
mode = st.radio(
    "Run a built-in example, or upload your own filled template:",
    ["Amazon (AMZN) — example", "Coca-Cola (KO) — example", "Upload my filled template"],
    index=0,
)
is_upload = mode.startswith("Upload")

uploaded = None
up_company = "Your Company"
up_ticker = "—"
if is_upload:
    uploaded = st.file_uploader("Drop your filled .xlsx here", type=["xlsx"])
    cc1, cc2 = st.columns(2)
    up_company = cc1.text_input("Company name (for the report)", value="Your Company")
    up_ticker = cc2.text_input("Ticker", value="—")

# market price
if is_upload:
    default_price = 0.0
else:
    default_price = EXAMPLES["Amazon (AMZN)" if mode.startswith("Amazon") else "Coca-Cola (KO)"]["price"]
market_price = st.number_input(
    "Today's market price per share — used to place the price inside the distribution",
    min_value=0.0, value=float(default_price), step=1.0,
)

run = st.button("Run the valuation", type="primary")

# ============================================================ input signature
def current_signature():
    up_sig = (uploaded.name, uploaded.size) if uploaded is not None else None
    return (mode, up_sig, up_company, up_ticker, round(float(market_price), 4))

# ============================================================ helpers
def example_key():
    return "Amazon (AMZN)" if mode.startswith("Amazon") else "Coca-Cola (KO)"

def build_example(price):
    cfg = EXAMPLES[example_key()]
    results = json.load(open(os.path.join(RUNTIME, cfg["results"])))
    base = DCFInputs(**json.load(open(os.path.join(RUNTIME, cfg["fixture"]))))
    meta = lp.build_templated_meta(
        base, results, company=cfg["company"], ticker=cfg["ticker"],
        market_price=price, market_date=cfg["date"], base_year=cfg["base_year"],
        fixture_rel=cfg["fixture"],
    )
    meta["__meta_path__"] = os.path.join(RUNTIME, "x_meta.json")  # dirname is what matters
    return results, meta

def build_upload(data, price, company, ticker, tmpdir, cb):
    base = DCFInputs(**data)
    results = lp.run_full(base, progress=cb)
    fx = os.path.join(tmpdir, "upload_fixture.json")
    json.dump(data, open(fx, "w"))
    meta = lp.build_templated_meta(
        base, results, company=company or "Your Company", ticker=ticker or "—",
        market_price=price, market_date="", base_year=None,
        fixture_rel="upload_fixture.json",
    )
    meta["__meta_path__"] = os.path.join(tmpdir, "meta.json")
    return results, meta

def make_reports(results, meta):
    """Build PDF + Excel, return (pdf_bytes, xlsx_bytes)."""
    d = tempfile.mkdtemp()
    pdf = os.path.join(d, "report.pdf")
    xlsx = os.path.join(d, "report.xlsx")
    build_pdf_report.build(results, meta, pdf)
    build_excel_output.build(results, meta, xlsx)
    return open(pdf, "rb").read(), open(xlsx, "rb").read()

def hist_df(text):
    rows = []
    for line in (text or "").splitlines():
        if "|" not in line:
            continue
        left, right = line.split("|", 1)
        try:
            v = float(left.strip())
        except ValueError:
            continue
        toks = right.strip().split()
        if not toks:
            continue
        try:
            c = int(toks[-1])
        except ValueError:
            continue
        rows.append((v, c))
    return pd.DataFrame(rows, columns=["value", "count"])

def convergence_chart(pair, title, color):
    df = pd.DataFrame({"n": pair["n_grid"], "scatter": pair["scatter"]})
    line = alt.Chart(df).mark_line(point=True, color=color).encode(
        x=alt.X("n:Q", scale=alt.Scale(type="log"), title="Simulations n (log)"),
        y=alt.Y("scatter:Q", title="Scatter of run-means ($/sh)"),
        tooltip=["n", alt.Tooltip("scatter", format=".3f")],
    )
    bar = alt.Chart(pd.DataFrame({"y": [pair["precision_bar"]]})).mark_rule(
        color="#999999", strokeDash=[4, 3]).encode(y="y:Q")
    zline = alt.Chart(pd.DataFrame({"x": [pair["z_star"]]})).mark_rule(
        color=color, size=2).encode(x="x:Q")
    folk_df = pd.DataFrame({"x": [10000], "lbl": ["folk 10,000"]})
    folk = alt.Chart(folk_df).mark_rule(
        color="#C0392B", strokeDash=[6, 4], size=1.5).encode(x="x:Q")
    folk_txt = alt.Chart(folk_df).mark_text(
        align="right", dx=-4, dy=-8, color="#C0392B", fontSize=11,
        angle=0).encode(x="x:Q", text="lbl:N")
    return alt.layer(line, bar, zline, folk, folk_txt).properties(height=260, title=title)

# ============================================================ run
if run:
    if is_upload and uploaded is None:
        st.warning("Upload a filled template, then click Run — or pick one of the examples above.")
        st.stop()
    if market_price <= 0:
        st.warning("Enter today's market price per share so the report can place it inside the distribution.")
        st.stop()

    tmpdir = tempfile.mkdtemp()
    try:
        if is_upload:
            tmp = os.path.join(tmpdir, "uploaded.xlsx")
            with open(tmp, "wb") as f:
                f.write(uploaded.getbuffer())
            try:
                data, warnings = excel_to_inputs(tmp)
            except TemplateError as exc:
                st.error(f"The template has problems:\n\n{exc}")
                st.stop()
            st.info(
                "Running the full engine: continuous convergence (z\\*), then the shocked "
                "engine (z\\*\\*), then the 10,000-path benchmark. This takes a minute or two "
                "— it's doing the real work, not a shortcut."
            )
            prog = st.progress(0.0, text="Starting…")
            def cb(msg, frac):
                prog.progress(min(float(frac), 1.0), text=msg)
            results, meta = build_upload(data, market_price, up_company, up_ticker, tmpdir, cb)
            prog.empty()
        else:
            warnings = []
            with st.spinner("Loading the worked example…"):
                results, meta = build_example(market_price)

        pdf_bytes, xlsx_bytes = make_reports(results, meta)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Something went wrong while running the engine: {exc}")
        st.stop()

    st.session_state["mc"] = {
        "sig": current_signature(),
        "warnings": list(warnings),
        "results": results,
        "meta": meta,
        "pdf": pdf_bytes,
        "xlsx": xlsx_bytes,
        "price": float(market_price),
        "label": meta["company"] + (f" ({meta['ticker']})" if meta.get("ticker") else ""),
    }

# ============================================================ results view
state = st.session_state.get("mc")
if state is not None and state["sig"] != current_signature():
    st.session_state.pop("mc", None)
    state = None
    st.info("Inputs changed. Click **Run the valuation** to refresh the results.")

if state is not None:
    for w in state["warnings"]:
        st.warning(w)

    results = state["results"]
    meta = state["meta"]
    mp = state["price"]
    central = results["central"]
    cont = results["cont"]
    cprod = cont["production"]
    shock = results.get("shock", {})

    st.header(f"3 · {state['label']}")

    c1, c2, c3 = st.columns(3)
    c1.metric("Central DCF / share", f"${central['value']:,.2f}")
    c2.metric("WACC", f"{central['wacc']*100:.2f}%")
    c3.metric("Market price", f"${mp:,.2f}")

    c4, c5, c6 = st.columns(3)
    c4.metric("Continuous median (z\\*)", f"${cprod['median']:,.2f}")
    if shock:
        c5.metric("Shocked median (z\\*\\*)", f"${shock['production']['median']:,.2f}")
    c6.metric("z\\* paths", f"{cont['pair']['z_star']:,}")

    # market position
    pp = {int(k): v for k, v in cprod["pct"].items()}
    if mp >= cprod["max"]:
        where = f"**above** the maximum simulated value (${cprod['max']:,.2f})"
    elif mp <= cprod["min"]:
        where = f"**below** the minimum simulated value (${cprod['min']:,.2f})"
    else:
        below = [k for k in sorted(pp) if pp[k] <= mp]
        where = f"around the **{(below[-1] if below else 0)}th–{(below[-1]+5 if below else 5)}th percentile**"
    gap = abs(mp - cprod["median"]) / cprod["median"] * 100.0
    side = "above" if mp > cprod["median"] else "below"
    st.markdown(
        f"Today's price of **${mp:,.2f}** sits {where} of the continuous distribution — "
        f"**{gap:.1f}% {side}** the engine's median of ${cprod['median']:,.2f}."
    )

    # distribution chart
    st.subheader("Distribution of intrinsic value")
    dfh = hist_df(cont.get("histogram", ""))
    if not dfh.empty:
        bars = alt.Chart(dfh).mark_bar(opacity=0.85, color=NAVY).encode(
            x=alt.X("value:Q", title="Intrinsic value per share ($)"),
            y=alt.Y("count:Q", title="Simulations"),
            tooltip=["value", "count"],
        )
        layers = [bars]
        layers.append(alt.Chart(pd.DataFrame({"v": [cprod["median"]]})).mark_rule(
            color=GREEN, size=2).encode(x="v:Q"))
        layers.append(alt.Chart(pd.DataFrame({"v": [mp]})).mark_rule(
            color=ORANGE, size=2, strokeDash=[4, 3]).encode(x="v:Q"))
        st.altair_chart(alt.layer(*layers).properties(height=320), use_container_width=True)
        st.caption("Green line = continuous median.  Orange dashed line = today's market price.")

    # convergence charts
    st.subheader("Where the simulation converges")
    st.markdown(
        "Each curve shows how the disagreement between independent run-means (the "
        "*scatter*) shrinks as the number of paths grows. The grey dashed line is the "
        "precision bar; the solid line marks where the engine resolved — **z\\*** for the "
        "continuous engine, **z\\*\\*** once shocks are added."
    )
    g1, g2 = st.columns(2)
    with g1:
        st.altair_chart(convergence_chart(cont["pair"], f"Continuous · z* = {cont['pair']['z_star']:,}", NAVY),
                        use_container_width=True)
    if shock:
        with g2:
            st.altair_chart(convergence_chart(shock["pair"], f"Shocked · z** = {shock['pair']['z_star']:,}", ORANGE),
                            use_container_width=True)

    # benchmark callout
    if "benchmark" in cont:
        b = cont["benchmark"]
        st.info(
            f"**Benchmark vs the folk 10,000:** the engine resolved at z\\* = "
            f"{b['z_star']:,} paths — **{b['compute_ratio']}×** the compute of a fixed "
            f"10,000 run — yet the mean differs by only **{b['mean_gap_pct']:.1f}%** "
            f"(${b['z_mean']:,.2f} vs ${b['folk_mean']:,.2f}). The engine picks the sample "
            f"size this company actually needs."
        )

    # percentile table
    st.subheader("Percentiles")
    order = [5, 10, 25, 50, 75, 90, 95]
    cont_pct = {int(k): v for k, v in cprod["pct"].items()}
    table = {"Percentile": [f"P{k}" for k in order],
             "Continuous (z*)": [f"${cont_pct.get(k, float('nan')):,.2f}" for k in order]}
    if shock:
        sp = {int(k): v for k, v in shock["production"]["pct"].items()}
        table["Shocked (z**)"] = [f"${sp.get(k, float('nan')):,.2f}" for k in order]
    st.dataframe(pd.DataFrame(table), hide_index=True, use_container_width=True)

    # downloads
    st.subheader("Download the full report")
    d1, d2 = st.columns(2)
    slug = (meta.get("ticker") or meta.get("company") or "valuation").replace(" ", "_").replace("—", "co")
    d1.download_button("Download PDF report", data=state["pdf"],
                       file_name=f"{slug}_Valuation_Report.pdf", mime="application/pdf")
    d2.download_button("Download Excel workbook", data=state["xlsx"],
                       file_name=f"{slug}_Output.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.divider()
st.caption(
    "Not investment advice. Every output is a statement about the assumptions supplied, "
    "not a recommendation. Engine applied as-is; no DCF / Monte Carlo / shock / "
    "convergence logic is modified by this interface."
)
