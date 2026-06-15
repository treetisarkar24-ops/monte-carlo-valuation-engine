"""
Candidate #7 — TitanScale
=========================
Convergence stress test: revenue-scale amplification.

Design intent:
  - Very large revenue scale (30,000) + very small share count (50)
    => per-share values in the hundreds-to-thousands range
    => absolute sigma is enormous, straining the 1%-precision bar
  - Moderate-to-high beta (2.3) + positive-centre economics
    => WACC is high but the company is profitable — valid positive centre
  - Primary question: does the true convergence requirement exceed N_GRID[-1] = 10,000?

Instructions (fixture): Do NOT modify engine logic or N_GRID.
"""

# --- engine path bootstrap (auto-added during reorg; frozen engine lives in ../engine) ---
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "engine"))
# --- end bootstrap ---

import json
import sys
import os

# ── path ──────────────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

from dcf import DCFInputs, run_dcf, compute_wacc
from mc_config import MCConfig
from mc_engine import run_monte_carlo, summarize, format_summary
from mc_convergence import (
    convergence_with_recommendation,
    convergence_with_shocks,
    benchmark_against_folk,
    format_pair,
    format_benchmark,
    plot_convergence,
    ConvergenceResult,
)
import mc_defaults


# ── fixture ───────────────────────────────────────────────────────────────────
BASE = DCFInputs(
    starting_revenue       = 30_000,
    net_debt               = 500,
    shares_outstanding     = 50,
    forecast_years         = 5,
    revenue_growth         = [0.20, 0.18, 0.15, 0.12, 0.10],
    operating_margin       = [0.08, 0.09, 0.10, 0.11, 0.12],
    capex_pct_revenue      = [0.05, 0.05, 0.05, 0.04, 0.04],
    da_pct_revenue         = [0.03, 0.03, 0.03, 0.03, 0.03],
    nwc_pct_revenue        = [0.02, 0.02, 0.02, 0.02, 0.02],
    tax_rate               = 0.25,
    terminal_growth        = 0.025,
    risk_free_rate         = 0.04,
    equity_risk_premium    = 0.055,
    beta                   = 2.3,
    cost_of_debt           = 0.07,
    debt_to_total_capital  = 0.25,
)


# ── deterministic sanity check ────────────────────────────────────────────────
def deterministic_check():
    wacc = compute_wacc(BASE)
    per_share = run_dcf(BASE)
    print("=" * 60)
    print("DETERMINISTIC CENTRAL CASE")
    print("=" * 60)
    print(f"  WACC           : {wacc*100:.3f}%")
    print(f"  per-share (DCF): ${per_share:,.4f}")
    print(f"  shares         : {BASE.shares_outstanding}")
    print(f"  net_debt       : {BASE.net_debt:,}")
    print()
    return wacc, per_share


# ── sigma survey — how wide is the distribution? ─────────────────────────────
def sigma_survey(mean_price: float):
    """Run one large batch to characterise sigma and the CV."""
    print("=" * 60)
    print("SIGMA SURVEY  (n = 40,000 reference run)")
    print("=" * 60)
    cfg = MCConfig(n_simulations=40_000, random_seed=42)
    results = run_monte_carlo(BASE, cfg)
    summary = summarize(results)
    cv = summary.std / abs(summary.mean) if summary.mean != 0 else float("inf")
    precision_bar = mc_defaults.CONVERGENCE_PRECISION_PCT * summary.mean
    # SE at max grid point
    se_at_10k = summary.std / (10_000 ** 0.5)
    margin_at_10k = (precision_bar - se_at_10k) / se_at_10k if se_at_10k > 0 else float("inf")
    print(format_summary(summary))
    print()
    print(f"  coefficient of variation (CV): {cv:.4f}  ({cv*100:.2f}%)")
    print(f"  precision bar (1% of mean)   : ${precision_bar:,.4f}")
    print(f"  sigma/sqrt(10000)            : ${se_at_10k:,.4f}")
    print(f"  bar - SE@10k (margin)        : ${precision_bar - se_at_10k:,.4f}  ({margin_at_10k*100:+.1f}%)")
    if se_at_10k > precision_bar:
        print()
        print("  *** GRID SATURATION SIGNAL ***")
        print("  SE at n=10,000 still exceeds the 1% precision bar.")
        n_required = (summary.std / precision_bar) ** 2
        print(f"  Theoretical n for rule-2 clearance: {n_required:,.0f}")
    else:
        print()
        print(f"  Rule-2 clearance appears reachable within grid.")
    print()
    return summary


