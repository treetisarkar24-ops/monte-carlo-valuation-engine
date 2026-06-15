# Monte Carlo Valuation Engine

A discounted-cash-flow (DCF) valuation engine that returns a *distribution* of
intrinsic values rather than a single point estimate. It takes the inputs an
analyst reads off an annual report, projects free cash flow, discounts it at a
CAPM/WACC cost of capital, and then runs the whole thing thousands of times
under perturbed assumptions — with an optional discrete-shock overlay — to show
the full range of values the fundamentals can support and where today's market
price sits inside that range.

The engine is dependency-light (NumPy only for the core), deterministic under a
fixed seed, and has been validated on synthetic stress cases and real large-cap
companies.

---

## Why a distribution, not a point

A single DCF number hides how sensitive the answer is to assumptions. This
engine's thesis is that the actionable comparison is **market price vs. the whole
distribution** — not market price vs. one estimate. For Microsoft and Amazon the
result is striking: the market trades at the ~99th percentile (MSFT) or *above
the entire simulated distribution* (AMZN) of what these conservative fixtures
can produce. The engine quantifies exactly how far into the tail the market sits.

---

## How it works (pipeline)

1. **Deterministic DCF** (`dcf.py`) — project revenue, margins, capex, D&A and
   working capital across an explicit forecast horizon; compute unlevered free
   cash flow; discount at WACC (CAPM cost of equity + after-tax cost of debt);
   add a Gordon-growth terminal value; subtract net debt; divide by shares.
2. **Continuous Monte Carlo** (`mc_engine.py`) — perturb the forward-looking
   inputs and re-run, producing a distribution of per-share values.
3. **Convergence** (`mc_convergence.py`) — measure (don't assume) how many paths
   the answer actually needs via a percentile rule and an elbow rule, yielding a
   per-company sample size `z*` instead of a one-size-fits-all "folk number".
4. **Shock overlay** (`mc_shocks.py`) — add five discrete jump channels
   (revenue, margin, funding, strategic, cash) with severity-weighted damage and
   stress accumulation, yielding a shocked sample size `z**` and a fatter-tailed
   distribution.

The architecture is frozen and validated; the math layer is not modified by the
packaging tools described below.

---

## Repository layout

```
Core engine (frozen)
  dcf.py                 Deterministic DCF + WACC
  mc_engine.py           Continuous Monte Carlo
  mc_convergence.py      z* / z** convergence machinery
  mc_shocks.py           Discrete shock overlay
  mc_defaults.py         Perturbation widths, correlations, shock channels
  mc_config.py           MCConfig (n_simulations, seed, overrides)

Tests / verification
  mc_smoke_test.py             Core MC invariants
  mc_shocks_smoke_test.py      Shock-channel diagnostics
  sanity_check.py              Deterministic DCF checks
  textbook_verification.py     Cross-check against textbook cases

Usability layer (packaging — sits in front of the engine)
  MC_Input_Template.xlsx   Human-friendly input template
  input_template.json      Same fields in the JSON shape the engine loads
  excel_loader.py          Filled template (.xlsx) -> validated engine JSON
  generate_report.py       results JSON -> standardised case-study Markdown

Case studies
  case_study_runner.py     Shared runner helpers
  msft_runner.py / amazon_runner.py   Per-company pipeline drivers
  *_fixture.json           Input fixtures
  *_results.json           Cached deterministic results
  *_Case_Study.md          Written reports
```

---

## Quick start

```bash
pip install -r requirements.txt        # numpy, openpyxl

# 1. Sanity-check the engine
python3 mc_smoke_test.py
python3 mc_shocks_smoke_test.py

# 2. Run a valuation from a filled template
python3 excel_loader.py my_company.xlsx -o my_company.json --run

# 3. (Case-study path) run the staged pipeline + build a report
python3 amazon_runner.py central
python3 amazon_runner.py cont
python3 amazon_runner.py shock_conv
python3 amazon_runner.py shock_prod
python3 generate_report.py amazon_results.json amazon_meta.json -o AMZN_Case_Study.md
```

See `WORKFLOW.md` for the full end-to-end user flow.

---

## Validation highlights

| Company | Central / share | WACC | z* (cont) | z** (shock) | Market | Market position |
|---|---|---|---|---|---|---|
| Microsoft (MSFT) | $263.74 | 9.16% | 2,000–3,000 | 1,000–2,000 | ~$450 | ~99th percentile |
| Amazon (AMZN) | $96.52 | 11.27% | 1,500–3,000 | 1,500–2,000 | ~$246 | above the full distribution |

Plus ten synthetic stress cases (Carvana, Rivian, CloudGrow, MedTechX,
RetailRollup, Project Doom, TitanScale, LeveragedRetail, ThinEquity, and the
Steady Co teaching device) documented in `STRESS_TEST_TRACKER.md`.

---

## Status & scope

The engine is complete and the architecture is frozen. Remaining work is
refinement and packaging (more case studies, dashboard, closure review). One
correctness item is deliberately deferred: the engine-level input-validation
layer ("Step 7"). Until it lands, validate inputs through `excel_loader.py`,
which gates the spreadsheet before anything reaches the engine.

*Not investment advice. All case-study outputs are statements about a fixture's
assumptions, not recommendations.*
