# Dashboard Plan (planning only — not built)

Goal: let a visitor run their own case against the **real** engine, for free,
linked from a portfolio page. This is a plan, not an implementation.

---

## Recommended approach: Streamlit on Streamlit Community Cloud

| Criterion | Why Streamlit fits |
|---|---|
| Runs the real engine | Executes the actual Python (`dcf.py`, `mc_engine.py`, …) unchanged — no re-implementation, architecture stays frozen |
| Free | Streamlit Community Cloud deploys free from a public GitHub repo |
| Visitor runs own inputs | Native form widgets map directly to the 16 DCFInputs |
| Low maintenance | Single `app.py`; no server to manage |

Alternatives considered and why not (for now): a hosted API + custom JS
front-end (more moving parts, hosting cost); Pyodide/WASM in-browser (no server,
but a few-thousand-path MC is slow in-browser and the build is heavier);
pre-computed case-study explorer (cannot run arbitrary user input).

---

## Prerequisite (hard gate)

Public input means strangers type values. **The `excel_loader.py` validation
must be reused as the input gate** before anything reaches the engine — or, when
Step 7 lands, the engine-level validation. No public deployment should run
unguarded inputs.

---

## Proposed architecture

```
app.py (Streamlit)
  ├─ Sidebar form
  │    Block A: 11 number inputs (with help text + sensible defaults)
  │    Block B: an editable table, forecast_years rows × 5 trajectory columns
  ├─ Validate  → reuse excel_loader.build_inputs() (shared validation)
  ├─ Run       → run_dcf, compute_wacc, run_monte_carlo, (optional) shocks
  ├─ Convergence (optional, capped) → convergence_with_recommendation
  └─ Display
       • Central value + WACC card
       • Distribution histogram (matplotlib/altair)
       • Percentile table + "where does market price land" gauge
       • Download buttons: inputs JSON, results JSON
```

Reusing `excel_loader.build_inputs()` keeps one validation code path for both the
spreadsheet and the web form.

---

## Public-run guardrails

- **Cap path count.** Public runs limited to the validated range (z* studies use
  1,500–3,000; cap at e.g. 5,000) so a free instance stays responsive.
- **Cap forecast_years** (e.g. ≤ 10) to bound compute.
- **Cold starts.** Free instances sleep after inactivity (~30s wake) — note this
  on the page so visitors don't think it's broken.
- **Disclaimer.** Output is a statement about the user's assumptions, not advice.
- **Public code.** Deploying from a public repo means the engine is readable —
  for a portfolio that is the point, but it is a deliberate choice.

---

## Build checklist (when greenlit)

1. Public GitHub repo with `requirements.txt` (+ `streamlit`).
2. `app.py` wiring the form to the engine via the shared validator.
3. Histogram + percentile/market-gauge components.
4. Path/horizon caps and the disclaimer.
5. Deploy on Streamlit Community Cloud; link from the portfolio.
6. Smoke-test the MSFT and AMZN fixtures through the web form; confirm they
   reproduce the documented central values ($263.74 / $96.52).

Estimated scope: roughly a day of work once Step 7 (or the loader gate) is the
agreed validation path.