# ── z* sweep (continuous engine) ─────────────────────────────────────────────
def run_z_star():
    print("=" * 60)
    print("PASS 1 — z*  (continuous engine, default 40 batches)")
    print("=" * 60)
    pair = convergence_with_recommendation(BASE)
    print(format_pair(pair))
    print()

    # Plot z* sweep
    result_to_plot = pair.refined if pair.refined is not None else pair.default
    plot_path = os.path.join(os.path.dirname(__file__), "candidate7_zstar_convergence.png")
    plot_convergence(
        result_to_plot,
        save_path=plot_path,
        title="TitanScale — z* convergence  (continuous engine)",
    )
    print(f"  [plot saved: {plot_path}]")
    print()
    return pair


# ── z** sweep (shocked engine) ────────────────────────────────────────────────
def run_z_star_star():
    print("=" * 60)
    print("PASS 2 — z**  (shocked engine)")
    print("=" * 60)
    pair = convergence_with_shocks(BASE)
    print(format_pair(pair))
    print()

    result_to_plot = pair.refined if pair.refined is not None else pair.default
    plot_path = os.path.join(os.path.dirname(__file__), "candidate7_zstarstar_convergence.png")
    plot_convergence(
        result_to_plot,
        save_path=plot_path,
        title="TitanScale — z** convergence  (shocked engine)",
    )
    print(f"  [plot saved: {plot_path}]")
    print()
    return pair


# ── benchmark z* vs folk-10,000 ──────────────────────────────────────────────
def run_benchmark(z_star_pair):
    print("=" * 60)
    print("BENCHMARK — z* vs folk-10,000")
    print("=" * 60)
    bench = benchmark_against_folk(BASE, z_star_pair)
    print(format_benchmark(bench))
    print()
    return bench


# ── grid-saturation deep dive ─────────────────────────────────────────────────
def grid_saturation_probe(sigma: float, mean: float):
    """
    If n=10,000 is at or near the top of the grid and z* = 10,000,
    investigate what n would ACTUALLY be needed.
    Extrapolate from sigma/sqrt(n) = precision_bar.
    """
    print("=" * 60)
    print("GRID SATURATION — TRUE REQUIREMENT ESTIMATE")
    print("=" * 60)
    precision_bar = mc_defaults.CONVERGENCE_PRECISION_PCT * mean
    n_true = (sigma / precision_bar) ** 2
    print(f"  sigma (from 40k ref run)     : {sigma:,.4f}")
    print(f"  mean (central estimate)      : {mean:,.4f}")
    print(f"  precision bar (1% of mean)   : {precision_bar:,.4f}")
    print(f"  true n for rule-2 (theory)   : {n_true:,.0f}")
    ratio = n_true / mc_defaults.N_GRID[-1]
    print(f"  ratio to grid top (10,000)   : {ratio:.2f}x")
    if ratio > 1.0:
        print()
        print(f"  *** TRUE REQUIREMENT EXCEEDS GRID ***")
        print(f"  This company needs ~{n_true:,.0f} simulations to satisfy rule 2.")
        print(f"  The folk-wisdom 10,000 falls {100*(1 - 1/ratio):.1f}% short.")
    else:
        print(f"  Grid is sufficient (ratio < 1).")
    print()
    return n_true


# ── scatter-vs-bar summary across grid ───────────────────────────────────────
def scatter_vs_bar_report(result: ConvergenceResult):
    print("=" * 60)
    print("SCATTER vs PRECISION BAR — every grid point")
    print("=" * 60)
    bar = result.precision_bar
    print(f"  {'n':>7}  {'scatter':>10}  {'bar':>10}  {'scatter/bar':>12}  {'status'}")
    print(f"  {'-'*7}  {'-'*10}  {'-'*10}  {'-'*12}  {'-'*14}")
    for n, s in zip(result.n_grid, result.scatter):
        ratio = s / bar if bar > 0 else float("inf")
        status = "ABOVE BAR" if s > bar else "below bar"
        print(f"  {n:>7,}  {s:>10.4f}  {bar:>10.4f}  {ratio:>12.4f}  {status}")
    print()


