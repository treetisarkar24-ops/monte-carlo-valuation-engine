"""
Candidate #1 - Carvana : staged pipeline run
============================================

Stage-driven so each convergence sweep (~31s) fits one shell call. Results
accrue in candidate1_carvana_results.json; the investigation document is
built from that file, not from memory.

Carvana is a FIXTURE for architecture exploration, NOT an investment call.
Its outputs are case-study observations, never architecture truths.

Usage:  python3 candidate1_carvana_run.py <stage>
Stages: central | cont | shock | seed:<n> | dump
"""

# --- engine path bootstrap (auto-added during reorg; frozen engine lives in ../engine) ---
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "engine"))
# --- end bootstrap ---

import sys
import json
import time
import numpy as np

from dcf import DCFInputs, run_dcf
from mc_config import MCConfig
from mc_engine import run_monte_carlo, summarize, text_histogram
from mc_shocks import run_monte_carlo_with_shocks, sample_inputs_with_shocks
from mc_convergence import (
    convergence_with_recommendation,
    convergence_with_shocks,
    benchmark_against_folk,
)
import mc_defaults

RESULTS = "candidate1_carvana_results.json"
SEED = 42


def carvana() -> DCFInputs:
    return DCFInputs(
        starting_revenue=20300, net_debt=5000, shares_outstanding=220, forecast_years=5,
        revenue_growth=[0.20, 0.15, 0.10, 0.06, 0.04],
        operating_margin=[0.04, 0.05, 0.06, 0.07, 0.08],
        capex_pct_revenue=[0.03] * 5, da_pct_revenue=[0.015] * 5, nwc_pct_revenue=[0.03] * 5,
        tax_rate=0.25, terminal_growth=0.025, risk_free_rate=0.04,
        equity_risk_premium=0.055, beta=2.2, cost_of_debt=0.085, debt_to_total_capital=0.55,
    )


def steady_co() -> DCFInputs:
    return DCFInputs(
        starting_revenue=1000, net_debt=300, shares_outstanding=100, forecast_years=5,
        revenue_growth=[0.10, 0.08, 0.06, 0.05, 0.04], operating_margin=[0.15] * 5,
        capex_pct_revenue=[0.07] * 5, da_pct_revenue=[0.05] * 5, nwc_pct_revenue=[0.02] * 5,
        tax_rate=0.25, terminal_growth=0.025, risk_free_rate=0.04,
        equity_risk_premium=0.055, beta=1.1, cost_of_debt=0.05, debt_to_total_capital=0.30,
    )


def load():
    try:
        with open(RESULTS) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save(d):
    with open(RESULTS, "w") as f:
        json.dump(d, f, indent=2)


def summ_dict(s):
    return {"n": s.n, "mean": s.mean, "median": s.median, "std": s.std,
            "min": s.minimum, "max": s.maximum, "pct": {str(k): v for k, v in s.percentiles.items()}}


def pair_dict(p):
    d = p.default
    return {"z_star": p.z_star, "z_star_moved": p.z_star_moved,
            "adequately_resolved": p.adequately_resolved,
            "final_recommendation": p.final_recommendation,
            "refinement_capped": p.refinement_capped,
            "z_pct": d.z_pct, "z_elbow": d.z_elbow,
            "decision_margin_pct": d.decision_margin_pct,
            "precision_bar": d.precision_bar, "sigma_estimate": d.sigma_estimate,
            "center_mean": float(np.mean(d.center)), "borderline": d.borderline,
            "batches_used": d.batches_used, "batches_recommended": d.batches_recommended,
            "scatter": d.scatter, "n_grid": d.n_grid}


def stage_central(d):
    b = carvana()
    d["central"] = {"carvana": run_dcf(b), "steady_co": run_dcf(steady_co())}
    # WACC + first-year FCF transparency
    from dcf import compute_wacc
    d["central"]["wacc"] = compute_wacc(b)
    print("central:", d["central"])


def stage_cont(d):
    b = carvana()
    t = time.time()
    cont = convergence_with_recommendation(b, rerun=False)  # seeded 42 by default
    z = cont.z_star
    res = run_monte_carlo(b, MCConfig(n_simulations=z, random_seed=SEED))
    s = summarize(res)
    arr = np.asarray(res)
    bench = benchmark_against_folk(b, cont, market_price=None, folk_n=10_000, seed=SEED)
    d["cont"] = {
        "pair": pair_dict(cont),
        "production": summ_dict(s),
        "frac_negative_pct": float(100.0 * np.mean(arr < 0)),
        "histogram": text_histogram(res, bins=20, width=42),
        "benchmark": {"z_star": bench.z_star, "folk_n": bench.folk_n,
                      "compute_ratio": bench.compute_ratio,
                      "mean_gap_pct": bench.mean_gap_pct,
                      "z_mean": bench.z_summary.mean, "z_median": bench.z_summary.median,
                      "folk_mean": bench.folk_summary.mean, "folk_median": bench.folk_summary.median,
                      "z_n": bench.z_summary.n, "folk_n_actual": bench.folk_summary.n},
        "secs": time.time() - t,
    }
    print(f"cont done z*={z} margin%={cont.default.decision_margin_pct:.2f} "
          f"z_pct={cont.default.z_pct} frac_neg={d['cont']['frac_negative_pct']:.1f}% "
          f"in {d['cont']['secs']:.1f}s")


