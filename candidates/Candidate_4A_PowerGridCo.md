# Candidate #4A — PowerGridCo

**Classification:** Boundary-Cross Attempt — Failed Pre-Run Check
**Status:** Closed. Full pipeline was NOT run.
**Date:** 2026-06-01. Engine state: steps 2–6 complete and locked.

---

## 0. Framing

PowerGridCo is a **fixture for architecture exploration, not an investment recommendation.** These inputs are synthetic.

**Purpose of this candidate.** Candidate #4A was designed to be the second positive-centre fragile company — following CloudGrow (Candidate #3, central +$5.58) — to test whether the following architecture questions could be answered on a second positive-centre fixture:

- Does F8 (thin shocked margin, large rec_batches on a positive-centre fragile company) reproduce?
- Does z\*\* separate from z\* at higher volatility?
- Does cash-channel dominance return for a high-revenue/thin-equity positive-centre company?
- Is the revenue/equity-ratio mechanism the correct predictor of worst-path channel ordering?

The pre-run check failed. The candidate never entered the regime being studied.

---

## 1. Inputs

| Field | Value |
|---|---|
| starting_revenue | 12,000 |
| net_debt | 7,000 |
| shares_outstanding | 350 |
| forecast_years | 5 |
| revenue_growth | 10%, 8%, 7%, 5%, 4% |
| operating_margin | 8%, 9%, 10%, 11%, 12% |
| capex_pct_revenue | 12%, 11%, 10%, 9%, 8% |
| da_pct_revenue | 5% flat |
| nwc_pct_revenue | 3% flat |
| tax_rate | 25% |
| terminal_growth | 2.5% |
| risk_free_rate | 4% |
| equity_risk_premium | 5.5% |
| beta | 1.8 |
| cost_of_debt | 8% |
| debt_to_total_capital | 45% |

**Derived WACC:** 10.345%

---

## 2. Pre-Run Check Result

| | |
|---|---|
| Deterministic central value | **−$9.62 / share** |
| WACC | **10.345%** |
| Positive-centre gate | **FAILED** |
| Full pipeline run | **NO** |

The fixture does not satisfy the positive-centre requirement. Per the pre-run protocol, the investigation stops here.

---

## 3. Failure Analysis

Four forces compound to produce a negative centre. None is individually disqualifying; together they are sufficient.

**Force 1 — Capex persistently exceeds D&A (7pp gap in year 1, narrowing to 3pp by year 5).**

FCF = NOPAT + D&A − Capex − ΔNWC. When capex% exceeds D&A% by 7pp, a large fraction of NOPAT is absorbed by net investment. Year 1 FCF is approximately −$168M despite an 8% operating margin:

| Year | Revenue ($M) | NOPAT ($M) | D&A ($M) | Capex ($M) | ΔNWC ($M) | FCF ($M) |
|------|-------------|-----------|---------|-----------|----------|---------|
| 1 | 13,200 | 792 | 660 | 1,584 | 36 | −168 |
| 2 | 14,256 | 962 | 713 | 1,568 | 31 | 76 |
| 3 | 15,254 | 1,144 | 763 | 1,525 | 30 | 352 |
| 4 | 16,017 | 1,321 | 801 | 1,441 | 23 | 658 |
| 5 | 16,658 | 1,495 | 833 | 1,333 | 19 | 976 |

Year 1 is negative; years 2–5 are positive but modest. The explicit period is a net drag.

**Force 2 — Thin operating margins (8%–12%) limit NOPAT.**

NOPAT grows from $792M to $1,495M across the five years — meaningful in absolute terms, but insufficient to overcome the large net capex bite at a 10.345% discount rate.

**Force 3 — $7,000M net debt on 350M shares = $20/share equity burden.**

Enterprise value must exceed $7bn for equity to be worth anything. At the derived enterprise value (positive but modest), subtracting $7bn of net debt and dividing by 350M shares produces a deeply negative per-share figure.

**Force 4 — WACC 10.345% compresses all present values.**

Beta 1.8 × ERP 5.5% = 9.9% equity premium. Equity cost = 13.9%. WACC = 0.55 × 13.9% + 0.45 × 8% × 0.75 = 10.345%. At this rate, $1 of terminal value five years out is worth $0.61 today. The TV multiplier is 1/(10.345% − 2.5%) ≈ 12.75×, which produces a terminal value in the $8bn range after discounting — not enough to cover $7bn net debt with margin to spare.

**Interaction.** The four forces are mutually reinforcing. Lower WACC alone might rescue the equity. Lighter net debt alone might rescue it. Wider margins alone might. What the fixture demonstrates is that combining all four simultaneously creates a regime where the equity is structurally underwater at the central case, regardless of the nominal "fragile positive" intent.

---

## 4. Architecture Relevance

This candidate produces **no evidence** regarding:

- B1 (sign-fragile precision rule)
- B2 (borderline mis-fire)
- F3 (z\*\* direction relative to z\*)
- F8 (thin shocked margin on positive-centre fragile company)
- z\*, z\*\*, decision margins, convergence behaviour
- Channel mix under shocks
- Seed robustness

None of these are tested. The candidate never crossed the positive-centre gate and therefore never entered the regime under study. No findings are promoted to any tier.

**What this failure does contribute:**

A positive-centre fragile company is more difficult to construct than initially expected when capital intensity, leverage, and discount rate pressure are combined. The combination of capex > D&A, thin margins, high net debt, and a meaningful beta is sufficient to suppress a positive valuation centre even when each individual parameter looks "only moderately stressed." This is a boundary-construction observation, not an architecture finding.

---

## 5. Comparison vs Prior Candidates

| | Steady Co | Carvana | Rivian | CloudGrow | **PowerGridCo 4A** |
|---|---|---|---|---|---|
| Central value | +$12.77 | −$5.61 | −$2.35 | +$5.58 | **−$9.62** |
| WACC | 8.16% | 10.75% | 12.56% | 12.535% | **10.345%** |
| Net debt/share | $3.00 | $22.73 | $0.83 | $1.00 | **$20.00** |
| Starting revenue ($M) | 1,000 | 20,300 | 5,500 | 3,000 | **12,000** |
| Pipeline run | Full | Full | Full | Full | **None — failed gate** |

PowerGridCo has the second-largest net-debt/share burden of any fixture (after Carvana), the second-largest starting revenue, and a WACC that sits between Steady Co and the high-WACC fragile candidates. The combination of Carvana-scale net debt and Rivian-scale discount rate, applied to a moderate-revenue business with persistent capex overhang, is what kills the centre.

---

## 6. No Findings

| Tier | Finding | Status |
|------|---------|--------|
| Candidate-specific | Positive-centre construction harder than expected under combined capital-intensity + leverage + rate pressure | **Noted, not promoted** |
| Fragile-company | — | — |
| Architecture | — | — |

Nothing is promoted. The candidate is a data point about fixture design, not about engine behaviour.

---

## 7. Open Question for Next Candidate

The next positive-centre fragile fixture should relax at least one of the four compounding forces while preserving high beta and genuine fragility. The question for design: which force to relax while keeping the company legitimately fragile?

Candidate options:
- Lower capex% relative to D&A% (improve FCF conversion, preserve revenue/equity ratio for cash-channel test)
- Lower net debt (preserve revenue scale and margins, reduce the equity burden)
- Higher margins (preserve capital structure and leverage, improve NOPAT enough to cover capex)

The fixture does not need to be rebuilt here. This document records what the constraints are.

---

*End of Candidate #4A log. Candidate #4B or a renamed fixture will be the next attempt at a positive-centre fragile company.*