# ── main ──────────────────────────────────────────────────────────────────────
def main():
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  CANDIDATE #7 — TitanScale  Convergence Stress Test      ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    print(f"  N_GRID (locked)  : {mc_defaults.N_GRID}")
    print(f"  BATCHES_PER_N    : {mc_defaults.BATCHES_PER_N}")
    print(f"  PRECISION_PCT    : {mc_defaults.CONVERGENCE_PRECISION_PCT*100:.1f}%")
    print()

    # 1. Deterministic centre
    wacc, central_per_share = deterministic_check()

    # 2. Sigma survey
    mc_summary = sigma_survey(central_per_share)

    # 3. Grid saturation probe (pre-sweep theory)
    n_true = grid_saturation_probe(mc_summary.std, mc_summary.mean)

    # 4. z* sweep
    z_star_pair = run_z_star()

    # 5. Scatter vs bar table for z* (default pass)
    scatter_vs_bar_report(z_star_pair.default)

    # 6. z** sweep
    z_star_star_pair = run_z_star_star()

    # 7. Scatter vs bar for z**
    scatter_vs_bar_report(z_star_star_pair.default)

    # 8. Benchmark
    bench = run_benchmark(z_star_pair)

    # 9. Final verdict
    print("=" * 60)
    print("TITANSCALE — STRESS TEST VERDICT")
    print("=" * 60)
    dz = z_star_pair.z_star
    dzz = z_star_star_pair.z_star
    at_grid_top = (dz == mc_defaults.N_GRID[-1] or dzz == mc_defaults.N_GRID[-1])
    print(f"  z*               : {dz:,}")
    print(f"  z**              : {dzz:,}")
    print(f"  z* at grid top?  : {'YES — grid saturation' if dz == mc_defaults.N_GRID[-1] else 'no'}")
    print(f"  z** at grid top? : {'YES — grid saturation' if dzz == mc_defaults.N_GRID[-1] else 'no'}")
    print(f"  z* borderline?   : {z_star_pair.default.borderline}")
    print(f"  z** borderline?  : {z_star_star_pair.default.borderline}")
    print(f"  true n (theory)  : {n_true:,.0f}")
    print(f"  exceeds grid?    : {'YES' if n_true > mc_defaults.N_GRID[-1] else 'no'}")
    print(f"  benchmark gap    : {bench.mean_gap_pct:.4f}%  (z* vs folk-10k)")
    print()

    if at_grid_top or n_true > mc_defaults.N_GRID[-1]:
        print("  FINDING: TitanScale provides positive evidence that the true")
        print("  convergence requirement lies BEYOND the current 10,000 grid.")
        print("  The folk-wisdom ceiling is demonstrably insufficient for this")
        print("  fixture's variance profile.")
    else:
        print("  FINDING: TitanScale converges within the current grid.")
        print("  Revenue-scale amplification alone does not push z* past 10,000.")

    # Save results JSON
    results_data = {
        "candidate": "7_TitanScale",
        "wacc": wacc,
        "central_per_share": central_per_share,
        "sigma": mc_summary.std,
        "mean": mc_summary.mean,
        "cv": mc_summary.std / abs(mc_summary.mean),
        "precision_bar": mc_defaults.CONVERGENCE_PRECISION_PCT * mc_summary.mean,
        "se_at_10k": mc_summary.std / (10_000 ** 0.5),
        "n_true_theory": n_true,
        "z_star": dz,
        "z_star_star": dzz,
        "z_star_borderline": z_star_pair.default.borderline,
        "z_star_star_borderline": z_star_star_pair.default.borderline,
        "z_star_decision_margin_pct": z_star_pair.default.decision_margin_pct,
        "z_star_star_decision_margin_pct": z_star_star_pair.default.decision_margin_pct,
        "benchmark_mean_gap_pct": bench.mean_gap_pct,
        "benchmark_compute_ratio": bench.compute_ratio,
        "grid_saturated": at_grid_top,
        "true_requirement_exceeds_grid": n_true > mc_defaults.N_GRID[-1],
    }
    out_path = os.path.join(os.path.dirname(__file__), "candidate7_results.json")
    with open(out_path, "w") as f:
        json.dump(results_data, f, indent=2)
    print(f"\n  [results saved: {out_path}]")
    print()


if __name__ == "__main__":
    main()