def stage_shock(d):
    b = carvana()
    t = time.time()
    shock = convergence_with_shocks(b, rerun=False)
    z = shock.z_star
    res = run_monte_carlo_with_shocks(b, MCConfig(n_simulations=z, random_seed=SEED))
    s = summarize(res)
    arr = np.asarray(res)
    # channel diagnostic (5000 sims)
    cfg = MCConfig(n_simulations=5000, random_seed=SEED)
    rng = np.random.default_rng(cfg.random_seed)
    rows = []
    for _ in range(cfg.n_simulations):
        oc = sample_inputs_with_shocks(b, cfg, rng, enabled=True)
        rows.append((run_dcf(oc.inputs), oc))
    fires = {ch: 0 for ch in mc_defaults.SHOCK_CHANNELS}
    stresses = []
    for _, oc in rows:
        stresses.append(oc.final_stress)
        for ev in oc.events:
            fires[ev.channel] += 1
    any_paths = sum(1 for _, oc in rows if oc.events)
    rows_sorted = sorted(rows, key=lambda r: r[0])
    worst = rows_sorted[: max(1, len(rows) // 20)]
    wfires = {ch: 0 for ch in mc_defaults.SHOCK_CHANNELS}
    for _, oc in worst:
        for ev in oc.events:
            wfires[ev.channel] += 1
    # market-percentile grid on shocked distribution
    grid = {str(p): float(100.0 * np.mean(arr < p)) for p in (-5, -2, 0, 2, 5, 8, 11, 15)}
    d["shock"] = {
        "pair": pair_dict(shock),
        "production": summ_dict(s),
        "frac_negative_pct": float(100.0 * np.mean(arr < 0)),
        "histogram": text_histogram(res, bins=20, width=42),
        "shock_free_pct": float(100.0 * (1 - any_paths / len(rows))),
        "fires_all": fires,
        "fires_worst5": wfires,
        "mean_stress": float(np.mean(stresses)),
        "max_stress": float(np.max(stresses)),
        "total_fires": int(sum(fires.values())),
        "market_grid": grid,
        "secs": time.time() - t,
    }
    print(f"shock done z**={z} margin%={shock.default.decision_margin_pct:.2f} "
          f"z_pct={shock.default.z_pct} frac_neg={d['shock']['frac_negative_pct']:.1f}% "
          f"shock_free={d['shock']['shock_free_pct']:.1f}% in {d['shock']['secs']:.1f}s")


def stage_seed(d, seed, which):
    b = carvana()
    t = time.time()
    cfg = MCConfig(n_simulations=0, random_seed=seed)
    rec = d.setdefault("seeds", {}).setdefault(str(seed), {})
    if which == "cont":
        c = convergence_with_recommendation(b, config=cfg, rerun=False)
        rec.update(cont_z=c.z_star, cont_batches=c.final_recommendation,
                   cont_margin=c.default.decision_margin_pct, cont_zpct=c.default.z_pct)
        print(f"seed {seed} cont: z*={c.z_star} margin={c.default.decision_margin_pct:.1f} "
              f"zpct={c.default.z_pct} in {time.time()-t:.1f}s")
    else:
        s = convergence_with_shocks(b, config=cfg, rerun=False)
        rec.update(shock_z=s.z_star, shock_batches=s.final_recommendation,
                   shock_margin=s.default.decision_margin_pct, shock_zpct=s.default.z_pct)
        print(f"seed {seed} shock: z**={s.z_star} margin={s.default.decision_margin_pct:.1f} "
              f"zpct={s.default.z_pct} in {time.time()-t:.1f}s")


def main():
    stage = sys.argv[1]
    d = load()
    if stage == "central":
        stage_central(d)
    elif stage == "cont":
        stage_cont(d)
    elif stage == "shock":
        stage_shock(d)
    elif stage.startswith("seedc:"):
        stage_seed(d, int(stage.split(":")[1]), "cont")
    elif stage.startswith("seedk:"):
        stage_seed(d, int(stage.split(":")[1]), "shock")
    elif stage == "seed42":
        # seed 42 already implicit in cont/shock stages; record from defaults
        d.setdefault("seeds", {})["42"] = {
            "cont_z": d["cont"]["pair"]["z_star"], "cont_batches": d["cont"]["pair"]["final_recommendation"],
            "cont_margin": d["cont"]["pair"]["decision_margin_pct"], "cont_zpct": d["cont"]["pair"]["z_pct"],
            "shock_z": d["shock"]["pair"]["z_star"], "shock_batches": d["shock"]["pair"]["final_recommendation"],
            "shock_margin": d["shock"]["pair"]["decision_margin_pct"], "shock_zpct": d["shock"]["pair"]["z_pct"]}
        print("seed42 recorded from cont/shock stages")
    elif stage == "dump":
        print(json.dumps(d, indent=2))
        return
    save(d)


if __name__ == "__main__":
    main()
