import pydantic

from classiq_interface.chemistry.operator import PauliOperator
from classiq_interface.executor.quantum_program import QuantumProgram


class HamiltonianMinimizationProblem(pydantic.BaseModel):
    ansatz: QuantumProgram
    hamiltonian: PauliOperator
