"""
Monte Carlo Smoke Test — zero-perturbation collapses to deterministic
=====================================================================

The proof that the perturbation layer (mc_engine) is bolted cleanly onto the
deterministic engine (dcf) and does not distort it when switched off.

The logic: if we set both perturbation widths to zero, every random draw
becomes a no-op. Each normal dial scales by (1 + 0) = 1, the per-year noise
is 0, and terminal_growth is held at its central value (the off-switch
convention in sample_inputs). So EVERY simulation must reproduce the single
deterministic value run_dcf(base) returns — exactly, to floating point.

If this passes, the Monte Carlo machinery is a faithful wrapper: it adds
dispersion and nothing else. If it fails, the perturbation layer is leaking
some systematic shift into the valuation even at zero width, which would
contaminate every real run.

Run:  python3 mc_smoke_test.py
"""

# --- engine path bootstrap (auto-added during reorg; frozen engine lives in ../engine) ---
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "engine"))
# --- end bootstrap ---

import numpy as np

from dcf import DCFInputs, run_dcf
from mc_config import MCConfig
from mc_engine import run_monte_carlo, summarize


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


def test_zero_perturbation_collapses_to_deterministic() -> None:
    """With both widths at zero, every simulation must equal run_dcf(base)."""
    base = steady_co()
    deterministic = run_dcf(base)

    # Turn perturbation fully off: trajectory width 0 (which also freezes
    # terminal_growth via the off-switch convention) and per-year noise 0.
    config = MCConfig(
        n_simulations=1000,
        random_seed=42,
        width_overrides={"trajectory": 0.0, "per_year_noise": 0.0},
    )
    results = run_monte_carlo(base, config)

    arr = np.array(results)
    # Every draw identical to the deterministic value, to floating-point
    # tolerance. np.allclose with a tight tolerance is the right check —
    # the arithmetic should match to epsilon, not just "approximately".
    assert np.allclose(arr, deterministic, rtol=0, atol=1e-12), (
        f"zero-perturbation drift detected: deterministic={deterministic}, "
        f"min={arr.min()}, max={arr.max()}"
    )

    spread = arr.max() - arr.min()
    print("PASS  zero-perturbation collapse")
    print(f"        deterministic per-share : {deterministic:.10f}")
    print(f"        MC min / max            : {arr.min():.10f} / {arr.max():.10f}")
    print(f"        spread across 1000 runs : {spread:.2e}  (want ~0)")


def test_perturbation_on_produces_spread() -> None:
    """Sanity counter-check: with the real widths, the distribution DOES spread.

    Guards against a false pass where the engine looks deterministic because
    perturbation is silently broken (e.g. widths not being read at all).
    """
    base = steady_co()
    config = MCConfig(n_simulations=2000, random_seed=42)  # real default widths
    results = run_monte_carlo(base, config)
    s = summarize(results)

    assert s.std > 0.5, f"expected real dispersion, got std={s.std}"
    print("PASS  perturbation-on produces spread")
    print(f"        std across 2000 runs    : {s.std:.4f}  (want > 0.5)")
    print(f"        median                  : {s.median:.4f}  (near deterministic)")


def test_seed_reproducibility() -> None:
    """Same seed => identical distribution; different seed => different."""
    base = steady_co()
    a = run_monte_carlo(base, MCConfig(n_simulations=500, random_seed=7))
    b = run_monte_carlo(base, MCConfig(n_simulations=500, random_seed=7))
    c = run_monte_carlo(base, MCConfig(n_simulations=500, random_seed=8))

    assert a == b, "same seed produced different results"
    assert a != c, "different seed produced identical results"
    print("PASS  seed reproducibility")
    print("        seed 7 == seed 7,  seed 7 != seed 8")


if __name__ == "__main__":
    print("=" * 60)
    print("Monte Carlo smoke test")
    print("=" * 60)
    test_zero_perturbation_collapses_to_deterministic()
    print()
    test_perturbation_on_produces_spread()
    print()
    test_seed_reproducibility()
    print()
    print("All smoke tests passed.")
