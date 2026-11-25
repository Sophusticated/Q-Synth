#! /usr/bin/env python3

# It calls the sandbox's synthesis code directly, bypassing qsynth/api.py and
# the q-synth.py CLI entirely, so you can edit anything under
# src/qsynth/CnotPlusT/ and immediately see the effect without wiring it into
# the rest of the project.
#
# Usage:
#   python Scripts/cnotplust_run.py INPUT.qasm [--minimize cx-count|cx-depth] [--model sat|qbf] [--check]
#
# Example:
#   python Scripts/cnotplust_run.py Benchmarks/CNOT-slices/tof_3/tof_3_slice_1.qasm --check

import argparse

from qsynth.CnotPlusT.cnot_synthesis import cnot_optimization_from_file


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", metavar="INPUT.qasm", help="input CNOT circuit file")
    parser.add_argument(
        "--minimize",
        default="cx-count",
        choices=("cx-count", "cx-depth"),
        help="metric to minimize (default: cx-count)",
    )
    parser.add_argument(
        "--model",
        default="sat",
        choices=("sat", "qbf"),
        help="encoding to use: 'sat' -> lifted/grounded SAT, 'qbf' -> lifted QBF (default: sat)",
    )
    parser.add_argument("--time", type=float, default=600, help="solver time limit in seconds (default: 600)")
    parser.add_argument("--check", action="store_true", help="verify output circuit is equivalent to the input")
    parser.add_argument("-v", "--verbose", type=int, default=2, help="verbosity level (default: 2)")
    args = parser.parse_args()

    result = cnot_optimization_from_file(
        circuit_in=args.input,
        encoding="lifted",
        time=args.time,
        minimization=args.minimize,
        verbose=args.verbose,
    )

    print()
    if result is None or result.circuit is None:
        print("No result (timed out or no plan found).")
        return

    print("Resulting circuit:")
    print(result.circuit)
    print(f"timed_out={result.timed_out}  no_plan_found={result.no_plan_found}")


if __name__ == "__main__":
    main()
