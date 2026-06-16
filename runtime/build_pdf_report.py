#!/usr/bin/env python3
"""
build_pdf_report.py — render a case-study valuation as a polished PDF.

Primary deliverable in the three-tier output set (PDF report / Excel workbook /
Markdown diagnostics). Reads the SAME results.json + meta.json the Markdown
generator uses, plus the fixture for the year-by-year tables. Presentation layer
only — it imports the engine read-only (to project the FCFF trajectory) and
modifies no DCF / MC / shock / convergence logic.

Usage:
    python3 build_pdf_report.py amazon_results.json amazon_meta.json -o Amazon_Valuation_Report.pdf
"""
from __future__ import annotations

# --- engine path bootstrap (auto-added during reorg; frozen engine lives in ../engine) ---
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "engine"))
# --- end bootstrap ---

import argparse
import json
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable,
)

NAVY = colors.HexColor("#1F3A5F")
STEEL = colors.HexColor("#2E5E8C")
LIGHT = colors.HexColor("#EAF0F6")
GREY = colors.HexColor("#666666")


def f0(x):
    return f"${x:,.0f}"


def f2(x):
    return f"${x:,.2f}"


def pc(x, dp=1):
    return f"{x:.{dp}f}%"


def styles():
    ss = getSampleStyleSheet()
    ss.add(ParagraphStyle("Cover", parent=ss["Title"], fontSize=26, textColor=NAVY,
                          spaceAfter=6, alignment=TA_CENTER))
    ss.add(ParagraphStyle("CoverSub", parent=ss["Normal"], fontSize=13, textColor=STEEL,
                          alignment=TA_CENTER, spaceAfter=2))
    ss.add(ParagraphStyle("CoverMeta", parent=ss["Normal"], fontSize=10, textColor=GREY,
                          alignment=TA_CENTER))
    ss.add(ParagraphStyle("H2", parent=ss["Heading2"], fontSize=14, textColor=NAVY,
                          spaceBefore=14, spaceAfter=6))
    ss.add(ParagraphStyle("Body", parent=ss["Normal"], fontSize=9.5, leading=14,
                          spaceAfter=6, alignment=TA_LEFT))
    ss.add(ParagraphStyle("Caption", parent=ss["Normal"], fontSize=8, textColor=GREY,
                          spaceAfter=10))
    ss.add(ParagraphStyle("Headline", parent=ss["Normal"], fontSize=11, textColor=NAVY,
                          alignment=TA_CENTER, spaceBefore=10, spaceAfter=2))
    ss.add(ParagraphStyle("HeadlineBig", parent=ss["Normal"], fontSize=30, textColor=NAVY,
                          alignment=TA_CENTER, spaceAfter=2))
    return ss


def year_tables(meta):
    fixture = meta.get("fixture")
    if not fixture:
        return None, None, None
    try:
        from dcf import (DCFInputs, project_revenue, project_ebit, project_nopat,
                         project_da, project_capex, project_dnwc, project_fcf)
        path = fixture
        if not os.path.exists(path) and meta.get("__meta_path__"):
            path = os.path.join(os.path.dirname(meta["__meta_path__"]), fixture)
        inp = DCFInputs(**json.load(open(path)))
    except Exception:
        return None, None, None
    base = meta.get("base_year")
    fy = inp.forecast_years
    rev = project_revenue(inp); ebit = project_ebit(rev, inp); nopat = project_nopat(ebit, inp)
    da = project_da(rev, inp); capex = project_capex(rev, inp); dnwc = project_dnwc(rev, inp)
    fcf = project_fcf(nopat, rev, inp)

    def yr(i):
        return f"FY{base + 1 + i}" if base else f"Year {i + 1}"

    window = (f"Forecast window: base year FY{base} (reported actuals); explicit forecast "
              f"FY{base+1}–FY{base+fy} ({fy} years); terminal value from FY{base+fy+1} onward."
              if base else
              f"Forecast window: year 0 = today (actuals); explicit forecast years 1–{fy}; "
              f"terminal value thereafter.")
    assum = [["Year", "Rev growth", "Op margin", "Capex %", "D&A %", "ΔNWC %"]]
    for i in range(fy):
        assum.append([yr(i), f"{inp.revenue_growth[i]*100:.0f}%", f"{inp.operating_margin[i]*100:.1f}%",
                      f"{inp.capex_pct_revenue[i]*100:.1f}%", f"{inp.da_pct_revenue[i]*100:.1f}%",
                      f"{inp.nwc_pct_revenue[i]*100:.1f}%"])
    base_label = f"FY{base}" if base else "Year 0"
    fcft = [["Year", "Revenue", "EBIT", "NOPAT", "+D&A", "−Capex", "FCFF"]]
    fcft.append([base_label, f0(inp.starting_revenue), "—", "—", "—", "—", "—"])
    for i in range(fy):
        fcft.append([yr(i), f0(rev[i]), f0(ebit[i]), f0(nopat[i]), f0(da[i]),
                     f"({f0(capex[i])})", f0(fcf[i])])
    return window, assum, fcft


