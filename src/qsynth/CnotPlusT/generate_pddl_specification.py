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
    return pddl_lines


def theta_to_k(theta):
    """Converts a phase to its multiple of pi/4"""
    return round(theta / (np.pi / 4)) % 8


def goal_parities(phase_polynomial, num_qubits):
    """
    goal for the phase polynomial.

    Each distinct parity that accumulated a nonzero phase becomes a
    parity object. eg. (in pN qI) marks which qubits are in that parity, and (done pN) is
    the corresponding goal.
    The T action checks at search time whether a qubit's current column matches a parity's target,
    so this function only needs to emit the static 'in' facts.

    Returns:
        parity_names: PDDL object names, one per distinct rotation
        init_lines: '(in pN qI)' facts for :init
        goal_lines: '(done pN)' literals for :goal
        parity_thetas: from parity name to its accumulated phase, for the
            human-readable comment in :init
        parity_ks: from parity name to its phase as a multiple of pi/4 (mod 8),
            used for computing costs and decoding the circuit
    """
    parity_names = []
    init_lines = []
    goal_lines = []
    parity_thetas = {}
    parity_ks = {}
    init_lines.append("\n;; Static Parities:\n")
    for idx, (parity_vector, theta) in enumerate(phase_polynomial.items()):
        p_name = f"p{idx}"
        parity_names.append(p_name)
        parity_thetas[p_name] = theta
        parity_ks[p_name] = theta_to_k(theta)
        init_lines.append(f"; {p_name}: theta={theta}\n")
        for qubit_id in range(num_qubits):
            if parity_vector[qubit_id]:
                init_lines.append(f"(in {p_name} q{qubit_id})\n")
        goal_lines.append(f"(done {p_name})")
    return parity_names, init_lines, goal_lines, parity_thetas, parity_ks


def detect_triangles(phase_polynomial, parity_names, parity_ks, cs_cost, csdg_cost, cz_cost):
    """
    Finds triples of existing parities {a, b, c} with c = a XOR b, where resolving
    c's phase can be done in a single 2-qubit gate on the wires holding a and b. 

    Which gate that is depends only on c's k (mod 4):
        k mod 4 == 0: (skip)
        k mod 4 == 1: CSdg
        k mod 4 == 2: CZ
        k mod 4 == 3: CS
    a's and b's own k can be anything, and their cost is calculated.
    This price is added to the triangle's cost.

    Any given 3 parities hav 3 possible triangle values, all of which are checked

    Returns a dict {"cs": [...], "csdg": [...], "cz": [...]} where each entry is
    a list of (wire_a, wire_b, implicit, cost) tuples.
    """
    vector_of = {}
    name_of = {}
    for idx, parity_vector in enumerate(phase_polynomial.keys()):
        vector_of[parity_names[idx]] = parity_vector
        name_of[parity_vector] = parity_names[idx]

    gate_by_residue = {1: "csdg", 2: "cz", 3: "cs"}
    base_cost_of = {"cs": cs_cost, "csdg": csdg_cost, "cz": cz_cost}

    triangles = {"cs": [], "csdg": [], "cz": []}
    seen = set()

    for i in range(len(parity_names)):
        for j in range(i + 1, len(parity_names)):
            name_i, name_j = parity_names[i], parity_names[j]
            vec_xor = tuple(x ^ y for x, y in zip(vector_of[name_i], vector_of[name_j]))
            if vec_xor not in name_of:
                continue
            name_k = name_of[vec_xor]
            if name_k in (name_i, name_j):
                continue

            for wire_a, wire_b, implicit in (
                (name_i, name_j, name_k),
                (name_i, name_k, name_j),
                (name_j, name_k, name_i),
            ):
                key = (frozenset((wire_a, wire_b)), implicit)
                if key in seen:
                    continue
                seen.add(key)

                gate = gate_by_residue.get(parity_ks[implicit] % 4)
                if gate is None:
                    continue

                leftover_a = (parity_ks[wire_a] + parity_ks[implicit]) % 2
                leftover_b = (parity_ks[wire_b] + parity_ks[implicit]) % 2
                cost = base_cost_of[gate] + leftover_a + leftover_b
                triangles[gate].append((wire_a, wire_b, implicit, cost))

    return triangles


