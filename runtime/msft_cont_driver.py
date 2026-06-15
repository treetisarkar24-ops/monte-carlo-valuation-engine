"""
Chunked, resumable driver for the MSFT continuous stage.

Reproduces case_study_runner.stage_cont EXACTLY (same convergence sweep at the
default seed, same production run at z*, same folk-n benchmark, same histogram
and frac-negative), but injects a disk-memoizing wrapper around run_monte_carlo
through the convergence module's `runner` seam so it completes within the per-call
wall limit. Memo keys on (n_simulations, random_seed); the engine is seeded, so
every cached list is identical to the real runner's. No engine/convergence/grid
logic is modified.
"""

# --- engine path bootstrap (auto-added during reorg; frozen engine lives in ../engine) ---
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "engine"))
# --- end bootstrap ---
import os, sys, time
import numpy as np

from mc_config import MCConfig
from mc_engine import run_monte_carlo, summarize, text_histogram
from mc_convergence import convergence_with_recommendation, benchmark_against_folk
from case_study_runner import get_base, load, save, summ_dict, pair_dict, SEED

CACHE = "msft_cont_cache_v2"
os.makedirs(CACHE, exist_ok=True)
BUDGET = float(sys.argv[1]) if len(sys.argv) > 1 else 40.0
START = time.time()


def memo(base, cfg):
    key = f"{cfg.n_simulations}_{cfg.random_seed}.npy"
    path = os.path.join(CACHE, key)
    if os.path.exists(path):
        return np.load(path)
    if time.time() - START > BUDGET:
        raise TimeoutError("budget exhausted; resume next call")
    res = np.asarray(run_monte_carlo(base, cfg))
    np.save(path, res)
    return res


def main():
    base = get_base("msft")
    try:
        cont = convergence_with_recommendation(base, rerun=False, runner=memo)
        z = cont.z_star
        res = memo(base, MCConfig(n_simulations=z, random_seed=SEED))
        # benchmark: production at z vs folk_n=10000, same seed
        zres = res
        folk = memo(base, MCConfig(n_simulations=10000, random_seed=SEED))
    except TimeoutError as e:
        print("PARTIAL:", e, "cached:", len(os.listdir(CACHE)))
        return

    arr = np.asarray(res)
    zs = summarize(list(np.asarray(zres)))
    fs = summarize(list(np.asarray(folk)))
    d = load("msft")
    d["cont"] = {
        "pair": pair_dict(cont),
        "production": summ_dict(summarize(list(arr))),
        "frac_negative_pct": float(100.0 * np.mean(arr < 0)),
        "histogram": text_histogram(list(arr), bins=20, width=42),
        "benchmark": {
            "z_star": z, "folk_n": 10000,
            "compute_ratio": z / 10000.0,
            "mean_gap_pct": abs(zs.mean - fs.mean) / fs.mean * 100.0,
            "z_mean": zs.mean, "folk_mean": fs.mean,
            "z_median": zs.median, "folk_median": fs.median,
        },
    }
    save("msft", d)
    print(f"DONE cont z*={z} z_pct={cont.default.z_pct} z_elbow={cont.default.z_elbow} "
          f"margin%={cont.default.decision_margin_pct:.2f} batches_used={cont.default.batches_used} "
          f"frac_neg={d['cont']['frac_negative_pct']:.1f}%")


if __name__ == "__main__":
    main()