def grid_table(data, ss, header_bg=NAVY, col_widths=None, money_right=True):
    t = Table(data, colWidths=col_widths, repeatRows=1, hAlign="LEFT")
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C9D4E0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]
    if money_right:
        style.append(("ALIGN", (1, 1), (-1, -1), "RIGHT"))
    t.setStyle(TableStyle(style))
    return t


def kv_table(rows, ss, col_widths=(3.0 * inch, 2.0 * inch)):
    t = Table(rows, colWidths=col_widths, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (1, 0), (1, -1), NAVY),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C9D4E0")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def P(text, ss, sty="Body"):
    return Paragraph(text, ss[sty])


def build(results, meta, out_path):
    ss = styles()
    co, tk = meta["company"], meta["ticker"]
    central = results["central"]
    cont = results["cont"]
    shock = results.get("shock", {})
    mp = meta["market_price"]
    md = meta.get("market_date", "")
    story = []

    # ---------- Cover ----------
    story += [Spacer(1, 1.4 * inch),
              P(f"{co}", ss, "Cover"),
              P(f"({tk}) &nbsp;&middot;&nbsp; Monte Carlo DCF Valuation Report", ss, "CoverSub"),
              Spacer(1, 0.5 * inch),
              P("Central intrinsic value per share", ss, "Headline"),
              P(f"{f2(central['value'])}", ss, "HeadlineBig"),
              Spacer(1, 0.15 * inch),
              P(f"WACC {pc(central['wacc']*100,2)} &nbsp;|&nbsp; Market {f2(mp)}"
                + (f" (as of {md})" if md else ""), ss, "Headline"),
              Spacer(1, 1.6 * inch),
              P("Generated by the Monte Carlo Valuation Engine. Engine applied as-is; "
                "no DCF / Monte Carlo / shock / convergence logic was modified. Figures are a "
                "statement about the input assumptions, not investment advice.", ss, "Caption"),
              PageBreak()]

    # ---------- 1. Assumptions ----------
    story += [P("1.&nbsp; Assumptions", ss, "H2")]
    arows = [["Input", "Value", "Rationale"]]
    for inp, val, why in meta["assumptions"]:
        arows.append([inp, str(val), Paragraph(why, ss["Body"])])
    story += [grid_table(arows, ss, col_widths=[1.5*inch, 1.0*inch, 4.0*inch], money_right=False),
              Spacer(1, 4),
              P(meta.get("assumptions_caveat", ""), ss, "Caption")]

    # ---------- 2. Deterministic ----------
    story += [P("2.&nbsp; Deterministic Central Case", ss, "H2")]
    window, assum, fcft = year_tables(meta)
    if window:
        story += [P(window, ss, "Body")]
    story += [kv_table([
        ["WACC", pc(central["wacc"]*100, 3)],
        ["Terminal spread (WACC − g)", pc((central["wacc"]-meta["terminal_growth"])*100, 2)],
        ["Central DCF per share", f2(central["value"])],
    ], ss)]
    if assum:
        story += [Spacer(1, 8), P("Year-by-year assumptions", ss, "Body"),
                  grid_table(assum, ss)]
    if fcft:
        story += [Spacer(1, 8), P("Free-cash-flow (FCFF) trajectory — USD millions", ss, "Body"),
                  grid_table(fcft, ss)]

    # ---------- 3. Continuous ----------
    p = cont["pair"]; prod = cont["production"]
    story += [PageBreak(), P("3.&nbsp; Continuous Monte Carlo (z*)", ss, "H2")]
    story += [P(f"Convergence resolved at <b>z* = {p['z_star']:,}</b> paths "
                f"(decision margin {pc(p['decision_margin_pct'])}; z_pct {p['z_pct']:,}, "
                f"z_elbow {p['z_elbow']:,}).", ss, "Body")]
    pr = {int(k): v for k, v in prod["pct"].items()}
    order = [5, 10, 25, 50, 75, 90, 95]
    story += [kv_table([
        ["Mean", f2(prod["mean"])], ["Median", f2(prod["median"])],
        ["Std deviation", f2(prod["std"])],
        ["Min / Max", f"{f2(prod['min'])} / {f2(prod['max'])}"],
        ["Fraction negative", pc(cont["frac_negative_pct"])],
    ], ss)]
    prow = [["Percentile"] + [f"P{k}" for k in order if k in pr],
            ["Value"] + [f2(pr[k]) for k in order if k in pr]]
    story += [Spacer(1, 8), grid_table(prow, ss, money_right=True)]
    if "benchmark" in cont:
        b = cont["benchmark"]
        if "z_mean" in b and "folk_mean" in b:
            _stat, _zc, _fc = "mean", b["z_mean"], b["folk_mean"]
        else:
            _stat, _zc, _fc = "median", b["z_median"], b["folk_median"]
        story += [Spacer(1, 6),
                  P(f"Benchmark vs. the 10,000-path folk number: z* uses <b>{b['compute_ratio']}×</b> "
                    f"the compute yet the {_stat} differs by only <b>{pc(b['mean_gap_pct'])}</b> "
                    f"({f2(_zc)} vs {f2(_fc)}).", ss, "Body")]

    # ---------- 4. Shocked ----------
    if shock:
        sp = shock["pair"]; spr = shock["production"]
        story += [P("4.&nbsp; Shocked Monte Carlo (z**)", ss, "H2")]
        story += [P(f"Re-converged under the discrete shock overlay at <b>z** = {sp['z_star']:,}</b> "
                    f"(decision margin {pc(sp['decision_margin_pct'])}).", ss, "Body")]
        spp = {int(k): v for k, v in spr["pct"].items()}
        story += [kv_table([
            ["Mean", f2(spr["mean"])], ["Median", f2(spr["median"])],
            ["Std deviation", f2(spr["std"])],
            ["Min / Max", f"{f2(spr['min'])} / {f2(spr['max'])}"],
            ["Fraction negative", pc(shock["frac_negative_pct"])],
        ], ss)]
        prow2 = [["Percentile"] + [f"P{k}" for k in order if k in spp],
                 ["Value"] + [f2(spp[k]) for k in order if k in spp]]
        story += [Spacer(1, 8), grid_table(prow2, ss, money_right=True)]
        if meta.get("shock_interpretation"):
            story += [Spacer(1, 6), P(meta["shock_interpretation"], ss, "Body")]

        # 5. Channels
        if shock.get("fires_all"):
            story += [P("5.&nbsp; Shock Channel Behaviour", ss, "H2")]
            chans = list(shock["fires_all"].keys())
            crows = [["Channel"] + [c.capitalize() for c in chans],
                     ["Fires — all paths"] + [str(shock["fires_all"][c]) for c in chans],
                     ["Fires — worst 5%"] + [str(shock["fires_worst5"][c]) for c in chans]]
            story += [grid_table(crows, ss, money_right=True),
                      Spacer(1, 6),
                      P(f"Shock-free paths: <b>{pc(shock['shock_free_pct'])}</b>. "
                        f"{meta.get('channel_interpretation','')}", ss, "Body")]

    # ---------- 6. Market ----------
    story += [PageBreak(), P("6.&nbsp; Market Comparison", ss, "H2")]

    def position(price, dist):
        pp = {int(k): v for k, v in dist["pct"].items()}
        if price >= dist["max"]:
            return f"above the maximum simulated value ({f2(dist['max'])})"
        if price <= dist["min"]:
            return f"below the minimum simulated value ({f2(dist['min'])})"
        below = [k for k in sorted(pp) if pp[k] <= price]
        above = [k for k in sorted(pp) if pp[k] >= price]
        return f"between the {below[-1] if below else 0}th and {above[0] if above else 100}th percentile"

    story += [P(f"{co} traded at <b>{f2(mp)}</b>{(' on ' + md) if md else ''}. "
                f"Against the continuous distribution the market price sits {position(mp, prod)}."
                + (f" Against the shocked distribution it sits {position(mp, shock['production'])}."
                   if shock else ""), ss, "Body"),
              Spacer(1, 4),
              P(meta.get("market_interpretation", ""), ss, "Body")]

    # ---------- 7. Seeds ----------
    if results.get("seeds"):
        story += [P("7.&nbsp; Seed Robustness", ss, "H2")]
        srows = [["Seed", "z* (cont)", "cont margin", "z** (shock)", "shock margin"]]
        for seed, r in results["seeds"].items():
            srows.append([str(seed), str(r.get("cont_z", "—")),
                          pc(r["cont_margin"]) if "cont_margin" in r else "—",
                          str(r.get("shock_z", "—")),
                          pc(r["shock_margin"]) if "shock_margin" in r else "—"])
        story += [grid_table(srows, ss, money_right=True), Spacer(1, 4),
                  P(meta.get("seed_interpretation", ""), ss, "Body")]

    # ---------- 8. Conclusion ----------
    story += [P("8.&nbsp; Conclusion", ss, "H2"),
              P(meta.get("final_interpretation", ""), ss, "Body"),
              Spacer(1, 10), HRFlowable(width="100%", color=colors.HexColor("#C9D4E0")),
              P("Engine applied as-is; no logic modified. Seed 42. "
                f"Market price as of {md}. This document reports model output under stated "
                "assumptions and is not investment advice.", ss, "Caption")]

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(GREY)
        canvas.drawString(0.9 * inch, 0.6 * inch, f"{co} ({tk}) — Monte Carlo DCF Valuation Report")
        canvas.drawRightString(7.6 * inch, 0.6 * inch, f"Page {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(out_path, pagesize=letter,
                            topMargin=0.8 * inch, bottomMargin=0.9 * inch,
                            leftMargin=0.9 * inch, rightMargin=0.9 * inch,
                            title=f"{co} ({tk}) Valuation Report")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return out_path


def main(argv=None):
    ap = argparse.ArgumentParser(description="Render a case-study valuation report to PDF.")
    ap.add_argument("results")
    ap.add_argument("meta")
    ap.add_argument("-o", "--out", required=True)
    args = ap.parse_args(argv)
    results = json.load(open(args.results))
    meta = json.load(open(args.meta))
    meta["__meta_path__"] = os.path.abspath(args.meta)
    build(results, meta, args.out)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    raise SystemExit(main())