def generate_problem_specification(goal_matrix, phase_polynomial, options, num_qubits):
    pddl_lines = []
    pddl_lines.append("(define (problem instance)\n")
    pddl_lines.append("  (:domain CnotplusT-Synthesis)\n")

    parity_names, parity_init_lines, parity_goal_lines, parity_thetas, parity_ks = goal_parities(
        phase_polynomial, num_qubits
    )

    triangles = detect_triangles(
        phase_polynomial, parity_names, parity_ks,
        options.cs_cost, options.csdg_cost, options.cz_cost,
    )

    # generating objects for rows/columns and for parities:
    qubits = ""
    for i in range(num_qubits):
        qubits += f"q{i} "
    parity_decl = ""
    if parity_names:
        parity_decl = " " + "".join(f"{p} " for p in parity_names) + "- parity"
    pddl_lines.append(f"  (:objects  {qubits}- qubit{parity_decl})\n")

    pddl_lines.append("(:init\n")
    pddl_lines.append("  (= (total-cost) 0)\n")
    pddl_lines.append(f"  (= (cnot-cost) {options.cnot_cost})\n")
    # identity matrix:
    cells = "\n;; Identity matrix\n"
    for i in range(num_qubits):
        cells += f"(X q{i} q{i})\n"
    pddl_lines.append(cells)

    # If coupling graph is given then we add it to the initial state:
    if options.coupling_graph:
        for edge in options.coupling_graph:
            pddl_lines.append(f"  (connected q{edge[0]} q{edge[1]})\n")

    pddl_lines = pddl_lines + parity_init_lines

    # Per-parity T cost: a parity has an extra T cost, which is k mod 2 (since S and Z are free)
    pddl_lines.append("\n;; Per-parity T cost:\n")
    for p_name in parity_names:
        pddl_lines.append(f"(= (tcost {p_name}) {parity_ks[p_name] % 2})\n")

    # Triangle facts: parities {a, b, c=a^b} that can be resolved together by a
    # single 2-qubit gate on the wires holding a and b.
    pddl_lines.append("\n;; Triangles:\n")
    for gate, entries in triangles.items():
        for wire_a, wire_b, implicit, cost in entries:
            pddl_lines.append(f"({gate}-triangle {wire_a} {wire_b} {implicit})\n")
            pddl_lines.append(f"(= ({gate}-cost {wire_a} {wire_b} {implicit}) {cost})\n")

    pddl_lines.append(")\n")

    pddl_lines.append("(:goal\n")

    # Destabilizer goal matrix:
    pddl_lines.append("  (and\n   ;; target destabilizer X matrix\n")
    pddl_lines = goal_x_and_z(goal_matrix, "X", pddl_lines, 0, num_qubits)

    # Rotations (T/Tdg) that must have been applied:
    pddl_lines.append("   ;; rotations applied\n")
    for goal_line in parity_goal_lines:
        pddl_lines.append(f"  {goal_line}\n")

    pddl_lines.append("  )\n)\n")
    pddl_lines.append("(:metric minimize (total-cost))\n")
    pddl_lines.append(")")
    return pddl_lines, parity_ks



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
        phase_polynomial as a dictionary from parity vectors (boolean vectors represented by numpy ints) to phases (modulo 2π)
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
            parity_vector = tuple(goal_matrix[:, q])
            old_coeff = phase_polynomial.get(parity_vector, 0)
            phase_polynomial[parity_vector] = old_coeff + theta
        else:
            raise ValueError(f"Unsupported gate: {instr.name}")

        # Simplify phase polynomial by taking coefficients modulo 2π and leaving out coefficients of 0
        phase_polynomial = {
            k: (v % (2 * np.pi))
            for k, v in phase_polynomial.items()
            if not np.isclose(v % (2 * np.pi), 0)
        }
    return goal_matrix, phase_polynomial
