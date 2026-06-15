"""
MSFT-specific pipeline runner — identical logic to case_study_runner.py
but uses batches=20 for every convergence sweep (fits the 45-second shell
timeout; the 40-batch default requires ~73s for a 7-year forecast).

Usage:
    python3 msft_runner.py <stage>

Stages: central  cont  shock_conv  shock_prod  seed42
        seedc99 seedk99 seedc123 seedk123 seedc7 seedk7 dump
"""

# --- engine path bootstrap (auto-added during reorg; frozen engine lives in ../engine) ---
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "engine"))
# --- end bootstrap ---

import sys, json, time
import numpy as np

from dcf import DCFInputs, run_dcf, compute_wacc
from mc_config import MCConfig
from mc_engine import run_monte_carlo, summarize, text_histogram
from mc_shocks import run_monte_carlo_with_shocks, sample_inputs_with_shocks
from mc_convergence import (
    convergence_with_recommendation,
    convergence_with_shocks,
    benchmark_against_folk,
)
import mc_defaults

SLUG           = "amazon"
SEED           = 42
BATCHES        = 20   # cont sweeps — fits 45s limit for 7-year MSFT
BATCHES_SEEDK  = 12   # shock seed sweeps — shocked engine is heavier; 12 fits comfortably

def load_fixture():
    with open("amazon_fixture.json") as f:
        return DCFInputs(**json.load(f))

def results_path(): return f"{SLUG}_results.json"
def load():
    try:
        with open(results_path()) as f: return json.load(f)
    except FileNotFoundError: return {}
def save(d):
    with open(results_path(), "w") as f: json.dump(d, f, indent=2)

def summ_dict(s):
    return {"n": s.n, "mean": s.mean, "median": s.median, "std": s.std,
            "min": s.minimum, "max": s.maximum,
            "pct": {str(k): v for k, v in s.percentiles.items()}}

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

# ── Stages ────────────────────────────────────────────────────────────────────

def stage_central(d, base):
    d["central"] = {"value": run_dcf(base), "wacc": compute_wacc(base)}
    print("central:", d["central"])

def stage_cont(d, base):
    t = time.time()
    cont = convergence_with_recommendation(base, rerun=False, batches=BATCHES)
    z = cont.z_star
    res  = run_monte_carlo(base, MCConfig(n_simulations=z, random_seed=SEED))
    arr   = np.asarray(res)
    bench = benchmark_against_folk(base, cont, folk_n=10_000, seed=SEED)
    d["cont"] = {
        "pair": pair_dict(cont),
        "production": summ_dict(summarize(res)),
        "frac_negative_pct": float(100.0 * np.mean(arr < 0)),
        "histogram": text_histogram(res, bins=20, width=42),
        "benchmark": {
            "z_star": bench.z_star, "folk_n": bench.folk_n,
            "compute_ratio": bench.compute_ratio, "mean_gap_pct": bench.mean_gap_pct,
            "z_mean": bench.z_summary.mean, "folk_mean": bench.folk_summary.mean,
            "z_median": bench.z_summary.median, "folk_median": bench.folk_summary.median,
        },
        "batches_used": BATCHES,
        "secs": time.time() - t,
    }
    print(f"cont z*={z}  margin%={cont.default.decision_margin_pct:.2f}  "
          f"z_pct={cont.default.z_pct}  z_elbow={cont.default.z_elbow}  "
          f"frac_neg={d['cont']['frac_negative_pct']:.1f}%  "
          f"in {d['cont']['secs']:.1f}s")

def stage_shock_conv(d, base):
    """Convergence sweep only — ~43s for 7-year MSFT with batches=20."""
    t = time.time()
    shock = convergence_with_shocks(base, rerun=False, batches=BATCHES)
    d.setdefault("shock", {})["pair"] = pair_dict(shock)
    d["shock"]["batches_used"] = BATCHES
    d["shock"]["conv_secs"] = time.time() - t
    print(f"shock_conv z**={shock.z_star}  margin%={shock.default.decision_margin_pct:.2f}  "
          f"z_pct={shock.default.z_pct}  z_elbow={shock.default.z_elbow}  "
          f"in {d['shock']['conv_secs']:.1f}s")

