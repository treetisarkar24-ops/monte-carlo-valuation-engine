# STRESS-TEST TRACKER — cross-candidate findings register

**What this is.** A handoff doc for *outputs*, not code. Each candidate is run in its
own chat through the SAME staged pipeline (`case_study_runner.py`), produces an
identically-structured `Candidate_N_<Name>.md` research log, and then lands ONE row
here plus any architecture-level finding folded into the ledger below.

**What this is NOT.** Not an investment thesis, not a ranking of companies. Every
company is a **fixture for architecture exploration**. Outputs are case-study
observations. **No single candidate's output is an architecture truth** — a finding
only earns the "architecture" tier once it reproduces across multiple fixtures.

---

## How to run a new candidate (do this in its own chat)

1. Add the company's inputs to the `CANDIDATES` dict in `case_study_runner.py`
   (or drop a `<slug>_fixture.json`). Pick a short slug, e.g. `candidate2`.
2. Run the stages (each convergence sweep is ~30–45s, so they are one-per-shell-call):

   ```
   python3 case_study_runner.py central   <slug>
   python3 case_study_runner.py cont      <slug>
   python3 case_study_runner.py shock     <slug>
   python3 case_study_runner.py seed42    <slug>
   python3 case_study_runner.py seedc:99  <slug>
   python3 case_study_runner.py seedk:99  <slug>
   python3 case_study_runner.py seedc:123 <slug>
   python3 case_study_runner.py seedk:123 <slug>
   python3 case_study_runner.py seedc:7   <slug>
   python3 case_study_runner.py seedk:7   <slug>
   python3 case_study_runner.py dump      <slug>
   ```

   Results accrue in `<slug>_results.json`.
3. Write `Candidate_N_<Name>.md` from that JSON, using `Candidate_1_Carvana.md` as the
   template (same section order).
4. Add a row to the **Candidate register** below, and fold any architecture-level
   observation into the **Findings ledger** and any defect into **Open bugs**.

---

## What to record (the standard, so every log is comparable)

For every candidate the research log and register row capture:

- **Inputs & assumptions** — full DCFInputs, WACC, what makes this fixture distinctive.
- **Deterministic central** — point value/share, vs Steady Co (+$12.77) as the calm anchor.
- **Continuous MC** — z\*, mean/median, std, P5–P95, % negative, histogram shape.
- **Shocked MC** — z\*\*, mean/median, min (floor), % negative, shock-free %.
- **Convergence diagnostics** — z\*, z\*\*, decision margins, precision bar, z_pct vs z_elbow, borderline flag.
- **Benchmark vs folk 10k** — compute ratio, mean gap %.
- **Channel behavior** — fires by channel (all paths) and among worst 5%.
- **Seed robustness** — z\* / z\*\* / margin across seeds {42, 7, 99, 123}.
- **Market-percentile grid** — % of distribution below a set of price points.
- **Three finding tiers** — (1) candidate-specific, (2) fragile-company-class, (3) architecture-level.
- **Surprises & open questions.**

---

## Candidate register

