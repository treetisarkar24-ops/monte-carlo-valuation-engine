"""
Consolidate the authoritative MSFT pipeline snapshot from local caches.

The shared msft_results.json was being clobbered by a concurrent writer. This
script rebuilds every stage deterministically from THIS session's own simulation
caches (cont/shock/seed _v2 dirs), in a single process, and writes a private
msft_report_data.json. Cached draws are bit-identical to live runs (engine is
seeded), so the convergence/production/benchmark numbers equal a clean run.
Only the 5000-sim channel diagnostic is recomputed live (fast, seed 42).
No engine/convergence/grid/shock-calibration logic is modified.
"""

# --- engine path bootstrap (auto-added during reorg; frozen engine lives in ../engine) ---
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "engine"))
# --- end bootstrap ---
import os, json
import numpy as np

from dcf import DCFInputs, run_dcf, compute_wacc
from mc_config import MCConfig
from mc_engine import run_monte_carlo, summarize, text_histogram
from mc_shocks import run_monte_carlo_with_shocks, sample_inputs_with_shocks
from mc_convergence import convergence_with_recommendation
import mc_defaults

SEED = 42
base = DCFInputs(**json.load(open("msft_fixture.json")))


def make_memo(cache, engine):
    def memo(b, cfg):
        path = os.path.join(cache, f"{cfg.n_simulations}_{cfg.random_seed}.npy")
        if os.path.exists(path):
            return np.load(path)
        res = np.asarray(engine(b, cfg))
        np.save(path, res)
        return res
    return memo


def summ_dict(s):
    return {"n": s.n, "mean": s.mean, "median": s.median, "std": s.std,
            "min": s.minimum, "max": s.maximum,
            "pct": {str(k): v for k, v in s.percentiles.items()}}


def pair_dict(p):
    d = p.default
    return {"z_star": p.z_star, "adequately_resolved": p.adequately_resolved,
            "final_recommendation": p.final_recommendation,
            "z_pct": d.z_pct, "z_elbow": d.z_elbow,
            "decision_margin_pct": d.decision_margin_pct,
            "precision_bar": d.precision_bar, "sigma_estimate": d.sigma_estimate,
            "center_mean": float(np.mean(d.center)), "borderline": d.borderline,
            "batches_used": d.batches_used, "batches_recommended": d.batches_recommended,
            "scatter": d.scatter, "n_grid": d.n_grid}


out = {}
out["central"] = {"value": run_dcf(base), "wacc": compute_wacc(base)}

# ---- continuous ----
cmemo = make_memo("msft_cont_cache_v2", run_monte_carlo)
cont = convergence_with_recommendation(base, rerun=False, runner=cmemo)
z = cont.z_star
cres = np.asarray(cmemo(base, MCConfig(n_simulations=z, random_seed=SEED)))
folk = np.asarray(cmemo(base, MCConfig(n_simulations=10000, random_seed=SEED)))
zs, fs = summarize(list(cres)), summarize(list(folk))
out["cont"] = {
    "pair": pair_dict(cont),
    "production": summ_dict(summarize(list(cres))),
    "frac_negative_pct": float(100.0 * np.mean(cres < 0)),
    "histogram": text_histogram(list(cres), bins=20, width=42),
    "benchmark": {"z_star": z, "folk_n": 10000, "compute_ratio": z / 10000.0,
                  "mean_gap_pct": abs(zs.mean - fs.mean) / fs.mean * 100.0,
                  "z_mean": zs.mean, "folk_mean": fs.mean,
                  "z_median": zs.median, "folk_median": fs.median},
}

# ---- shocked ----
smemo = make_memo("msft_shock_cache_v2", run_monte_carlo_with_shocks)
shock = convergence_with_recommendation(base, rerun=False, runner=smemo)
zz = shock.z_star
sres = np.asarray(smemo(base, MCConfig(n_simulations=zz, random_seed=SEED)))
# channel diagnostics (5000-sim apparatus, seed 42) — recomputed live
cfg = MCConfig(n_simulations=5000, random_seed=SEED)
rng = np.random.default_rng(cfg.random_seed)
rows = [(lambda oc: (run_dcf(oc.inputs), oc))(sample_inputs_with_shocks(base, cfg, rng, enabled=True))
        for _ in range(cfg.n_simulations)]
fires = {ch: 0 for ch in mc_defaults.SHOCK_CHANNELS}
stresses = []
for _, oc in rows:
    stresses.append(oc.final_stress)
    for ev in oc.events:
        fires[ev.channel] += 1
any_paths = sum(1 for _, oc in rows if oc.events)
worst = sorted(rows, key=lambda r: r[0])[: max(1, len(rows) // 20)]
wfires = {ch: 0 for ch in mc_defaults.SHOCK_CHANNELS}
for _, oc in worst:
    for ev in oc.events:
        wfires[ev.channel] += 1
# market grid keyed at realistic MSFT prices plus the zero floor
price_pts = [0, 50, 100, 150, 200, 263, 300, 400, 450, 500]
grid = {str(p): float(100.0 * np.mean(sres < p)) for p in price_pts}
out["shock"] = {
    "pair": pair_dict(shock),
    "production": summ_dict(summarize(list(sres))),
    "frac_negative_pct": float(100.0 * np.mean(sres < 0)),
    "histogram": text_histogram(list(sres), bins=20, width=42),
    "shock_free_pct": float(100.0 * (1 - any_paths / len(rows))),
    "fires_all": fires, "fires_worst5": wfires,
    "mean_stress": float(np.mean(stresses)), "max_stress": float(np.max(stresses)),
    "total_fires": int(sum(fires.values())), "market_grid": grid,
}

# ---- seed robustness ----
seeds = {"42": {"cont_z": cont.z_star, "cont_batches": cont.final_recommendation,
                "cont_margin": cont.default.decision_margin_pct, "cont_zpct": cont.default.z_pct,
                "shock_z": shock.z_star, "shock_batches": shock.final_recommendation,
                "shock_margin": shock.default.decision_margin_pct, "shock_zpct": shock.default.z_pct}}
for s in (99, 123, 7):
    cfgs = MCConfig(n_simulations=0, random_seed=s)
    cm = make_memo(f"msft_seed_cache_v2/cont_{s}", run_monte_carlo)
    km = make_memo(f"msft_seed_cache_v2/shock_{s}", run_monte_carlo_with_shocks)
    c = convergence_with_recommendation(base, config=cfgs, rerun=False, runner=cm)
    k = convergence_with_recommendation(base, config=cfgs, rerun=False, runner=km)
    seeds[str(s)] = {"cont_z": c.z_star, "cont_batches": c.final_recommendation,
                     "cont_margin": c.default.decision_margin_pct, "cont_zpct": c.default.z_pct,
                     "shock_z": k.z_star, "shock_batches": k.final_recommendation,
                     "shock_margin": k.default.decision_margin_pct, "shock_zpct": k.default.z_pct}
out["seeds"] = seeds

json.dump(out, open("msft_report_data.json", "w"), indent=2)
print("WROTE msft_report_data.json")
print("central:", round(out["central"]["value"], 2), "wacc:", round(out["central"]["wacc"], 4))
print("cont  z*=", cont.z_star, "margin%=", round(cont.default.decision_margin_pct, 1),
      "frac_neg=", out["cont"]["frac_negative_pct"])
print("shock z**=", shock.z_star, "margin%=", round(shock.default.decision_margin_pct, 1),
      "shock_free=", round(out["shock"]["shock_free_pct"], 1))
print("seeds:", {s: (v["cont_z"], v["shock_z"]) for s, v in seeds.items()})
