# Sophus Corry

import numpy as np
from qiskit import QuantumCircuit

def goal_x_and_z(matrix, matrix_predicate, pddl_lines, index_increment, num_qubits):
    for row_id in range(num_qubits):
        row_line = ""
        for column_id in range(num_qubits):
            cell = matrix[row_id][column_id]
            if cell == True:
                row_line += (
                    "     ("
                    + matrix_predicate
                    + f" q{index_increment+row_id} q{column_id}) "
                )
            else:
                assert cell == False
                row_line += (
                    "(not ("
                    + matrix_predicate
                    + f" q{index_increment+row_id} q{column_id}))"
                )
        pddl_lines.append(f" {row_line}\n")
    # Here I should actually print the parities as well
    return pddl_lines


def generate_problem_specification(clifford_matrix, options, num_qubits):
    pddl_lines = []
    pddl_lines.append("(define (problem instance)\n")
    pddl_lines.append("  (:domain Cnot-Synthesis)\n")
    pddl_lines.append("  (:objects")
    # generating objects for rows/columns:
    qubits = ""
    for i in range(num_qubits):
        qubits += f"q{i} "
    pddl_lines.append(f"  {qubits}- qubit)\n")

    pddl_lines.append("(:init\n")
    # identity matrix:
    cells = "\n;; Identity matrix\n"
    for i in range(num_qubits):
        cells += f"(X q{i} q{i})\n"
    pddl_lines.append(cells)

    # If coupling graph is given then we add it to the initial state:
    if options.coupling_graph:
        for edge in options.coupling_graph:
            pddl_lines.append(f"  (connected q{edge[0]} q{edge[1]})\n")
    pddl_lines.append(")\n")

    pddl_lines.append("(:goal\n")

    # Destabilizer goal matrices:
    pddl_lines.append("  (and\n   ;; target destabilizer X matrix\n")
    pddl_lines = goal_x_and_z(clifford_matrix.destab_x, "X", pddl_lines, 0, num_qubits)
    pddl_lines.append("  )\n)\n)")
    #Or maybe I should put it here
    return pddl_lines



def get_circuit_converted_to_cnot_T(circuit):
    """
    Takes a circuit with all gates in { CNOT,  SWAP, T, Tdg} and returns an equivalent CNOT+Rz circuit.
    """
    new_qc = QuantumCircuit(circuit.num_qubits, circuit.num_clbits)

    for instr, qargs, cargs in circuit.data:
        name = instr.name
        qubits = [circuit.find_bit(q).index for q in qargs]

        if name == "cx":
            new_qc.cx(*qubits)
        elif name == "swap":
            new_qc.swap(*qubits)
        elif name == "t":
            new_qc.rz(np.pi / 4, qubits[0])
        elif name == "tdg":
            new_qc.rz(-np.pi / 4, qubits[0])
        else:
            raise ValueError(f"Unsupported gate: {name}")
    return new_qc


def get_goal_matrix_and_phase_polynomial_from_cnot_rz_circuit(circuit):
    """
    Returns:
        goal_matrix as a numpy array
        phase_polynomial as a dictionary from state vectors (tuples of ints) to phases (modulo 2π)
    """
    circuit = get_circuit_converted_to_cnot_T(circuit)
    goal_matrix = np.eye(circuit.num_qubits, dtype=int)
    phase_polynomial = {}

    for instr in circuit.data:
        if instr.name == "cx":
            ctrl, trg = [circuit.find_bit(q).index for q in instr.qubits]
            goal_matrix[:, trg] = (goal_matrix[:, trg] + goal_matrix[:, ctrl]) % 2
        elif instr.name == "swap":
            i, j = [circuit.find_bit(q).index for q in instr.qubits]
            goal_matrix[:, [i, j]] = goal_matrix[:, [j, i]]
        elif instr.name == "rz":
            theta = instr.params[0]
            q = circuit.find_bit(instr.qubits[0]).index
            state_vector = tuple(goal_matrix[:, q])
            old_coeff = phase_polynomial.get(state_vector, 0)
            phase_polynomial[state_vector] = old_coeff + theta
        else:
            raise ValueError(f"Unsupported gate: {instr.name}")

        # Simplify phase polynomial by taking coefficients modulo 2π and leaving out coefficients of 0
        phase_polynomial = {
            k: (v % (2 * np.pi))
            for k, v in phase_polynomial.items()
            if not np.isclose(v % (2 * np.pi), 0)
        }
    return goal_matrix, phase_polynomial
