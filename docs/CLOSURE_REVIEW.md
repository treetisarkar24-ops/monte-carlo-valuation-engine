# Final Closure Review — Monte Carlo Valuation Engine

Purpose: consolidate, in one place, the blind spots, edge cases, architecture
findings, and open questions accumulated across the synthetic stress phase and
the real-world case studies — so the project can be closed (or paused) with a
clean record. Per the project's refinement-mode rule, the open research
questions below are **documented, not chased**: pursuing any of them is a
deliberate decision to reopen a research branch.

Primary sources: `STRESS_TEST_TRACKER.md` (findings ledger F11–F16),
`HANDOFF.md`, `NVDA_Investigation_Log.md`, the MSFT and AMZN case studies.

---

## 1. Validation status

- Core engine: **complete, frozen, validated.** Smoke tests (`mc_smoke_test.py`,
  `mc_shocks_smoke_test.py`) pass; deterministic DCF reproduces documented
  central values (MSFT $263.74, AMZN $96.52).
- Convergence machinery: validated across 10 synthetic fixtures + 2 real
  companies; the per-company `z*` reproduces the 10,000-path "folk number" answer
  within ~1% at ~0.2× compute on every tested case.
- Shock overlay: V1 fragility model in place (severity-weighted damage tally);
  healing/break dynamics (V2) deliberately deferred, not built.

---

## 2. Blind spots (architecture-level, confirmed)

**F11 — gate/convergence coupling (the central blind spot).** The pre-run
positive-centre gate and the convergence stress objective are structurally
coupled. Fixtures engineered to maximise sigma via **high beta** drive the equity
cost → WACC up, compress the Gordon multiple, push the centre negative, and
**fail the gate** — so they never deliver convergence evidence. Fixtures that
pass the gate trend toward modest revenue-scale sigma. Consequence: the
architecture **cannot simultaneously observe gate-passing behaviour and
maximum-beta behaviour.** Confirmed across two gate-failed fixtures (PowerGridCo
4A, Project Doom 6).

**Implication for the grid-saturation question.** No tested route pushes `z*` to
the 10,000 ceiling:
- Revenue-scale path: CV-neutral for convergence (**F13**); grid saturation would
  need CV > 100%, structurally impossible for a positive-centre company at the
  standard 12% trajectory widths.
- Leverage path: amplification routes through the **elbow at 1,500–2,000**, not
  the grid ceiling (**F16**); confirmed on a calibrated thin-equity fixture (8B).
- Beta path: structurally blocked by the gate (F11).

So all three known sigma-amplification routes are either CV-neutral or
self-defeating. "What fixture design *can* push z* to 10,000?" remains genuinely
open and may have no answer under the current architecture.

---

## 3. Edge cases (documented)

- **Gate failures are structural, not bugs.** Project Doom (central −$13.19,
  WACC 21.4%, beta 4.0) and LeveragedRetail (central −$16.59, net_debt $21B >
  enterprise value) fail the positive-centre gate by construction. Recorded as
  the fragile-company class **F12** (investment-intensity) and **F14**
  (leverage), not defects.
- **B1 trigger condition (F15).** The shock-pass safety trip fires on
  *convergence `center_mean` < 0*, **not** on *deterministic central DCF < 0*.
  ThinEquity (8B) passed the deterministic gate at +$8.41/share yet tripped B1
  because the convergence centre estimate went slightly negative (−$0.665). Worth
  remembering when a positive-gate fixture behaves unexpectedly in the shocked
  stage.
- **Negative intrinsic values are valid output**, not errors — high-CV fixtures
  (ThinEquity: 41.7% continuous / 51.8% shocked negative paths) genuinely
  produce them. Real net-cash, high-margin companies (MSFT) produce ~0%.

---

## 4. Open research questions (status; document, don't chase)

1. **Why has z\*\* (shocked) consistently been ≤ z\* (continuous)?** Original
   expectation was z\*\* ≥ z\*. *Status: partially explained.* The NVIDIA instance
   (z\*\*=1,500 < z\*=2,000) was traced to a finite-batch non-monotone scatter
   artefact at the n=1,500→2,000 transition (`NVDA_Investigation_Log.md`).
   Whether the same mechanism drives every other instance is unconfirmed. Note:
   the durable finding is **z\*\* > z\*** on harder fixtures *and* that shocked
   margin compression is **not** universal (CloudGrow: all seeds; MedTechX:
   seed-conditional).
2. **Is the shocked elbow dominated by the same mechanism as the continuous
   elbow?** Open. Both stages resolve via the elbow rather than the percentile
   rule on most fixtures, but a shared mechanism is not established.
3. **Do any real companies naturally need materially higher convergence?** Open.
   Tested real companies (MSFT, NVDA, AMZN) all resolve well below the grid
   ceiling. A genuinely higher-convergence real company has not been found.
4. **Are there archetypes with genuinely different convergence behaviour?** Open.
   The three synthetic amplification archetypes (revenue-scale, leverage, beta)
   are now characterised (F13/F16/F11); whether a *qualitatively different*
   archetype exists is unknown.

---

## 5. Deferred-by-design items (not blind spots)

- **Step 7 — engine-level input validation.** Math-first, validation-last design
  choice. Until built, the spreadsheet gate in `excel_loader.py` is the input
  guard.
- **Shock V2 — healing / break dynamics.** Intentionally scoped out of V1.
- **`terminal_growth` macro-state ("regime") modelling.** Reserved terminology;
  the current stochastic layer is "trajectory perturbation," not regime
  switching.

---

## 6. Closure checklist

| Item | Status |
|---|---|
| Blind spots documented | ✅ F11 (gate/convergence coupling) |
| Edge cases documented | ✅ gate failures, B1 trigger, negative-value validity |
| Architecture findings logged | ✅ F11–F16 in `STRESS_TEST_TRACKER.md` |
| Open questions separated from production findings | ✅ section 4 above |
| Real-world validation | ✅ MSFT, NVDA, AMZN |
| Usability layer | ✅ template, loader, report generator |
| Documentation | ✅ README, WORKFLOW, this review |
| Dashboard | ⏸ planned (`DASHBOARD_PLAN.md`), not built |
| Step 7 engine validation | ⏸ deferred by design |

The engine is in a defensible state to close as "complete + packaged." The only
correctness gap (Step 7) has a working mitigation (the loader gate); everything
else outstanding is either a planned enhancement or a logged research question
that the refinement-mode rule says to leave parked unless deliberately reopened.
