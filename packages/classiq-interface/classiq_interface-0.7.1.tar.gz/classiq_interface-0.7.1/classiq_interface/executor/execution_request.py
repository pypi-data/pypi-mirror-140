from typing import Any, Dict, Union

import pydantic
from typing_extensions import Literal

from classiq_interface.backend.backend_preferences import IonqBackendPreferences
from classiq_interface.executor.execution_preferences import ExecutionPreferences
from classiq_interface.executor.hamiltonian_minimization_problem import (
    HamiltonianMinimizationProblem,
)
from classiq_interface.executor.quantum_program import (
    QuantumInstructionSet,
    QuantumProgram,
)
from classiq_interface.generator.generation_metadata import GenerationMetadata


class GenerationMetadataExecution(GenerationMetadata):
    execution_type: Literal["generation_metadata"] = "generation_metadata"


class QuantumProgramExecution(QuantumProgram):
    execution_type: Literal["quantum_program"] = "quantum_program"


class HamiltonianMinimizationProblemExecution(HamiltonianMinimizationProblem):
    execution_type: Literal[
        "hamiltonian_minimization_problem"
    ] = "hamiltonian_minimization_problem"


class ExecutionRequest(pydantic.BaseModel):
    execution_payload: Union[
        GenerationMetadataExecution,
        QuantumProgramExecution,
        HamiltonianMinimizationProblemExecution,
    ]
    preferences: ExecutionPreferences = pydantic.Field(
        default_factory=ExecutionPreferences,
        description="preferences for the execution",
    )

    @pydantic.validator("preferences")
    def validate_ionq_backend(
        cls, preferences: ExecutionPreferences, values: Dict[str, Any]
    ):
        quantum_program = values.get("execution_payload")
        if isinstance(quantum_program, QuantumProgram):
            if quantum_program.syntax == QuantumInstructionSet.IONQ:
                raise ValueError("Can only execute IonQ code on IonQ backend.")
        elif isinstance(preferences.backend_preferences, IonqBackendPreferences):
            raise ValueError("IonQ backend supports only execution of QuantumPrograms")
        return preferences
