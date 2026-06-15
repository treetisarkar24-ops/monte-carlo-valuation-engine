"""
Shock-Overlay Smoke Test — the overlay is a clean, switchable add-on
====================================================================

Three proofs that mc_shocks bolts onto the step-3 engine without distorting it,
and a fourth diagnostic that inspects WHICH channels drive the worst paths.

1. disabled == pure step-3
   With enabled=False, run_monte_carlo_with_shocks must return EXACTLY the same
   list run_monte_carlo returns under the same seed. The shocked runner threads
   one generator through perturb-then-shock; when shocks are off, apply_shocks
   returns the inputs untouched and consumes no random numbers, so the RNG
   stream stays aligned with the pure step-3 run. Identical to floating point.

2. shocks-on bites
   With enabled=True the distribution must (a) spread wider, (b) drop its
   minimum below the shocks-off minimum, (c) pull the 5th percentile and the
   mean DOWN. Shocks only ever damage — never improve — so the whole left side
   of the histogram should sink. This proves the cascades actually fire and the
   fat LEFT tail is real, not a symmetric widening.

3. seed reproducibility
   Same seed => identical shocked distribution; different seed => different.

4. trip-wire diagnostic (NOT an assertion — an observation)
   Tally, across the worst paths, which channel did the most damage. The
   step-5 design flagged a watch item: are funding/cash-driven cascades
   implausibly rare? Equal base hazards + equal fragility weights mean no
   channel is structurally favoured, so we just print the mix and eyeball it.

Run:  python3 mc_shocks_smoke_test.py
"""

# --- engine path bootstrap (auto-added during reorg; frozen engine lives in ../engine) ---
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "engine"))
# --- end bootstrap ---

import numpy as np

from dcf import DCFInputs, run_dcf
from mc_config import MCConfig
from mc_engine import run_monte_carlo, summarize
from mc_shocks import (
    run_monte_carlo_with_shocks,
    sample_inputs_with_shocks,
    apply_shocks,
)
import mc_defaults


def steady_co() -> DCFInputs:
    """The Steady Co central case — the project's standard teaching fixture."""
    return DCFInputs(
        starting_revenue=1000,
        net_debt=300,
        shares_outstanding=100,
        forecast_years=5,
        revenue_growth=[0.10, 0.08, 0.06, 0.05, 0.04],
        operating_margin=[0.15] * 5,
        capex_pct_revenue=[0.07] * 5,
        da_pct_revenue=[0.05] * 5,
        nwc_pct_revenue=[0.02] * 5,
        tax_rate=0.25,
        terminal_growth=0.025,
        risk_free_rate=0.04,
        equity_risk_premium=0.055,
        beta=1.1,
        cost_of_debt=0.05,
        debt_to_total_capital=0.30,
    )


def test_disabled_equals_pure_step3() -> None:
    """enabled=False must reproduce run_monte_carlo exactly under one seed."""
    base = steady_co()
    config = MCConfig(n_simulations=2000, random_seed=42)

    pure = run_monte_carlo(base, config)
    off = run_monte_carlo_with_shocks(base, config, enabled=False)

    assert off == pure, (
        "shocks-disabled run diverged from pure step-3 — the overlay is "
        "consuming random numbers or mutating inputs even when off"
    )
    print("PASS  disabled == pure step-3")
    print(f"        {len(pure)} paths, identical to floating point")


def test_shocks_on_bites() -> None:
    """enabled=True must widen the spread and sink the left tail."""
    base = steady_co()
    config = MCConfig(n_simulations=5000, random_seed=42)

    off = summarize(run_monte_carlo_with_shocks(base, config, enabled=False))
    on = summarize(run_monte_carlo_with_shocks(base, config, enabled=True))

    assert on.std > off.std, f"shocks did not widen spread: {on.std} <= {off.std}"
    assert on.minimum < off.minimum, (
        f"shocks did not lower the floor: {on.minimum} >= {off.minimum}"
    )
    assert on.percentiles[5] < off.percentiles[5], (
        f"5th pct did not sink: {on.percentiles[5]} >= {off.percentiles[5]}"
    )
    assert on.mean < off.mean, f"mean did not fall: {on.mean} >= {off.mean}"

    print("PASS  shocks-on bites (wider spread, left tail sinks)")
    print(f"        std    off / on : {off.std:8.3f} / {on.std:8.3f}")
    print(f"        mean   off / on : {off.mean:8.3f} / {on.mean:8.3f}")
    print(f"        5th    off / on : {off.percentiles[5]:8.3f} / {on.percentiles[5]:8.3f}")
    print(f"        min    off / on : {off.minimum:8.3f} / {on.minimum:8.3f}")


