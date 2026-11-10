from qiskit import (
    QuantumCircuit,
    QuantumRegister,
    ClassicalRegister
)
from qiskit.visualization import circuit_drawer

def run(qc):
    qc.h(2)
    qc.cswap(2,0,1)
    qc.h(2)
    qc.x(2)
    qc.measure(2,0)

    return circuit_drawer(qc)
    #circuit_drawer(qc, filename='./swap_circuit')
    
print(run(QuantumCircuit(3,3)))




