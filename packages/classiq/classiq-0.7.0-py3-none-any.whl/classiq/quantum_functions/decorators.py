from typing import Callable

from classiq.quantum_functions.quantum_function import QuantumFunction


def quantum_function(func: Callable) -> QuantumFunction:
    qf = QuantumFunction()
    qf.add_implementation(func)
    return qf