def stage_shock_prod(d, base):
    """Production MC + channel diagnostics — uses z** from shock_conv."""
    t = time.time()
    z = d["shock"]["pair"]["z_star"]
    res = run_monte_carlo_with_shocks(base, MCConfig(n_simulations=z, random_seed=SEED))
    arr = np.asarray(res)
    cfg = MCConfig(n_simulations=5000, random_seed=SEED)
    rng = np.random.default_rng(cfg.random_seed)
    rows = []
    for _ in range(cfg.n_simulations):
        oc = sample_inputs_with_shocks(base, cfg, rng, enabled=True)
        rows.append((run_dcf(oc.inputs), oc))
    fires  = {ch: 0 for ch in mc_defaults.SHOCK_CHANNELS}
    stresses = []
    for _, oc in rows:
        stresses.append(oc.final_stress)
        for ev in oc.events: fires[ev.channel] += 1
    any_paths = sum(1 for _, oc in rows if oc.events)
    worst  = sorted(rows, key=lambda r: r[0])[: max(1, len(rows) // 20)]
    wfires = {ch: 0 for ch in mc_defaults.SHOCK_CHANNELS}
    for _, oc in worst:
        for ev in oc.events: wfires[ev.channel] += 1
    grid = {str(p): float(100.0 * np.mean(arr < p))
            for p in (-5, -2, 0, 2, 5, 8, 11, 15, 200, 263, 390)}
    d["shock"].update({
        "production": summ_dict(summarize(res)),
        "frac_negative_pct": float(100.0 * np.mean(arr < 0)),
        "histogram": text_histogram(res, bins=20, width=42),
        "shock_free_pct": float(100.0 * (1 - any_paths / len(rows))),
        "fires_all": fires, "fires_worst5": wfires,
        "mean_stress": float(np.mean(stresses)), "max_stress": float(np.max(stresses)),
        "total_fires": int(sum(fires.values())),
        "market_grid": grid,
        "prod_secs": time.time() - t,
    })
    print(f"shock_prod z**={z}  frac_neg={d['shock']['frac_negative_pct']:.1f}%  "
          f"shock_free={d['shock']['shock_free_pct']:.1f}%  in {d['shock']['prod_secs']:.1f}s")

def stage_seed42(d):
    d.setdefault("seeds", {})["42"] = {
        "cont_z":      d["cont"]["pair"]["z_star"],
        "cont_batches":d["cont"]["pair"]["final_recommendation"],
        "cont_margin": d["cont"]["pair"]["decision_margin_pct"],
        "cont_zpct":   d["cont"]["pair"]["z_pct"],
        "shock_z":     d["shock"]["pair"]["z_star"],
        "shock_batches":d["shock"]["pair"]["final_recommendation"],
        "shock_margin":d["shock"]["pair"]["decision_margin_pct"],
        "shock_zpct":  d["shock"]["pair"]["z_pct"],
    }
    print("seed42 recorded from cont/shock stages")

def stage_seed(d, base, seed, which):
    t = time.time()
    cfg = MCConfig(n_simulations=0, random_seed=seed)
    rec = d.setdefault("seeds", {}).setdefault(str(seed), {})
    if which == "cont":
        c = convergence_with_recommendation(base, config=cfg, rerun=False, batches=BATCHES)
        rec.update(cont_z=c.z_star, cont_batches=c.final_recommendation,
                   cont_margin=c.default.decision_margin_pct, cont_zpct=c.default.z_pct,
                   cont_batches_used=BATCHES)
        print(f"seed {seed} cont z*={c.z_star}  margin={c.default.decision_margin_pct:.1f}  "
              f"in {time.time()-t:.1f}s")
    else:
        s = convergence_with_shocks(base, config=cfg, rerun=False, batches=BATCHES_SEEDK)
        rec.update(shock_z=s.z_star, shock_batches=s.final_recommendation,
                   shock_margin=s.default.decision_margin_pct, shock_zpct=s.default.z_pct,
                   shock_batches_used=BATCHES_SEEDK)
        print(f"seed {seed} shock z**={s.z_star}  margin={s.default.decision_margin_pct:.1f}  "
              f"in {time.time()-t:.1f}s")

# ── Dispatch ──────────────────────────────────────────────────────────────────

def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else "dump"
    d    = load()
    base = load_fixture()

    if stage == "central":      stage_central(d, base)
    elif stage == "cont":       stage_cont(d, base)
    elif stage == "shock_conv": stage_shock_conv(d, base)
    elif stage == "shock_prod": stage_shock_prod(d, base)
    elif stage == "seed42":     stage_seed42(d)
    elif stage == "seedc99": stage_seed(d, base, 99, "cont")
    elif stage == "seedk99": stage_seed(d, base, 99, "shock")
    elif stage == "seedc123":stage_seed(d, base, 123, "cont")
    elif stage == "seedk123":stage_seed(d, base, 123, "shock")
    elif stage == "seedc7":  stage_seed(d, base, 7, "cont")
    elif stage == "seedk7":  stage_seed(d, base, 7, "shock")
    elif stage == "dump":    print(json.dumps(d, indent=2)); return
    else: raise SystemExit(f"unknown stage '{stage}'")

    save(d)

if __name__ == "__main__":
    main()
