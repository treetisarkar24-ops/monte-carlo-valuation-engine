"""End-to-end sanity check on the deterministic DCF engine.

Constructs a synthetic DCFInputs, walks blocks 1-7 in sequence,
prints every intermediate trajectory, and verifies the engine
produces a sensible per-share number end-to-end.

Also verifies the WACC / TV / EV / per-share numbers we worked
through by hand in the teach-mode beats against the engine's
actual output.

Run from this folder:   python3 sanity_check.py
"""

# --- engine path bootstrap (auto-added during reorg; frozen engine lives in ../engine) ---
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "engine"))
# --- end bootstrap ---

import sys, os
# Resolve dcf.py relative to this script.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dcf import (
    DCFInputs,
    project_revenue,
    project_ebit,
    project_nopat,
    project_da,
    project_capex,
    project_dnwc,
    project_fcf,
    compute_wacc,
    terminal_value,
    discount_fcfs,
    discount_tv,
    discount,
    equity_value,
    equity_value_per_share,
    run_dcf,
)

# ----------------------------------------------------------------
#  Synthetic inputs — values chosen to roughly match the WACC and
#  TV worked-example numbers from the teach-mode beats.
# ----------------------------------------------------------------
inputs = DCFInputs(
    starting_revenue=100.0,
    net_debt=50.0,
    shares_outstanding=10.0,
    forecast_years=5,
    revenue_growth=[0.12, 0.10, 0.08, 0.06, 0.04],
    operating_margin=[0.18, 0.19, 0.20, 0.20, 0.20],
    capex_pct_revenue=[0.05, 0.05, 0.04, 0.04, 0.04],
    da_pct_revenue=[0.04, 0.04, 0.04, 0.04, 0.04],
    nwc_pct_revenue=[0.02, 0.02, 0.02, 0.02, 0.02],
    tax_rate=0.25,
    terminal_growth=0.025,
    risk_free_rate=0.04,
    equity_risk_premium=0.055,
    beta=1.1,
    cost_of_debt=0.06,
    debt_to_total_capital=0.30,
)

print("=" * 64)
print("DCF ENGINE — END-TO-END SANITY CHECK")
print("=" * 64)

# ---- Block 1 ----
revenues = project_revenue(inputs)
print("\nBlock 1 — Revenue trajectory ($M):")
for t, r in enumerate(revenues, 1):
    print(f"  Year {t}:  {r:>8.2f}")

# ---- Block 2 ----
ebits = project_ebit(revenues, inputs)
nopats = project_nopat(ebits, inputs)
print("\nBlock 2 — Operating profit ($M):")
print(f"  {'Year':<6}{'EBIT':>10}{'NOPAT':>10}")
for t in range(inputs.forecast_years):
    print(f"  {t+1:<6}{ebits[t]:>10.2f}{nopats[t]:>10.2f}")

# ---- Block 3 ----
das = project_da(revenues, inputs)
capex = project_capex(revenues, inputs)
dnwcs = project_dnwc(revenues, inputs)
fcfs = project_fcf(nopats, revenues, inputs)
print("\nBlock 3 — Free cash flow ($M):")
print(f"  {'Year':<6}{'NOPAT':>10}{'D&A':>10}{'Capex':>10}{'dNWC':>10}{'FCF':>10}")
for t in range(inputs.forecast_years):
    print(f"  {t+1:<6}{nopats[t]:>10.2f}{das[t]:>10.2f}{capex[t]:>10.2f}{dnwcs[t]:>10.2f}{fcfs[t]:>10.2f}")

# ---- Block 4 ----
wacc = compute_wacc(inputs)
print(f"\nBlock 4 — WACC: {wacc:.4%}")
print(f"  expected ~8.385% from worked example ... ", end="")
print("MATCH" if abs(wacc - 0.08385) < 1e-4 else f"DRIFT ({wacc:.4%})")

# ---- Block 5 ----
tv = terminal_value(fcfs, wacc, inputs)
print(f"\nBlock 5 — Terminal value at year 5: ${tv:,.2f}M")

# ---- Block 6 ----
pv_fcfs = discount_fcfs(fcfs, wacc)
pv_tv = discount_tv(tv, len(fcfs), wacc)
ev = discount(fcfs, tv, wacc)
print("\nBlock 6 — Discounting:")
print(f"  {'Year':<6}{'FCF':>10}{'PV(FCF)':>12}")
for t in range(inputs.forecast_years):
    print(f"  {t+1:<6}{fcfs[t]:>10.2f}{pv_fcfs[t]:>12.2f}")
print(f"  PV of TV (year 5): ${pv_tv:,.2f}M  ({pv_tv/ev:.1%} of EV)")
print(f"  Enterprise value:  ${ev:,.2f}M")

# ---- Block 7 ----
eq_val = equity_value(ev, inputs)
per_share = equity_value_per_share(eq_val, inputs)
print("\nBlock 7 — Equity bridge:")
print(f"  Equity value: ${eq_val:,.2f}M  (EV ${ev:.2f}M − net debt ${inputs.net_debt:.2f}M)")
print(f"  Intrinsic value per share: ${per_share:.2f}")

# ----------------------------------------------------------------
#  Independent verification against the hand-computed worked
#  example: drive blocks 5-7 with the exact FCF series used in
#  the teach-mode beats so we can compare expected numbers
#  directly.
# ----------------------------------------------------------------
print("\n" + "=" * 64)
print("HAND-CHECK against worked-example FCFs [12, 14, 16, 18, 19.80]")
print("=" * 64)
worked_fcfs = [12.0, 14.0, 16.0, 18.0, 19.80]
worked_tv = terminal_value(worked_fcfs, wacc, inputs)
worked_ev = discount(worked_fcfs, worked_tv, wacc)
worked_eq = equity_value(worked_ev, inputs)
worked_ps = equity_value_per_share(worked_eq, inputs)
print(f"  TV_5      : ${worked_tv:,.2f}M   (expected ~$344.86M)")
print(f"  EV        : ${worked_ev:,.2f}M   (expected ~$292.44M)")
print(f"  Equity    : ${worked_eq:,.2f}M   (expected ~$242.44M)")
print(f"  Per share : ${worked_ps:.2f}     (expected ~$24.24)")
print("\nNote: the original chat walked-example numbers used a")
print("PLACEHOLDER WACC = 9% for TV but the real WACC = 8.385% for")
print("discounting — internally inconsistent. The values above are")
print("the consistent, all-WACC=8.385% reconciliation.")

print("\n" + "=" * 64)
print("ORCHESTRATOR CHECK — run_dcf(inputs)")
print("=" * 64)
orchestrator_result = run_dcf(inputs)
print(f"  Manual walk-through result : ${per_share:.2f}")
print(f"  Orchestrator result        : ${orchestrator_result:.2f}")
match = abs(orchestrator_result - per_share) < 1e-6
print(f"  {'MATCH' if match else 'MISMATCH'}")

print("\n" + "=" * 64)
print("All seven blocks + orchestrator executed without error.")
print("=" * 64)
