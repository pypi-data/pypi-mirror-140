"""Quantum circuit that adds two integers via the Draper method.
"""
from typing import Union
import logging
from numpy import pi


from qiskit import QuantumCircuit
from qiskit import QuantumRegister
from qiskit import ClassicalRegister
from qiskit import Aer
from qiskit import assemble


def embed_integers(
    circuit: QuantumCircuit, register: QuantumRegister, binary_rep: str
) -> QuantumCircuit:
    """Embeds an integer into a circuit


    Returns:
        QuantumCircuit: The circuit with the integer embedded.
    """
    if binary_rep == "":
        return circuit
    for i, binary in enumerate(reversed(binary_rep)):
        if binary == "1":
            circuit.x(register[i])
    return circuit


def qft_rotations(circuit: QuantumCircuit, num_qubits: int) -> None:
    """QFT without swap on the first n qubits in circuit

    Returns:
        None

    Credit: https://qiskit.org/textbook/ch-algorithms/quantum-fourier-transform.html
    """
    if num_qubits == 0:  # Exit function if circuit is empty
        return circuit
    num_qubits -= 1  # Indexes start from 0
    circuit.h(num_qubits)  # Apply the H-gate to the most significant qubit
    for qubit in range(num_qubits):
        # For each less significant qubit, we need to do a
        # smaller-angled controlled rotation:
        circuit.cp(pi / 2 ** (num_qubits - qubit), qubit, num_qubits)
    qft_rotations(circuit, num_qubits)
    return None


def inverse_qft(circuit: QuantumCircuit, num_qubits: int) -> QuantumCircuit:
    """Does the inverse QFT on the first n qubits in circuit"""
    # First we create a QFT circuit of the correct size:
    circ = QuantumCircuit(num_qubits)
    qft_rotations(circ, num_qubits)
    # Then we take the inverse of this circuit
    invqft_circ = circ.inverse()
    # And add it to the first n qubits in our existing circuit
    circuit.append(invqft_circ, circuit.qubits[:num_qubits])
    return circuit.decompose()  # .decompose() allows us to see the individual gates


def draper_adder(
    int_1: Union[int, str] = 7, int_2: Union[int, str] = 5
) -> QuantumCircuit:
    """Creates a quantum circuit that adds two integers via the Draper method.
        https://arxiv.org/pdf/quant-ph/0008033.pdf

    Returns:
        QuantumCircuit: The quantum circuit with the addition circuit.
    """

    if isinstance(int_1, int):
        if int_1 < 0:
            raise ValueError("Draper adder only works for positive integers")
        int_1 = "{0:b}".format(int_1)
    if isinstance(int_2, int):
        if int_2 < 0:
            raise ValueError("Draper adder only works for positive integers")
        int_2 = "{0:b}".format(int_2)
    num_qubits = max(len(int_2), len(int_1))
    q_1 = QuantumRegister(num_qubits + 1)  # add one for carry
    q_2 = QuantumRegister(num_qubits)
    c_1 = ClassicalRegister(num_qubits + 1)
    circ = QuantumCircuit(q_1, q_2, c_1)

    # Embed int_1 and int_2
    embed_integers(circ, q_1, int_1)
    embed_integers(circ, q_2, int_2)
    qft_rotations(circ, num_qubits + 1)

    # # Apply controlled phase shift to the target qubit
    register_len = len(q_2)
    for qubit in range(register_len):
        for idx in range(register_len - qubit):
            circ.cp(pi / 2 ** (idx), q_2[qubit], q_1[qubit + idx])

    # Apply controlled phase shift for carry
    for idx in range(register_len):
        circ.cp(2 * pi / 2 ** (idx + 2), q_2[register_len - idx - 1], q_1[register_len])
    # Apply inverse qft
    inverse_qft(circ, num_qubits + 1)

    # Apply measurement
    circ.measure(q_1, c_1)
    circ = circ.decompose()
    # Run job
    aer_sim = Aer.get_backend("aer_simulator")
    qobj = assemble(circ, shots=8192)
    job = aer_sim.run(qobj)
    hist = job.result().get_counts()
    keys = [key for key, value in hist.items() if value == max(hist.values())]
    if len(keys) > 1:
        logging.warning("Multiple results found. Using first result.")
    if len(keys) == 0:
        logging.warning(" No results found. Using 0.")
        return 0
    if keys[0].lstrip("0") == "":
        return "0"
    return keys[0].lstrip("0")
