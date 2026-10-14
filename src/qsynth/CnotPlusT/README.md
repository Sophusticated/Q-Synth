# CnotPlusT (sandbox)

This is a working copy of [`qsynth.CnotSynthesis`](../CnotSynthesis) forked for
experimentation. It is not wired into `qsynth/api.py` or the `q-synth.py` CLI —
edit it freely without touching shared code paths.

Everything here started as a byte-for-byte copy; only the internal
self-imports were rewritten from `qsynth.CnotSynthesis.*` to `qsynth.CnotPlusT.*`
so the package is self-contained. Imports of genuinely shared infrastructure
(`qsynth.Utilities`, `qsynth.LayoutSynthesis`, `qsynth.CliffordSynthesis`,
`qsynth.ReachabilitySolver`) still point at the original modules.

## Running it

Use the standalone runner instead of the CLI:

```bash
python Scripts/cnotplust_run.py Benchmarks/CNOT-slices/tof_3/tof_3_slice_1.qasm --check
```

It calls `cnot_optimization_from_file` in `cnot_synthesis_sat_qbf.py` directly.
See that script's `--help` for options (`--minimize`, `--model`, `--time`, `-v`).

## Comparing against the original

Since this started as an exact copy, diff against the source anytime to see
what you've changed:

```bash
diff -ru src/qsynth/CnotSynthesis src/qsynth/CnotPlusT
```

## Next steps, if useful later

- To also make it selectable from the real CLI (`./q-synth.py cnot -m ...`),
  add a branch in `src/qsynth/Synthesizers/cnot_synthesizer.py` and a matching
  option in `src/qsynth/Synthesizers/configs.py`.
- To unit-test it the way the original is tested, see
  `Tests/cnot_synthesis_test.py` for the pattern (it calls `qsynth.api`
  functions directly) — a parallel test file could import from
  `qsynth.CnotPlusT` instead.