| # | Slug | Company | Central $/sh | WACC | z\* | z\*\* | % neg (cont / shock) | Shock floor | Worst-5% driver | Headline observation |
|---|------|---------|-------------:|-----:|----:|-----:|----------------------|------------:|-----------------|----------------------|
| — | steady_co | Steady Co (control) | +12.77 | 8.16% | — | — | — | — | — | Calm anchor fixture; ~75% shock-free target |
| 1 | candidate1 | Carvana (fragile) | −5.61 | 10.75% | 2000 | 1500 | 65.3% / 71.3% | −89.78 | margin 43% / cash 37% | Negative central → precision rule goes sign-fragile (bug #1) |
| 2 | candidate2 | Rivian (fragile, shallow-negative) | −2.35 | 12.56% | 1500 | 2000* | 96.6% / 97.2% | −10.24 | cash 46% / margin 37% | B1+B2 confirmed on 2nd fixture; z\*\* seed-unstable (1000–2000); cash dominance exceeds Carvana |
| 3 | candidate3 | CloudGrow (positive-centre fragile) | +5.58 | 12.535% | 2000 | 2000* | 0.0% / 0.6% | −2.89 | margin 41% / cash 25% | **B1+B2 absent** — positive centre re-enables full convergence machinery; shocked margin thin (+3%) but correct |
| 4A | candidate4 | PowerGridCo (**failed pre-run check**) | −9.62 | 10.345% | — | — | — / — | — | — | **Positive-centre gate not met** — capex > D&A + heavy debt + thin margins + high WACC compounded; pipeline not run; no architecture evidence |
| 4B | candidate4b | MedTechX (positive-centre fragile, beta 2.4) | +6.20 | 14.98% | 3,000 | 5,000 | 0.4% / 3.1% | −6.80 | margin 41% / cash 32% | **First z\*\*>z\* (all seeds); F8 partially confirmed — engine louder on shocked pass; shocked margin seed-conditional, not universally thin |
| 5 | candidate5 | RetailRollup (positive-centre fragile, high revenue scale) | +26.16 | 12.845% | 3,000 | 7,500 | 2.6% / 6.8% | −61.53 | margin 42% / cash 31% | **Largest z\*\*−z\* gap (2 rungs, seed 42); cash did NOT overtake margin at rev/eq 2.75×; sigma driven by revenue scale not beta; shocked floor −$61.53 (largest positive-centre extension)** |
| 6 | candidate6 | Project Doom (**gate-failed**, beta 4.0) | −13.19 | 21.375% | — | — | — / — | — | — | **Positive-centre gate not met** — WACC 21.4% (beta 4.0) + capex 7–8% + NWC 6% of rapidly-growing revenue produce negative FCFs years 1–4; PV(FCF)=−$699M overwhelms PV(TV)=$139M; breakeven beta ≈ 0.594; pipeline not run; gate/convergence coupling confirmed (second gate failure) |
| 7 | candidate7 | TitanScale (**stress test, rev-scale**) | +459.24 | 13.800% | 2,000 | 2,000 | 0% / — | — | — | **Grid saturation not achieved** — revenue-scale amplification is scale-neutral for convergence (bar = 1% × mean scales with σ); CV = 33% → true n_true ≈ 1,100; z\* = z\*\* = 2,000; no borderline; benchmark holds (0.09% gap at 20% compute); shocked engine knife-edge at n=1,500 (scatter/bar = 1.06) is the sole stress signal; F13 established |
| 8 | candidate8 | LeveragedRetail (**gate-failed**, leverage CV amplification) | −16.59 | 8.244% | — | — | — / — | — | — | **Positive-centre gate not met** — net_debt $21,000M exceeds EV $17,682M by $3,318M; WACC lowered to 8.244% by 75% debt weight (maximum tax shield) but $18,500M debt increase swamps $8,643M EV gain from lower WACC; D/V scan confirms no capital structure assumption rescues gate with this debt load; leverage path has same gate-convergence incompatibility as beta path (F11 extended to three routes) |
| 8B | candidate8b | ThinEquity (**B1 fires on positive centre**, leverage CV amplification) | +8.41 | 8.244% | 2,000 (elbow) | 2,000 (elbow) | 41.7% / 51.8% | −133.17 | margin 156/300 worst-5 | **z\_pct = None on all 4 seeds, both passes — B1 fires on positive-centre fixture.** CV = 419% (σ=$31.48, mean=$7.51); n\_theory ≈ 175,000 → grid saturation predicted but not observed. Elbow fires at 1,500–2,000 before grid top. New F15: B1 can fire on positive-centre companies when extreme CV makes convergence center\_mean estimate go negative (shock pass: center\_mean = −$0.665). New F16: leverage-CV amplification routes through elbow, not grid ceiling — z\* = 1,500–2,000, not 10,000 |

---

## Findings ledger (architecture-level, accumulating)

A finding is promoted to **architecture** tier only when it reproduces across ≥2 fixtures.
Until then it sits at **candidate** or **fragile-class** tier with its source named.

| ID | Tier | Finding | Source(s) | Status |
|----|------|---------|-----------|--------|
| F1 | **architecture** | Decision margin can collapse (deeply negative) while z\* stays stable — the sample-size diagnostic and the decision-confidence diagnostic are genuinely independent axes. | Carvana, Rivian | **CONFIRMED** — both negative-centre fixtures show stable z elbow with uniformly negative margins (−117% to −207%) across all seeds |
| F2 | **architecture** | A negative-centre valuation silently disables the precision arm (z_pct = None, bar < 0) — the convergence rule silently runs on one leg (elbow only). Steady Co (positive centre) could never expose this. | Carvana, Rivian | **CONFIRMED** — identical z_pct = None on both fixtures, both engines, all seeds. Sign of centre is binary — a shallow negative (−$2.35) triggers the same inversion as a deep one (−$5.61) |
| F3 | **architecture** | For positive-centre fragile companies: z\*\* ≥ z\* on all seeds (CloudGrow: tied; MedTechX: z\*\*>z\* by 1–2 rungs). For negative-centre companies: z\*\* direction was masked by B2 and remains unresolved. The positive-centre direction is now established and directionally intuitive — shocks widen sigma, precision rule responds with higher z\*\*. | Carvana, Rivian (masked), CloudGrow, MedTechX (positive-centre evidence) | **RESOLVED for positive-centre regime** — direction established: z\*\*≥z\*. Negative-centre direction still requires B1/B2 fix to observe cleanly. |
| F4 | **fragile-class** | Cash channel disproportionately drives worst 5% for high-revenue / thin-per-share-equity companies. Equal base hazards, systematically unequal consequences, ordered by capital structure × revenue-sizing. | Carvana (37%), Rivian (46%) | **CONFIRMED** — two fixtures, same mechanism, escalating with revenue/equity ratio. Steady Co (15%) is the baseline. |
| F5 | **architecture** | The elbow leg alone, when the precision leg is disabled, finds a usable sample size for negative-centre companies. Benchmark thesis survives: z\* elbow-only reproduces folk-10,000 within 1% at 15–20% compute. | Carvana (0.92% gap, 20% compute), Rivian (0.67% gap, 15% compute) | **CONFIRMED** — two fixtures confirm elbow reliability independent of precision leg |
| F6 | **architecture** | Borderline mis-fire on negative centres suppresses batch-grading and z\*\* seed-sensitivity reporting — the engine gets quieter precisely when it should be louder. Fragile companies get less convergence scrutiny than healthy ones. | Carvana, Rivian | **CONFIRMED** — rec_batches pinned 40 on all seeds for both fixtures; contrast Steady Co's shocked swing 171–1,464 |
| F7 | **architecture** | B1 and B2 are negative-centre phenomena, not fragile-company phenomena. The sign of the valuation centre is a binary switch: positive centres enable the full convergence machinery; negative centres disable it structurally, regardless of magnitude. | Carvana, Rivian (trigger), CloudGrow (non-trigger) | **CONFIRMED** — CloudGrow (+$5.58 centre, beta 1.9, WACC 12.535%) shows z_pct active, margins positive, borderline correct, batch-grading working, on all seeds and both engines. Neither B1 nor B2 fires. |
| F8 | **architecture** | The engine correctly detects that the shocked pass is harder to converge (wider sigma → higher z\*\*) and responds: z\*\* ≥ z\* on both positive-centre fragile fixtures; batch machinery correctly grades rec_batches from the margin at z\*\*. The thin-margin / large-batches pattern appears seed-conditionally (when z\*\* falls at a grid rung where scatter is still near the bar) — not as a universal consequence of shock presence. Engine is louder on the shocked pass for the right reason. **The strong-form "shocked margins always thin" is not architecture-level.** | CloudGrow, MedTechX | **CONFIRMED (revised framing)** — two positive-centre fixtures. Promoted to architecture tier with nuanced statement. |
| F9 | **architecture** (three fixtures) | z\*\* ≥ z\* on all seeds for positive-centre fragile companies. CloudGrow (beta 1.9): z\*\*=z\* tied. MedTechX (beta 2.4): z\*\*>z\* by one–two grid rungs on all seeds. RetailRollup (beta 2.2, large revenue scale): z\*\*>z\* by two rungs (seed 42), one rung (seed 99), tied on seeds 123/7. Zero instances of z\*\*<z\* across three fixtures and twelve seeds. The z\*\*−z\* gap grows with sigma; sigma has two drivers — beta (WACC volatility) AND revenue scale (FCF/equity volatility). | CloudGrow, MedTechX, RetailRollup | **CONFIRMED (architecture, three fixtures)** — consistent direction on all seeds across all three positive-centre fixtures. |
| F10 | **fragile-class** | The worst-5% channel ordering margin > cash > revenue > strategic > funding is stable across all three positive-centre fragile fixtures (CloudGrow, MedTechX, RetailRollup) and does not flip to cash dominance even at revenue/equity ratio 2.75×. Cash share is elevated above the Steady Co baseline (15%) on all three positive-centre fixtures (25%–32%), but margin retains the lead due to its persistence advantage. | CloudGrow, MedTechX, RetailRollup | **CONFIRMED (fragile-class, three fixtures)** — channel ordering robust; cash dominance (as seen for negative-centre companies) does not appear for positive-centre companies under V1 calibration. |
| F11 | **architecture** | The pre-run positive-centre gate and the convergence stress-test objective are structurally coupled in a way that creates a systematic blind spot: fixtures designed to maximise sigma via high beta (equity cost → WACC → Gordon-multiple compression) tend toward negative centres and fail the gate, while fixtures that pass the gate trend toward revenue-scale sigma. The architecture cannot simultaneously observe gate-passing behaviour and maximum-beta behaviour. | PowerGridCo (4A), Project Doom (6) — two gate failures | **CONFIRMED (architecture, two gate-failed fixtures)** — both failures driven by high investment intensity + elevated WACC; neither delivers convergence evidence. The grid-saturation question (does z\* reach 10,000?) requires a revenue-scale-path fixture, not a beta-path fixture. |
| F12 | **fragile-class** | Investment-intensive fixtures (capex 7–8% + NWC 6% of rapidly growing revenue) produce deeply negative FCFs in early years that overwhelm terminal value at any realistic WACC. Negative centre is structural — not resolved by beta adjustment alone. For Project Doom the breakeven beta is ≈ 0.594 (WACC 7.33%), well below the market-risk threshold. The same mechanism drove PowerGridCo's failure (capex > D&A + $20/share debt burden). | PowerGridCo (4A), Project Doom (6) | **CONFIRMED (fragile-class, two fixtures)** — two independent fixtures with different capital structures both fail due to investment-intensity × WACC compounding. Gate-failure is predictable from inputs without running the pipeline. |
| F13 | **architecture** | Revenue-scale amplification is scale-neutral for the convergence precision rule. The 1% precision bar is a relative criterion (1% of mean); when revenue scale rises, σ and mean scale together, leaving CV unchanged. Convergence is governed entirely by CV: `n_true = (CV / 0.01)²`. Absolute per-share magnitude and share count have no independent effect on z\*. Grid saturation requires CV > 100% (σ > mean), which is not achievable in positive-centre companies under standard trajectory widths. The revenue-scale path (F11's predicted route) cannot stress the grid to 10,000 via scale alone. | TitanScale (7) | **ESTABLISHED (one fixture)** — single fixture; needs replication. Directly resolves the open question from F11: revenue-scale amplification alone cannot push z\* past N_GRID ceiling. |
| F14 | **architecture** | A third route to high sigma — leverage-driven CV amplification through the equity bridge — has the same gate-convergence incompatibility as the beta path (F11). Extreme leverage both thins the equity denominator (raising CV, the intended effect) and may cause debt to exceed EV (killing the gate). For this particular fixture, the $18,500M debt increase swamps the $8,643M EV gain from lower WACC, producing negative equity. All three known sigma-amplification routes (beta, revenue-scale, leverage) share a self-defeating property: the mechanism that stresses the grid also risks disabling the gate. | PowerGridCo (4A), Project Doom (6), LeveragedRetail (8) — three gate failures across three routes | **ESTABLISHED** — three fixtures, three distinct mechanisms, same structural coupling. The gate and grid are architecturally coupled across all probed routes. A thin-equity leverage fixture (calibrated net_debt just below EV breakeven) remains the untested path to test the leverage-CV hypothesis properly. |
| F15 | **architecture** | B1 (sign-fragile precision bar) can fire on positive-centre fixtures when CV is extreme. The B1 trigger condition is not "negative deterministic centre" — it is "any condition that makes the convergence algorithm's own center\_mean estimate go negative." At CV ≈ 419%, the mean of run-means is highly unstable; the shock-pass center\_mean = −$0.665 even though the true mean is positive (+$7.51) and the deterministic gate value is +$8.41. When center\_mean < 0, precision\_bar = 1% × center\_mean < 0, and z\_pct is undefined. B1 fires on all 4 seeds, both passes. | ThinEquity (C8B) | **ESTABLISHED (one fixture)** — new trigger condition confirmed. B1's domain is broader than prior evidence suggested. Needs replication on a second extreme-CV positive-centre fixture to reach architecture tier. |
| F16 | **architecture** | Leverage-CV amplification does not produce grid saturation (z\* = 10,000). At CV = 419%, theory predicts n\_true ≈ 175,000 >> N\_GRID, implying certain saturation. Observed: z\* = 1,500–2,000 on all 4 seeds (elbow only). The elbow is an early-exit clause that fires when no consecutive grid-point pair shows sufficient improvement — which occurs early under flat-scatter conditions (all scatter values >> bar). Additionally, B1 fires before z\_pct can be computed. Grid saturation requires the scatter to just barely exceed the bar at n = 10,000 (precision-binding), which requires both bar > 0 (B1 not triggered) and a narrowly-converging scatter curve. Extreme CV satisfies neither condition. | ThinEquity (C8B) | **ESTABLISHED (one fixture)** — resolves the primary C8B research question. The leverage-CV path does not stress the grid ceiling; it stresses the elbow and B1 simultaneously. Combined with F13 (revenue-scale path CV-neutral), this closes two of three sigma-amplification routes as incapable of producing grid saturation under the current architecture. |

---

## Open bugs / watch items

| ID | Severity | Description | First seen | Status |
|----|----------|-------------|-----------|--------|
| B1 | **high** | **Sign-fragile precision bar.** Precision bar = 1% × valuation goes negative when the centre is negative, silently disabling z_pct. The fix must be sign-aware — options: (a) bar as fraction of |centre|; (b) bar as fraction of σ (sign-agnostic and scale-free — architecturally cleanest); (c) explicit N/A branch for non-positive centres. | Carvana, Rivian | **CONFIRMED on 2nd fixture** — severity upgraded from watch to confirmed. Shallow negative (−$2.35) triggers identically to deep negative (−$5.61). Fix needed before the primary architecture question (positive-centre fragile company) can be cleanly answered. |
| B2 | **high** | **Borderline flag mis-fires on negative centres**, suppressing batch-grading, refinement, and z\*\* seed-sensitivity reporting. Reports `adequately_resolved=True` as false comfort. Fragile companies get less convergence scrutiny than healthy ones — backwards from what fat tails warrant. | Carvana, Rivian | **CONFIRMED on 2nd fixture** — severity upgraded. Both fixtures, all seeds, both engines: `borderline=True`, `batches_recommended=40` (pinned). Contrast Steady Co's correct 171–1,464 swing under shocks. |
| B3 | medium | **z\*\* seed-instability undetected on negative-centre companies.** Rivian shocked z\*\* ranges 1,000–2,000 across seeds (3-rung spread) with a non-monotone scatter bump at n=3,000. Because B2 suppresses batch-grading, the engine doesn't flag this instability — it silently picks whichever elbow the seed delivers. | Rivian | **PARTIALLY RESOLVED** — CloudGrow (positive-centre) shows the margin/rec_batches pathway correctly surfaces instability: shocked margin thin (+1.9–8.4%), rec_batches 286–5,294 across seeds. The instability is now correctly reported rather than silently hidden. Remains medium because the underlying seed-sensitivity of shocked z\*\* (1–2 grid rungs) is structural to the grid resolution, not a bug per se. |

---

## Copy-paste template for a new candidate row + log kickoff

```
# In case_study_runner.py CANDIDATES dict:
"candidateN": DCFInputs(
    starting_revenue=, net_debt=, shares_outstanding=, forecast_years=5,
    revenue_growth=[...], operating_margin=[...],
    capex_pct_revenue=[...], da_pct_revenue=[...], nwc_pct_revenue=[...],
    tax_rate=0.25, terminal_growth=0.025, risk_free_rate=0.04,
    equity_risk_premium=0.055, beta=, cost_of_debt=, debt_to_total_capital=,
),

# Register row (fill from <slug>_results.json):
| N | candidateN | <Name> | <central> | <wacc> | <z*> | <z**> | <%neg cont>/<%neg shock> | <floor> | <driver> | <observation> |
```

Questions worth checking on each new fixture (carried forward):
1. Does B1 (negative precision bar) fire? *(RESOLVED: fires on negative-centre companies; confirmed absent on positive-centre companies. Check: does the fix — bar as fraction of σ — work correctly?)*
2. Does z\*\* separate from z\* — above or below — and is the gap systematic? *(CloudGrow: z\* and z\*\* both in 1500–2000 band, no systematic direction. Need higher-σ or more fragile positive-centre fixture to test.)*
3. Which channel dominates the worst 5%, and does capital structure predict it? *(Confirmed: revenue/equity ratio is the predictor. High-revenue/thin-equity → cash-dominated. Moderate ratio → margin-dominated.)*
4. Does decision margin collapse while z stays stable (F1)? *(Confirmed on negative centres. On CloudGrow: continuous margin healthy +21%, shocked margin thin +3% — margin changes between passes, z stays stable. F1 holds.)*
5. Does the shocked margin narrow systematically vs continuous? *(CloudGrow: yes all seeds. MedTechX: seed-conditional — compressed on seeds 42 and 7, expanded on seeds 99/123 because z\*\* lands at n=5,000 where scatter is low. Not a universal rule. The core finding is z\*\*>z\*, not consistent margin compression.)*
6. What does this fixture exercise that prior candidates could not? *(Standard question per candidate)*

**Candidate #4A post-mortem (PowerGridCo, 2026-06-01):** Failed the pre-run positive-centre gate. Central DCF = −$9.62/share (WACC 10.345%). Four compounding forces: (1) capex > D&A by 7pp→3pp, making year-1 FCF negative; (2) thin margins (8%→12%); (3) $7,000M net debt on 350M shares = $20/share equity burden; (4) beta 1.8 at 10.345% WACC. No architecture evidence gathered.

**Candidate #4B outcomes (MedTechX, 2026-06-01):** Pre-run check passed (+$6.20, WACC 14.98%). Full pipeline run. Key results: z\*=3,000 (highest positive-centre z\*), z\*\*=5,000 on three seeds, 3,000 on seed 7 — first fixture with consistent z\*\*>z\* separation. F8 confirmed (revised framing). F9 established (z\*\*≥z\* on all seeds for positive-centre fragiles). Channel ordering (margin > cash > revenue) reproduced on second positive-centre fixture. Cash prominence (32%) higher than CloudGrow (25%), consistent with revenue/equity-ratio predictor.

**Candidate #6 post-mortem (Project Doom, 2026-06-01):** Failed the pre-run positive-centre gate. Central DCF = −$13.19/share (WACC 21.375%, beta 4.0). Four compounding forces: (1) WACC 21.4% compresses the Gordon multiple to 5.43×, making terminal value tiny relative to investment-phase losses; (2) capex 7–8% + NWC 6% of rapidly growing revenue produce FCFs of −270, −339, −341, −176 in years 1–4; (3) PV(FCF 1–4) = −$699M overwhelms PV(TV) = $139M; (4) even at beta → 0 the breakeven requires WACC ≤ 7.33% (breakeven beta ≈ 0.594), well below market-risk levels. The primary architecture question (does z\* reach 10,000?) could not be answered: the fixture that was designed to stress the grid was incompatible with the gate it must pass to enter the pipeline. New findings F11 (gate/convergence coupling) and F12 (investment-intensity gate failure class) promoted to architecture and fragile-class tiers respectively. The grid-saturation question requires a revenue-scale-path redesign (see Future Questions in Candidate_6_ProjectDoom.md).

**Candidate #8 post-mortem (LeveragedRetail, 2026-06-01):** Failed the pre-run positive-centre gate. Central DCF = −$16.59/share (WACC 8.244%). The operating template is RetailRollup (C5) with only capital structure changed: net_debt $2,500M → $21,000M; D/V 0.30 → 0.75; cost_of_debt 7.0% → 7.5%; shares 250M → 200M. The lower WACC (8.244% vs 12.845%) inflated EV from $9,039M to $17,682M (+$8,643M) via the WACC tax shield, but the debt increase (+$18,500M) dwarfs the EV gain by $9,857M. Breakeven net_debt = EV = $17,682M; the specified $21,000M exceeds this by $3,318M. D/V scan confirms the specified D/V=0.75 is actually the least-bad case — every lower D/V raises WACC, shrinks EV, and worsens the deficit. Gate failure is structural: no single capital structure parameter change while holding net_debt=21,000M can produce a positive centre. New finding F14 established: leverage path shares same gate-convergence incompatibility as beta path and revenue-scale path — all three known sigma-amplification routes are structurally self-defeating at sufficient intensity. A calibrated thin-equity fixture (net_debt ~95% of EV, e.g. ~$16,800M) remains the correct vehicle for testing the leverage-CV hypothesis.

**Candidate #8B outcomes (ThinEquity, 2026-06-01):** Pre-run check passed (+$8.41/share, WACC 8.244%). Same operating template as RetailRollup (C5) with net\_debt calibrated to $16,000M (equity fraction 9.51% of EV). Primary question: does leverage-CV amplification produce z\* > 10,000? Answer: No. CV = 419% (σ=$31.48/share, mean=$7.51/share), n\_theory ≈ 175,000. Observed z\* = 1,500–2,000 on all 4 seeds — elbow only, z\_pct = None universally. Two mechanisms prevent grid saturation: (1) the elbow fires early under flat scatter (all scatter values >> bar, no meaningful improvement between consecutive grid points); (2) B1 fires even on the positive-centre fixture because the shock-pass center\_mean estimate goes negative (−$0.665) despite a deterministic gate value of +$8.41. New finding F15 establishes B1's trigger condition is "convergence center\_mean < 0," not merely "deterministic central DCF < 0." New finding F16 establishes that leverage-CV amplification routes through the elbow at 1,500–2,000, not the grid ceiling at 10,000. Frac\_negative: 41.7% (cont), 51.8% (shock). Shock floor: −$133.17/share. Shock-free: 75.4%. Combined with F13 (revenue-scale path CV-neutral), two of three sigma-amplification routes are now confirmed incapable of producing grid saturation under the current architecture. The beta path (gate failures) remains the untested but structurally blocked third route.

**Candidate #7 outcomes (TitanScale, 2026-06-01):** Pre-run check passed (+$459.24, WACC 13.80%, beta 2.3). Convergence stress test run (not full pipeline — no shock channel breakdown, no seed sweep, no market-percentile grid). Primary question: does revenue-scale amplification push z\* past 10,000? Answer: No. CV = 33.2%, true theoretical n_true ≈ 1,100. z\* = 2,000 (continuous), z\*\* = 2,000 (shocked). One stress signal: shocked engine at n = 1,500 has scatter/bar = 1.06 (knife-edge, one rung below z\*\*). Benchmark: 0.09% mean gap at 20% compute — holds cleanly. New finding F13 established: revenue-scale amplification is scale-neutral for convergence. Grid saturation requires CV > 100%, which is structurally impossible for positive-centre companies under standard trajectory widths (12%). The open architectural question remains: what fixture design CAN push z\* to 10,000?

**Candidate #5 outcomes (RetailRollup, 2026-06-01):** Pre-run check passed (+$26.16, WACC 12.845%). Full pipeline run. Key results: z\*=3,000 (precision-binding), z\*\*=7,500 on seed 42 (largest positive-centre z\*\* yet, two-rung separation from z\*), tied at 5,000 on seeds 123/7, one-rung separation on seed 99. **Cash did NOT overtake margin** as worst-5% driver despite revenue/equity ratio ~2.75× (margin 42%, cash 31%). The revenue/equity predictor (F4/FC3) is directionally supported but non-monotone above ~1.6×. Sigma = $14.94 continuous (largest positive-centre sigma, driven by revenue scale not beta). Shocked floor −$61.53 (largest positive-centre floor extension). F8 confirmed on third fixture. F9 confirmed on third fixture. New observation: sigma = f(beta, revenue_scale) and z\*\* tracks sigma rather than beta alone. F10 established: positive-centre channel ordering margin>cash is robust across three fixtures.
