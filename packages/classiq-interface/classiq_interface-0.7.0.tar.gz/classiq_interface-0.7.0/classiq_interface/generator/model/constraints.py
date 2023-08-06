from collections import defaultdict
from typing import Dict, Optional

import pydantic

from classiq_interface.generator.qiskit_quantum_gates import QiskitBuiltinQuantumGates


class Constraints(pydantic.BaseModel):
    """
    Input constraints for the generated quantum circuit.
    """

    max_width: Optional[pydantic.PositiveInt] = pydantic.Field(
        default=None,
        description="Maximum number of qubits in generated quantum circuit",
    )
    max_depth: Optional[pydantic.PositiveInt] = None

    max_gate_count: Dict[
        QiskitBuiltinQuantumGates, pydantic.NonNegativeInt
    ] = pydantic.Field(default_factory=lambda: defaultdict(int))

    class Config:
        extra = "forbid"
