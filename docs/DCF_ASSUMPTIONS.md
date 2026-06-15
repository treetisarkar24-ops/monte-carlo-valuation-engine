# DCF Assumptions

The valuation rests on two layers: the **inputs you supply per company** and the
**structural choices baked into the engine** (`dcf.py`, frozen). Everything below
documents the existing model — no logic is changed here.

---

## 1. Per-run inputs (the dials you set each time)

These are the fields of `DCFInputs`.

**Anchor facts**
- `starting_revenue` — most recent actual revenue, in dollars
- `net_debt` — total debt minus cash (can be negative for net-cash companies)
- `shares_outstanding`

**Horizon**
- `forecast_years` — explicit forecast length, default **7**

**Trajectories** (one value per forecast year, all as decimals)
- `revenue_growth[]`
- `operating_margin[]`
- `capex_pct_revenue[]`
- `da_pct_revenue[]` — depreciation & amortization
- `nwc_pct_revenue[]` — change in net working capital

**Tax & terminal**
- `tax_rate` — flat across the horizon
- `terminal_growth` — perpetuity growth rate `g`

**Discounting block**
- `risk_free_rate`
- `equity_risk_premium`
- `beta` (deliberately allowed to be negative)
- `cost_of_debt`
- `weight_debt` — debt's share of the capital structure

---

## 2. Structural assumptions (baked into the engine)

1. **Cost of equity via CAPM** — `risk_free + beta × ERP`.

2. **WACC as a static blend with a debt tax shield** —
   `(E/V)·CoE + (D/V)·CoD·(1 − tax)`.
   One capital structure, held constant across all forecast years (no re-levering).

3. **Cash flow is FCFF** —
   `FCFF = NOPAT + D&A − Capex − ΔNWC`, where
   `NOPAT = EBIT·(1 − tax)` and `EBIT = revenue × operating_margin`.
   Margin applies to revenue directly; the tax rate is flat.

4. **Terminal value via Gordon growth** —
   `TV_N = FCF_{N+1} / (WACC − g)`, which structurally requires **WACC > g**.
   In practice this term carries **60–80% of enterprise value** — the perpetuity
   dominates the answer.

5. **Everything below EBIT scales as a % of revenue.** This is the engine's
   documented fragility:
   - `capex_pct_revenue` — **most fragile**; breaks for heavy growth-investment,
     wind-downs, and asset-light businesses.
   - `da_pct_revenue` — breaks for capital-heavy or early-stage companies.
   - `nwc_pct_revenue` — **most defensible** of the three.

6. **Bridge to equity** —
   `EV = Σ PV(FCFs) + PV(TV)`;
   `equity = EV − net_debt`;
   `per_share = equity / shares_outstanding`.

---

## 3. Where the model is most sensitive

Two places concentrate the leverage:

- **Terminal value** — because it's most of EV, small changes to `terminal_growth`
  or the terminal WACC move the valuation most.
- **Capex** — the most fragile of the % -of-revenue scalers.

These are the assumptions to stress-test first.
