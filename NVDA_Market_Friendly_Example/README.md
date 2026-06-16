# NVIDIA (NVDA) — Market-Friendly Example Case

Brand-new full engine run as of **16 June 2026**, packaged like the Microsoft
example. The fixture is the **market-friendly** case: operating assumptions set to
the optimistic-but-defensible edge, with the discount rate left honest (beta held
at NVIDIA's defensible historical 1.75 — **not** reverse-engineered). All numbers
are **final**, produced by the frozen engine (seed 42).

## Headline figures

| Metric | Value |
|---|---|
| Central DCF (deterministic) | **$145.78 / share** |
| WACC | **13.42%** |
| Continuous MC median | **$142.21** |
| Continuous P5 / P95 | $84.68 / $231.77 |
| Shocked MC median | $133.29 |
| Convergence z* (continuous) | 3,000 sims |
| Market reference price (15–16 Jun 2026) | **$211.93** (~$5.23T cap) |
| **Market percentile — continuous** | **91st** |
| **Market percentile — shocked** | **~94th** |
| Tail signature | operating (revenue + margin), not financial |

## The read

On a bullish-but-defensible operating case, NVIDIA's market price (**$211.93**) sits
at the **91st percentile** of the continuous distribution and **~94th** of the
shocked one — **rich, but inside the distribution**. The model *can* reach today's
price (max draw $383.49), but only in its optimistic upper decile; the market is
paying ~45% above the bull-case central value of $145.78, and that premium is
carried entirely by the growth and margin assumptions, not by any discount-rate
adjustment.

This contrasts with a *conservative* NVDA fixture, under which the same $211.93
lands **above the entire distribution** (100th percentile). The difference is purely
the operating assumptions — proof the engine faithfully transmits the fixture.

## Files

- `nvda_fixture.json` — the 16-field market-friendly engine input
- `nvda_results.json` — full engine output (central, continuous + shocked MC with
  percentiles, histograms, shock channel diagnostics, seed-robustness, market percentile)
- `NVDA_MarketFriendly_FILLED.xlsx` — input template filled with this fixture;
  verified to reprice to $145.784283 (exact match to the JSON DCF)
- `nvda_meta.json` — headline summary for quick reference
- `NVDA_NVIDIA_Case_Study.md` / `.pdf` — the full written case study

## Reproduce

```
python3 runtime/excel_loader.py NVDA_Market_Friendly_Example/NVDA_MarketFriendly_FILLED.xlsx --run
```
