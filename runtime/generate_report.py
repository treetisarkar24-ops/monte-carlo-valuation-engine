#!/usr/bin/env python3
"""
generate_report.py — standardised case-study report generator.

Turns a `<slug>_results.json` (produced by a case-study runner) plus a small
`<slug>_meta.json` (company name, market price, assumptions, interpretation
prose) into a standardised Markdown case study in the same shape as the MSFT
reference report.

This is a presentation-layer tool. It reads results that the engine already
produced; it does not run, import, or modify any DCF / Monte Carlo / shock /
convergence logic.

Usage:
    python3 generate_report.py amazon_results.json amazon_meta.json -o AMZN_Case_Study.md
"""
from __future__ import annotations

# --- engine path bootstrap (auto-added during reorg; frozen engine lives in ../engine) ---
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "engine"))
# --- end bootstrap ---

import argparse
import json


def f0(x):  # whole-dollar
    return f"${x:,.0f}"


def f2(x):  # two-dp dollar
    return f"${x:,.2f}"


def pc(x, dp=1):  # percent from a raw percent number
    return f"{x:.{dp}f}%"


def market_position(price, prod):
    """Where the market price sits relative to a production distribution."""
    pcts = {int(k): v for k, v in prod["pct"].items()}
    lo, hi = prod["min"], prod["max"]
    if price >= hi:
        return f"above the maximum simulated value ({f2(hi)}) — beyond the ~100th percentile"
    if price <= lo:
        return f"below the minimum simulated value ({f2(lo)}) — beneath the ~0th percentile"
    below = [p for p in sorted(pcts) if pcts[p] <= price]
    above = [p for p in sorted(pcts) if pcts[p] >= price]
    lo_p = below[-1] if below else 0
    hi_p = above[0] if above else 100
    return f"between the {lo_p}th and {hi_p}th percentile"


def year_tables(meta):
    """Build the year-by-year assumption + FCF tables from the fixture.

    Requires meta['fixture'] (path to the DCFInputs JSON) and optionally
    meta['base_year']. Returns (window_line, assumptions_md, fcf_md) or
    (None, None, None) if the fixture/engine is unavailable.
    """
    fixture = meta.get("fixture")
    if not fixture:
        return None, None, None
    try:
        import os
        from dcf import (DCFInputs, project_revenue, project_ebit, project_nopat,
                         project_da, project_capex, project_dnwc, project_fcf)
        path = fixture if os.path.exists(fixture) else os.path.join(
            os.path.dirname(os.path.abspath(meta["__meta_path__"])), fixture) \
            if meta.get("__meta_path__") else fixture
        inp = DCFInputs(**json.load(open(path)))
    except Exception:
        return None, None, None

    base = meta.get("base_year")
    fy = inp.forecast_years
    rev = project_revenue(inp)
    ebit = project_ebit(rev, inp)
    nopat = project_nopat(ebit, inp)
    da = project_da(rev, inp)
    capex = project_capex(rev, inp)
    dnwc = project_dnwc(rev, inp)
    fcf = project_fcf(nopat, rev, inp)

    def yr(i):
        return f"FY{base + 1 + i}" if base else f"Year {i + 1}"

    base_label = f"FY{base}" if base else "Year 0 (today)"
    if base:
        window = (f"**Forecast window:** base year **FY{base}** (reported actuals, not "
                  f"forecast); explicit forecast **FY{base+1}–FY{base+fy}** ({fy} years); "
                  f"terminal value from FY{base+fy+1} onward.")
    else:
        window = (f"**Forecast window:** year 0 = today (actuals); explicit forecast "
                  f"years 1–{fy}; terminal value thereafter.")

    a = ["| Year | Revenue growth | Operating margin | Capex % rev | D&A % rev | ΔNWC % rev |",
         "|---|---|---|---|---|---|"]
    for i in range(fy):
        a.append(f"| {yr(i)} | {inp.revenue_growth[i]*100:.0f}% | {inp.operating_margin[i]*100:.1f}% "
                 f"| {inp.capex_pct_revenue[i]*100:.1f}% | {inp.da_pct_revenue[i]*100:.1f}% "
                 f"| {inp.nwc_pct_revenue[i]*100:.1f}% |")

    f = [f"| Year | Revenue | EBIT | NOPAT | + D&A | − Capex | − ΔNWC | **FCFF** |",
         "|---|---|---|---|---|---|---|---|",
         f"| {base_label} | {f0(inp.starting_revenue)} | — | — | — | — | — | — |"]
    for i in range(fy):
        f.append(f"| {yr(i)} | {f0(rev[i])} | {f0(ebit[i])} | {f0(nopat[i])} | {f0(da[i])} "
                 f"| ({f0(capex[i])}) | ({f0(dnwc[i])}) | **{f0(fcf[i])}** |")
    return window, "\n".join(a), "\n".join(f)


