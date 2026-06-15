"""
Chunked shock driver for NVIDIA (nvda) case study.

Mirrors msft_shock_driver.py exactly — same memoising + resumable pattern,
same channel-diagnostics apparatus. Swap slug to "nvda" and cache dir to
"nvda_shock_cache". Run repeatedly until DONE appears.
"""

# --- engine path bootstrap (auto-added during reorg; frozen engine lives in ../engine) ---
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "engine"))
# --- end bootstrap ---
import os, sys, time, json
import numpy as np

from dcf import DCFInputs, run_dcf
from mc_config import MCConfig
from mc_engine import summarize, text_histogram
from mc_shocks import run_monte_carlo_with_shocks, sample_inputs_with_shocks
from mc_convergence import convergence_with_recommendation
import mc_defaults
from case_study_runner import get_base, load, save, summ_dict, pair_dict, SEED

CACHE = "nvda_shock_cache"
os.makedirs(CACHE, exist_ok=True)
BUDGET = float(sys.argv[1]) if len(sys.argv) > 1 else 40.0
START = time.time()


def memo_runner(base, cfg):
    key = f"{cfg.n_simulations}_{cfg.random_seed}.npy"
    path = os.path.join(CACHE, key)
    if os.path.exists(path):
        return np.load(path)
    if time.time() - START > BUDGET:
        raise TimeoutError("budget exhausted; resume in next call")
    res = np.asarray(run_monte_carlo_with_shocks(base, cfg))
    np.save(path, res)
    return res


def main():
    slug = "nvda"
    base = get_base(slug)
    d = load(slug)

    try:
        shock = convergence_with_recommendation(
            base, rerun=False, runner=memo_runner
        )
    except TimeoutError as e:
        print("PARTIAL:", e, "cached files:", len(os.listdir(CACHE)))
        return

    z = shock.z_star
    res = memo_runner(base, MCConfig(n_simulations=z, random_seed=SEED))
    arr = np.asarray(res)

    cfg = MCConfig(n_simulations=5000, random_seed=SEED)
    rng = np.random.default_rng(cfg.random_seed)
    rows = []
    for _ in range(cfg.n_simulations):
        oc = sample_inputs_with_shocks(base, cfg, rng, enabled=True)
        rows.append((run_dcf(oc.inputs), oc))
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
    grid = {str(p): float(100.0 * np.mean(arr < p)) for p in (-5, -2, 0, 2, 5, 8, 11, 15)}

    d["shock"] = {
        "pair": pair_dict(shock),
        "production": summ_dict(summarize(list(arr))),
        "frac_negative_pct": float(100.0 * np.mean(arr < 0)),
        "histogram": text_histogram(list(arr), bins=20, width=42),
        "shock_free_pct": float(100.0 * (1 - any_paths / len(rows))),
        "fires_all": fires, "fires_worst5": wfires,
        "mean_stress": float(np.mean(stresses)), "max_stress": float(np.max(stresses)),
        "total_fires": int(sum(fires.values())), "market_grid": grid,
    }
    save(slug, d)
    print(f"DONE shock z**={z} margin%={shock.default.decision_margin_pct:.2f} "
          f"z_pct={shock.default.z_pct} frac_neg={d['shock']['frac_negative_pct']:.1f}% "
          f"shock_free={d['shock']['shock_free_pct']:.1f}%")


if __name__ == "__main__":
    main()
