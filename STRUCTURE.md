# Project MC — folder map

Reorganised 2026-06-14. The valuation engine is unchanged; only the file layout
moved. The six core modules in `engine/` are byte-for-byte identical to before.

```
engine/        Frozen, validated core. dcf, mc_engine, mc_convergence,
               mc_shocks, mc_defaults, mc_config. Do not edit.
runtime/       Everything that drives the engine: excel_loader, the *_runner
               and *_driver scripts, the build_* renderers, case_study_runner,
               and the company fixtures/results (*_fixture.json, *_results.json).
candidates/    Synthetic stress-test scripts, their *_results.json, and the
               Candidate_*.md write-ups (Carvana … ThinEquity, Steady Co).
tests/         Self-checks: mc_smoke_test, mc_shocks_smoke_test, sanity_check,
               textbook_verification. All five pass.
case_studies/  Real-company deliverables: MSFT / AMZN / NVIDIA write-ups + PDFs.
outputs/       Production deliverables (Amazon_Output.xlsx, Amazon report PDF).
templates/     Input templates + loader example fixtures (MC_Input_Template*,
               input_template.json, ko_fixture.json, filled_ko_typed.xlsx).
website/       WEBSITE_BRIEF Monte Carlo.md + assets/ (convergence chart PNGs).
docs/          README is at root; the rest of the docs live here (HANDOFF,
               WORKFLOW, DCF_ASSUMPTIONS, CLOSURE_REVIEW, STRESS_TEST_TRACKER…).
_archive/      Superseded files kept for safety + MANIFEST_before_reorg.txt.
```

## How separated folders still import the frozen engine
Every script imports the engine with flat imports (`from dcf import …`). To keep
that working without editing the frozen core, each consumer script in
`runtime/`, `candidates/`, and `tests/` carries a 4-line bootstrap at the top
(tagged `engine path bootstrap`) that prepends `../engine` to `sys.path`.

## Running things
    cd tests    && python3 mc_smoke_test.py
    cd runtime  && python3 excel_loader.py ../templates/filled_ko_typed.xlsx --run
    cd runtime  && python3 msft_runner.py            # fixtures sit beside the runners

## Removed in the reorg (exact duplicates / junk)
STRESS_TEST_TRACKER copy.md, Candidate_AMZN_Amazon_com__Inc.md,
Amazon_com__Inc_Valuation_Report.pdf (all byte-identical dups), two empty log
files, a stale LibreOffice lock, .DS_Store, __pycache__.
`Amazon_com__Inc_Output.xlsx` and two scratch PNGs were moved to `_archive/`.

> Note: `WEBSITE_BRIEF Monte Carlo.md` was missing from disk at reorg time and
> was recovered intact into `website/` from the session transcript.