def assumptions_table(meta):
    rows = ["| Input | Value | Rationale |", "|---|---|---|"]
    for inp, val, why in meta["assumptions"]:
        rows.append(f"| {inp} | {val} | {why} |")
    return "\n".join(rows)


def pct_line(prod):
    p = {int(k): v for k, v in prod["pct"].items()}
    order = [5, 10, 25, 50, 75, 90, 95]
    return " · ".join(f"P{k} {f2(p[k])}" for k in order if k in p)


def conv_table(pair):
    rows = ["| n | Scatter | ", "|---|---|"]
    for n, s in zip(pair["n_grid"], pair["scatter"]):
        rows.append(f"| {n:,} | {s:.2f} |")
    return "\n".join(rows)


def build(results, meta):
    co, tk = meta["company"], meta["ticker"]
    central = results["central"]
    cont = results["cont"]
    shock = results.get("shock", {})
    out = []
    A = out.append

    A(f"# {co} ({tk})")
    A("## Real-World Valuation Case Study — Monte Carlo DCF Engine\n")
    A(f"**Purpose:** {meta.get('purpose', 'A production application of the finished engine to a real, large-cap company. No engine, convergence, N_GRID, or shock-calibration logic was modified.')}\n")
    A(f"**Base fixture:** {meta.get('base_note', '')}\n")
    A("---\n")

    # 1. Assumptions
    A("## 1. Assumptions Used (DCFInputs Fixture)\n")
    A(assumptions_table(meta) + "\n")
    A(f"> {meta.get('assumptions_caveat', 'Inputs are analyst assumptions derived from the latest reported actuals; they encode a deliberately conservative central view, not a forecast.')}\n")
    A("---\n")

    # 2. Deterministic
    A("## 2. Deterministic Central Case\n")
    window, assum_yr, fcf_yr = year_tables(meta)
    if window:
        A(window + "\n")
    A("| Metric | Value |")
    A("|---|---|")
    A(f"| WACC | **{pc(central['wacc']*100, 3)}** |")
    A(f"| Terminal spread (WACC − g) | {pc((central['wacc']-meta['terminal_growth'])*100, 2)} |")
    A(f"| **Central DCF per share** | **{f2(central['value'])}** |")
    A("")
    A(f"The deterministic gate **{'passes' if central['value']>0 and meta['terminal_growth']<central['wacc'] else 'fails'}** "
      f"(value {'positive' if central['value']>0 else 'non-positive'}, terminal growth "
      f"{pc(meta['terminal_growth']*100)} {'<' if meta['terminal_growth']<central['wacc'] else '>='} WACC "
      f"{pc(central['wacc']*100)}), so the full stochastic pipeline was run.\n")
    if assum_yr:
        A("**Year-by-year assumptions (the trajectory inputs that drive the central case):**\n")
        A(assum_yr + "\n")
    if fcf_yr:
        A("**Resulting unlevered free-cash-flow (FCFF) trajectory, all figures in the fixture's currency units (USD millions):**\n")
        A(fcf_yr + "\n")
    A("---\n")

    # 3. Continuous
    p = cont["pair"]; prod = cont["production"]
    A("## 3. Continuous Monte Carlo (z*)\n")
    A(f"**Convergence sweep ({p['batches_used']}-batch apparatus, seed 42):**\n")
    A(conv_table(p) + "\n")
    A(f"- z_pct (rule 2) = **{p['z_pct']:,}**, z_elbow (rule 3) = **{p['z_elbow']:,}**")
    A(f"- **z\\* = {p['z_star']:,}**, decision margin = **{pc(p['decision_margin_pct'])}**, σ ≈ {f2(p['sigma_estimate'])}, adequately resolved = {p['adequately_resolved']}\n")
    A(f"**Production run at z\\* = {prod['n']:,}:**\n")
    A("| Statistic | Value |")
    A("|---|---|")
    A(f"| Mean | {f2(prod['mean'])} |")
    A(f"| Median | {f2(prod['median'])} |")
    A(f"| Std dev | {f2(prod['std'])} |")
    A(f"| Min / Max | {f2(prod['min'])} / {f2(prod['max'])} |")
    A(f"| Fraction negative | **{pc(cont['frac_negative_pct'])}** |")
    A("")
    A(f"**Percentiles:** {pct_line(prod)}.\n")
    if "benchmark" in cont:
        b = cont["benchmark"]
        A(f"**Benchmark vs. folk number (n = {b['folk_n']:,}):** z\\* uses **{b['compute_ratio']}×** the compute "
          f"yet the mean differs by only **{pc(b['mean_gap_pct'])}** ({f2(b['z_mean'])} vs {f2(b['folk_mean'])}). "
          "The empirically-derived sample size reproduces the folk-number answer at a fraction of the cost.\n")
    A("---\n")

    # 4. Shocked
    if shock:
        sp = shock["pair"]; spr = shock["production"]
        A("## 4. Shocked Monte Carlo (z**)\n")
        A(f"- z_pct = {sp['z_pct']:,}, z_elbow = {sp['z_elbow']:,} → **z\\*\\* = {sp['z_star']:,}**")
        A(f"- decision margin = **{pc(sp['decision_margin_pct'])}**, batches recommended = **{sp['batches_recommended']}** "
          f"(vs {sp['batches_used']} used), adequately resolved = {sp['adequately_resolved']}\n")
        A(f"**Production run at z\\*\\* = {spr['n']:,}:**\n")
        A("| Statistic | Value |")
        A("|---|---|")
        A(f"| Mean | {f2(spr['mean'])} |")
        A(f"| Median | {f2(spr['median'])} |")
        A(f"| Std dev | {f2(spr['std'])} |")
        A(f"| Min / Max | {f2(spr['min'])} / {f2(spr['max'])} |")
        A(f"| Fraction negative | **{pc(shock['frac_negative_pct'])}** |")
        A("")
        A(f"**Percentiles:** {pct_line(spr)}.\n")
        A(f"{meta.get('shock_interpretation','')}\n")
        A("---\n")

        # 5. Channels
        A("## 5. Shock Channel Behaviour\n")
        chans = list(shock["fires_all"].keys())
        A("| | " + " | ".join(c.capitalize() for c in chans) + " |")
        A("|" + "---|"*(len(chans)+1))
        A("| Fires — all paths | " + " | ".join(str(shock["fires_all"][c]) for c in chans) + " |")
        A("| Fires — worst 5% tail | " + " | ".join(f"**{shock['fires_worst5'][c]}**" for c in chans) + " |")
        A("")
        A(f"- **Shock-free paths: {pc(shock['shock_free_pct'])}**. Total fires: {shock['total_fires']:,}; "
          f"mean cumulative stress {shock['mean_stress']:.3f}; max stress {shock['max_stress']:.2f}.")
        A(f"- {meta.get('channel_interpretation','')}\n")
        A("---\n")

    # 6. Market percentile
    mp, md = meta["market_price"], meta.get("market_date", "")
    A("## 6. Market Percentile Analysis\n")
    A(f"{co} traded at **{f2(mp)}** {('on ' + md) if md else ''}.\n")
    A(f"- Continuous distribution: the market price sits {market_position(mp, prod)}.")
    if shock:
        A(f"- Shocked distribution: the market price sits {market_position(mp, shock['production'])}.")
    A("")
    A(f"{meta.get('market_interpretation','')}\n")
    A("---\n")

    # 7. Seeds
    if results.get("seeds"):
        A("## 7. Seed Robustness\n")
        A("| Seed | z* (cont) | cont margin | z** (shock) | shock margin |")
        A("|---|---|---|---|---|")
        for seed, r in results["seeds"].items():
            A(f"| {seed} | {r.get('cont_z','—')} | {pc(r['cont_margin']) if 'cont_margin' in r else '—'} "
              f"| {r.get('shock_z','—')} | {pc(r['shock_margin']) if 'shock_margin' in r else '—'} |")
        A("")
        A(f"{meta.get('seed_interpretation','')}\n")
        A("---\n")

    # 8. Final
    A("## 8. Final Interpretation\n")
    A(meta.get("final_interpretation", "") + "\n")
    A("---\n")
    A(f"*Engine applied as-is; no logic modified. Seed 42. Market price as of {md}.*")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Generate a standardised case-study report from results + meta JSON.")
    ap.add_argument("results")
    ap.add_argument("meta")
    ap.add_argument("-o", "--out", required=True)
    args = ap.parse_args(argv)
    results = json.load(open(args.results))
    meta = json.load(open(args.meta))
    import os
    meta["__meta_path__"] = os.path.abspath(args.meta)
    md = build(results, meta)
    with open(args.out, "w") as f:
        f.write(md + "\n")
    print(f"wrote {args.out}  ({len(md.splitlines())} lines)")


if __name__ == "__main__":
    raise SystemExit(main())
