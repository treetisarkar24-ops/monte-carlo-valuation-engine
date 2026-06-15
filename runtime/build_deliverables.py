#!/usr/bin/env python3
"""
build_deliverables.py — one command, three files.

Runs the full presentation layer over a single (results.json, meta.json) pair and
emits the three-tier deliverable set:

    <Name>_Valuation_Report.pdf   primary  — for ~95% of readers
    <Name>_Output.xlsx            support  — power users who want the numbers live
    Candidate_<TICKER>_<Name>.md  diagnostics — full technical detail

This is a thin ORCHESTRATOR. It does not compute anything itself: it shells out to
the three existing generators (generate_report.py, build_pdf_report.py,
build_excel_output.py), each of which reads the engine's output JSON. Nothing here
imports or modifies any DCF / Monte Carlo / shock / convergence logic — the engine
stays frozen; this only packages what the engine already produced.

Usage:
    python3 build_deliverables.py amazon_results.json amazon_meta.json
    python3 build_deliverables.py amazon_results.json amazon_meta.json -d deliverables/
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _slug(meta):
    """Derive (name, ticker) from meta.json for naming the output files.

    Prefers an explicit `short_name` (e.g. "Amazon"); otherwise falls back to the
    full `company`, with runs of non-alphanumerics collapsed to a single
    underscore so "Amazon.com, Inc." -> "Amazon_com_Inc" rather than
    "Amazon_com__Inc".
    """
    raw = str(meta.get("short_name") or meta.get("company", "Company")).strip()
    ticker = str(meta.get("ticker", "TICKER")).strip()
    out, prev_us = [], False
    for c in raw:
        if c.isalnum():
            out.append(c)
            prev_us = False
        elif not prev_us:
            out.append("_")
            prev_us = True
    safe = "".join(out).strip("_")
    return safe or "Company", ticker or "TICKER"


def _run(script, results, meta_path, out):
    """Invoke one generator; return (ok, message)."""
    path = os.path.join(HERE, script)
    if not os.path.exists(path):
        return False, f"generator not found: {script}"
    cmd = [sys.executable, path, results, meta_path, "-o", out]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return False, (proc.stderr or proc.stdout or "unknown error").strip()
    return True, out


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Emit the PDF + Excel + Markdown deliverable trio from one results/meta pair."
    )
    ap.add_argument("results", help="engine output, e.g. amazon_results.json")
    ap.add_argument("meta", help="case-study meta, e.g. amazon_meta.json")
    ap.add_argument("-d", "--dir", default=".", help="output directory (default: current)")
    args = ap.parse_args(argv)

    with open(args.meta) as f:
        meta = json.load(f)
    name, ticker = _slug(meta)
    os.makedirs(args.dir, exist_ok=True)

    jobs = [
        ("PDF (primary)", "build_pdf_report.py",
         os.path.join(args.dir, f"{name}_Valuation_Report.pdf")),
        ("Excel (support)", "build_excel_output.py",
         os.path.join(args.dir, f"{name}_Output.xlsx")),
        ("Markdown (diagnostics)", "generate_report.py",
         os.path.join(args.dir, f"Candidate_{ticker}_{name}.md")),
    ]

    results = []
    for label, script, out in jobs:
        ok, msg = _run(script, args.results, args.meta, out)
        results.append((label, ok, msg))
        mark = "ok " if ok else "FAIL"
        print(f"[{mark}] {label:24s} -> {msg}")

    failed = [r for r in results if not r[1]]
    if failed:
        print(f"\n{len(failed)} of {len(jobs)} generators failed.", file=sys.stderr)
        return 1
    print(f"\nAll three deliverables written to {os.path.abspath(args.dir)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
