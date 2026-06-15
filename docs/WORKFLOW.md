# User Workflow — from inputs to a finished valuation

This document describes the end-to-end path a user takes to value a company with
the engine. There are two entry points: a **spreadsheet path** (no code, fill a
template) and a **case-study path** (staged runner + report generator).

---

## Stage 0 — gather the inputs

The engine needs 16 inputs: 11 single values and 5 year-by-year trajectories.
All come from a company's most recent annual report plus a handful of market
figures (risk-free rate, equity risk premium, beta). The judgment work — reading
the report and deciding the growth/margin/capex fades — happens here, by the
analyst. The engine consumes only the distilled numbers; it ingests no prose.

Conventions:
- Rates and percentages are **decimals** (12% = 0.12).
- Currency figures are in **consistent units** (e.g. all $millions). The output
  per-share value comes out in that same currency.
- Each trajectory has exactly `forecast_years` entries.
- `terminal_growth` must be **less than** the resulting WACC.

---

## Path A — spreadsheet (no code)

```
MC_Input_Template.xlsx   →   excel_loader.py   →   engine   →   result
   (user fills)              (parse+validate)      (run)        (JSON / quick stats)
```

1. Open `MC_Input_Template.xlsx`. Read the "Read me first" tab.
2. Fill the yellow cells on the "Inputs" tab — Block A (company-level values)
   and Block B (one row per forecast year). The MSFT example column shows
   sensible ranges.
3. Run the loader:
   ```bash
   python3 excel_loader.py filled.xlsx -o my_company.json --run
   ```
   - It validates the sheet (missing values, wrong row count, out-of-range rates,
     percent-vs-decimal slips, `terminal_growth ≥ WACC`) and reports **all**
     problems at once.
   - With `--run` it prints WACC, the deterministic per-share value, and a quick
     Monte Carlo summary.
4. `my_company.json` is now in the exact shape the engine and the case-study
   runner accept.

This path is intended for a future hosted dashboard front-end (see
`DASHBOARD_PLAN.md`), which would replace step 1–2 with a web form.

---

## Path B — full case study (staged runner)

Used to produce a portfolio-grade write-up like `MSFT_Microsoft_Case_Study.md`
or `Candidate_AMZN_Amazon.md`.

1. **Create the fixture** — `<slug>_fixture.json` (or export it from the loader).
2. **Run the staged pipeline.** Each stage caches into `<slug>_results.json`, so
   stages can run independently and fit short timeouts:
   ```bash
   python3 <slug>_runner.py central       # deterministic value + WACC
   python3 <slug>_runner.py cont          # continuous z* + production run + folk benchmark
   python3 <slug>_runner.py shock_conv    # shocked z** convergence
   python3 <slug>_runner.py shock_prod    # shocked production + channel diagnostics
   python3 <slug>_runner.py seed42        # record seed-42 robustness row
   python3 <slug>_runner.py seedc99 ...   # extra seeds for robustness
   ```
   (A new company reuses `msft_runner.py` / `amazon_runner.py` as a template —
   change the slug and fixture filename.)
3. **Write the meta file** — `<slug>_meta.json`: company name, ticker, market
   price/date, the assumptions table with rationale, and the interpretation prose
   for the market and final sections.
4. **Generate the report:**
   ```bash
   python3 generate_report.py <slug>_results.json <slug>_meta.json -o <TICKER>_Case_Study.md
   ```
   The generator formats every quantitative section from the results and splices
   in the meta prose, producing the standardised 8-section report.

---

## Outputs produced

| Artifact | Produced by | Contents |
|---|---|---|
| `<slug>.json` | `excel_loader.py` | Validated DCFInputs in engine JSON shape |
| `<slug>_results.json` | runner stages | Central value, z*/z**, production stats, channel fires, seeds |
| `<TICKER>_Case_Study.md` | `generate_report.py` | Standardised 8-section written report |

---

## What is NOT yet automated

- **Engine-level input validation (Step 7).** Validation currently lives in
  `excel_loader.py` (the spreadsheet gate). A user who builds a fixture by hand
  and bypasses the loader gets no guardrail.
- **A single one-shot command.** The pipeline is intentionally staged so each
  step fits a short compute budget; a `run_all` wrapper is a possible convenience
  but is not built.
- **A web/GUI front-end.** Planned, not built — see `DASHBOARD_PLAN.md`.
