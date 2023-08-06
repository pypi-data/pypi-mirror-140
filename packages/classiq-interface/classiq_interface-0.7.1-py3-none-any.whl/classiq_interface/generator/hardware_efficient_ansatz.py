from typing import List, Union

import pydantic

from classiq_interface.generator import function_params

# TODO mutable defaults might be problematic @shahakL


class HardwareEfficientAnsatz(function_params.FunctionParams):
    _input_names = pydantic.PrivateAttr(default=[function_params.DEFAULT_INPUT_NAME])
    _output_names = pydantic.PrivateAttr(default=[function_params.DEFAULT_OUTPUT_NAME])

    num_qubits: pydantic.PositiveInt = pydantic.Field(
        description="Number of qubits in the ansatz"
    )
    connectivity_map: List[List[pydantic.NonNegativeInt]] = pydantic.Field(
        description="Hardware's connectivity map, in the form [ [x0, x1], [x1, x2],...]"
    )
    reps: pydantic.PositiveInt = pydantic.Field(
        default=1, description="Number of layers in the Ansatz"
    )

    one_qubit_gates: Union[str, List[str]] = pydantic.Field(
        default=["x", "ry"],
        description='List of gates for the one qubit gates layer, e.g. ["x", "ry"]',
    )
    two_qubit_gates: Union[str, List[str]] = pydantic.Field(
        default=["cx"],
        description='List of gates for the two qubit gates entangling layer, e.g. ["cx", "cry"]',
    )

    @pydantic.validator("connectivity_map")
    def validate_connectivity_map(cls, connectivity_map, values):
        num_qubits = values.get("num_qubits")
        if num_qubits is None:
            return
        for connection in connectivity_map:
            if len(connection) != 2:
                raise ValueError(
                    f"Connectivity {connection} is invalid, must connect exactly 2 qubits"
                )
            for index in connection:
                if index >= num_qubits:
                    raise ValueError(
                        f"Provided index {index} is bigger than num_qubits-1"
                    )
        return connectivity_map