def test_seed_reproducibility() -> None:
    """Same seed => identical shocked distribution; different seed => different."""
    base = steady_co()
    a = run_monte_carlo_with_shocks(base, MCConfig(n_simulations=500, random_seed=7))
    b = run_monte_carlo_with_shocks(base, MCConfig(n_simulations=500, random_seed=7))
    c = run_monte_carlo_with_shocks(base, MCConfig(n_simulations=500, random_seed=8))

    assert a == b, "same seed produced different shocked results"
    assert a != c, "different seed produced identical shocked results"
    print("PASS  seed reproducibility")
    print("        seed 7 == seed 7,  seed 7 != seed 8")


def diagnostic_channel_mix() -> None:
    """Observe which channels fire and which drive the worst paths.

    Not an assertion. Re-runs the perturb-then-shock path loop directly (so we
    can read each path's ShockOutcome, which run_monte_carlo_with_shocks throws
    away after valuing) and tallies: total fires per channel, and — among the
    worst-valued 5% of paths — which channel appears most. The trip-wire from
    the design notes: if funding/cash almost never drive cascades, that's the
    data-grounded reason to differentiate fragility weights in V2.
    """
    base = steady_co()
    config = MCConfig(n_simulations=5000, random_seed=42)
    rng = np.random.default_rng(config.random_seed)

    rows = []  # (value, outcome)
    for _ in range(config.n_simulations):
        outcome = sample_inputs_with_shocks(base, config, rng, enabled=True)
        rows.append((run_dcf(outcome.inputs), outcome))

    fires = {ch: 0 for ch in mc_defaults.SHOCK_CHANNELS}
    for _, oc in rows:
        for ev in oc.events:
            fires[ev.channel] += 1

    total_fires = sum(fires.values())
    paths_with_any = sum(1 for _, oc in rows if oc.events)
    shock_free_pct = 100.0 * (1 - paths_with_any / len(rows))

    # Worst 5% of paths by value: which channel fired most among them?
    rows_sorted = sorted(rows, key=lambda r: r[0])
    worst = rows_sorted[: max(1, len(rows) // 20)]
    worst_fires = {ch: 0 for ch in mc_defaults.SHOCK_CHANNELS}
    for _, oc in worst:
        for ev in oc.events:
            worst_fires[ev.channel] += 1

    print("OBSERVE  channel diagnostic")
    print(f"        shock-free paths        : {shock_free_pct:5.1f}%  (Steady Co ~75% target)")
    print(f"        total shock fires       : {total_fires}")
    print("        fires by channel        :")
    for ch in mc_defaults.SHOCK_CHANNELS:
        share = 100.0 * fires[ch] / total_fires if total_fires else 0.0
        print(f"            {ch:9s} : {fires[ch]:5d}  ({share:4.1f}%)")
    print("        among WORST 5% of paths :")
    wtot = sum(worst_fires.values())
    for ch in mc_defaults.SHOCK_CHANNELS:
        share = 100.0 * worst_fires[ch] / wtot if wtot else 0.0
        print(f"            {ch:9s} : {worst_fires[ch]:5d}  ({share:4.1f}%)")


if __name__ == "__main__":
    print("=" * 60)
    print("Shock overlay smoke test")
    print("=" * 60)
    test_disabled_equals_pure_step3()
    print()
    test_shocks_on_bites()
    print()
    test_seed_reproducibility()
    print()
    diagnostic_channel_mix()
    print()
    print("All shock smoke tests passed.")
