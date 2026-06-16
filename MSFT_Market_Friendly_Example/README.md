# Microsoft — Market-Friendly Example Case

A self-contained example case for the Monte Carlo Valuation Engine. Drop this
whole folder into the website build folder. Same frozen engine as the headline
case — **only the input fixture changed**, and every CAPM input is held at its
conventional value (beta = Microsoft's historical 0.90, not reverse-solved).

## Headline numbers (market reference ~$450)

| Metric | Value |
|---|---|
| DCF (point value) | **$326.41 / share** |
| Monte Carlo median | **$309.05 / share** |
| Where the market sits | **~94th percentile** of the distribution |
| WACC | 9.16% (beta 0.90, natural) |
| Terminal growth | 3.0% |
| Forecast horizon | 10 years |
| Convergence size z* | 2,000 |

Read: under a defensible, market-friendly set of assumptions — with the discount
rate left at its conventional 9.16% — Microsoft at ~$450 still looks **rich
(~94th percentile)**. The market is paying near the top of what these
fundamentals support, but not literally off the chart. The conservative headline
fixture puts it at ~99th; this one at ~94th. Same engine, two honest reads; the
only things that moved are the forecast paths, the horizon, and terminal growth.

## What changed vs the conservative headline fixture

- Terminal growth 2.5% -> **3.0%**
- Horizon 7 -> **10 years**, growth fading slowly to 5%
- Operating margin ceiling 47% -> **49%**
- Discount rate **unchanged** at 9.16% (beta held at 0.90)

No CAPM input was tuned to hit a target. That is the point of this version: the
result rests on a discount rate you can defend without argument.

## Files

| File | What it is |
|---|---|
| `msft_B_fixture.json` | The engine input fixture (16 fields). |
| `MSFT_MarketFriendly_FILLED.xlsx` | The same inputs as a filled template — loads in the live "Try It Yourself" engine. Verified to reprice to $326.41. |
| `msft_B_results.json` | Full engine output: central DCF, convergence z*, production MC (seed 42), histogram, percentiles, market percentile. |
| `msft_B_meta.json` | Company, market reference, the assumptions table, and notes. |

## How to use in the build

- **Key Visual / distribution:** `msft_B_results.json` -> `cont.production.pct`
  and `cont.histogram` (price marker at $450, the ~94th percentile).
- **Live "Try It Yourself":** load `MSFT_MarketFriendly_FILLED.xlsx` through
  `excel_loader.py` -> engine. It runs live and reprices to the numbers above.
- Numbers are final — do not recompute or re-round.
