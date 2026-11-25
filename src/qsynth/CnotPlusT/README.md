# CnotPlusT (sandbox)

This is a working copy of [`qsynth.CnotSynthesis`](../CnotSynthesis) forked for experimentation. 
The package is self-contained. Imports of genuinely shared infrastructure
(`qsynth.Utilities`, `qsynth.LayoutSynthesis`, `qsynth.CliffordSynthesis`,
`qsynth.ReachabilitySolver`) still point at the original modules.

## Running it
```bash
python Scripts/cnotplust_run.py Benchmarks/CNOT-slices/tof_3/tof_3_slice_1.qasm --check
```
check diff with
```bash
diff -ru src/qsynth/CnotSynthesis src/qsynth/CnotPlusT
```