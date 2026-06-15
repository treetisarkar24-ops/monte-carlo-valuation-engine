"""Textbook verification — Gordon-growth limit test.

A rigorous mathematical test of the engine's internal consistency.

Idea: in the steady-state limit where revenue growth, operating
margin, and asset-intensity are all constant — AND terminal_growth
equals revenue_growth, so the explicit forecast is ALREADY in
steady state from year 1 — the deterministic DCF must collapse
exactly to the Gordon growth formula:

    EV = FCF_1 / (WACC − g)

Why this matters: it tests the COMPOSITION of all seven blocks,
not any one in isolation. If revenue compounding, margin
application, FCF construction, WACC computation, terminal-value
formula, discounting, or summation has any systematic error,
the engine's answer will diverge from the closed-form result.

Two properties to look for:

  1. Engine answer matches the closed-form to within floating-point
     precision (~1e-12), not just "close enough."
  2. Engine answer is INVARIANT to forecast_years — produces the
     same value whether the forecast horizon is 3, 5, 10, or 100
     years. This is the mathematical telescoping: in steady state,
     explicit-forecast PVs + TV PV must always sum to the same
     thing regardless of where you split between them.

If either property fails, we've caught a real bug. If both pass,
the engine is mathematically consistent with first-principles
DCF theory.

Run from this folder:   python3 textbook_verification.py
"""

# --- engine path bootstrap (auto-added during reorg; frozen engine lives in ../engine) ---
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "engine"))
# --- end bootstrap ---

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dcf import DCFInputs, compute_wacc, run_dcf


# ----------------------------------------------------------------
# Steady-state DCFInputs constructor: every dial held constant,
# capex == D&A (no net investment), zero NWC change, terminal_growth
# equals revenue_growth (no transition from explicit forecast to
# terminal world), all-equity firm (so WACC = cost of equity).
# ----------------------------------------------------------------

G = 0.05  # constant growth used throughout (5%)


def make_steady_state_inputs(forecast_years: int) -> DCFInputs:
    return DCFInputs(
        starting_revenue=100.0,
        net_debt=0.0,                                # no debt → equity == EV
        shares_outstanding=10.0,
        forecast_years=forecast_years,
        revenue_growth=[G] * forecast_years,
        operating_margin=[0.20] * forecast_years,
        capex_pct_revenue=[0.04] * forecast_years,   # capex = D&A → no net investment
        da_pct_revenue=[0.04] * forecast_years,
        nwc_pct_revenue=[0.0] * forecast_years,      # no working capital drag
        tax_rate=0.25,
        terminal_growth=G,                           # same as revenue growth
        risk_free_rate=0.04,
        equity_risk_premium=0.06,
        beta=1.0,                                    # forces cost of equity = 10%
        cost_of_debt=0.05,                           # irrelevant (D/V=0)
        debt_to_total_capital=0.0,                   # all-equity → WACC = cost of equity = 10%
    )


# Confirm WACC is exactly 10% in this construction.
test_inputs = make_steady_state_inputs(5)
wacc = compute_wacc(test_inputs)
assert abs(wacc - 0.10) < 1e-12, f"Expected WACC=10%, got {wacc:.6%}"
print(f"WACC = {wacc:.4%}   (expected 10.0000%)   PASS")


# ----------------------------------------------------------------
# Closed-form expected value via the Gordon growth formula.
# ----------------------------------------------------------------
# In steady state with capex = D&A and zero NWC change, FCF = NOPAT.
# NOPAT_1 = Revenue_1 × margin × (1 − tax_rate)
# Revenue_1 = starting_revenue × (1 + g)
revenue_1 = 100.0 * (1 + G)
fcf_1 = revenue_1 * 0.20 * (1 - 0.25)
closed_form_ev = fcf_1 / (wacc - G)
closed_form_ps = closed_form_ev / 10.0

print(f"\nClosed-form Gordon result (the bar the engine must meet):")
print(f"  FCF_1            = ${revenue_1:.2f}M × 0.20 × 0.75 = ${fcf_1:.6f}M")
print(f"  EV               = FCF_1 / (WACC − g) = ${fcf_1:.6f} / {wacc - G:.4f} = ${closed_form_ev:.6f}M")
print(f"  Per share (10sh) = ${closed_form_ps:.6f}")


# ----------------------------------------------------------------
# Engine results across forecast horizons. Should be invariant.
# ----------------------------------------------------------------
print(f"\nEngine results across forecast horizons:")
print(f"  {'forecast_years':>16}   {'per_share':>14}   {'relative gap':>14}   {'verdict':>8}")
print(f"  {'-'*16}   {'-'*14}   {'-'*14}   {'-'*8}")

all_pass = True
TOLERANCE = 1e-10

for N in [3, 5, 7, 10, 25, 50, 100]:
    inputs_N = make_steady_state_inputs(N)
    engine_ps = run_dcf(inputs_N)
    relative_gap = abs(engine_ps - closed_form_ps) / closed_form_ps
    passed = relative_gap < TOLERANCE
    all_pass = all_pass and passed
    verdict = "PASS" if passed else "FAIL"
    print(f"  {N:>16}   ${engine_ps:>13.6f}   {relative_gap:>14.2e}   {verdict:>8}")

print()
print("=" * 64)
if all_pass:
    print(f"ALL CHECKS PASS — engine matches Gordon closed-form to <{TOLERANCE:.0e}")
    print("relative tolerance, AND is invariant to forecast_years.")
    print("Deterministic DCF engine is mathematically verified.")
else:
    print("ONE OR MORE CHECKS FAILED — investigate before proceeding.")
print("=" * 64)
