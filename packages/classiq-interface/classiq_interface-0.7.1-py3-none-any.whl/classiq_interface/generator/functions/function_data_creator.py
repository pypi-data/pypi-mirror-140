from functools import cached_property

from qiskit import QuantumCircuit

from classiq_interface.generator.functions import function_implementation
from classiq_interface.generator.functions.function_data import FunctionData
from classiq_interface.generator.functions.register import Register


# TODO: Delete this class and convert it's calls to tools from SDK once they are imported into classiq_interface
class FunctionDataCreator:
    def __init__(self, qc: QuantumCircuit, name: str):
        self.qc = qc
        self.name = name

        self.input_register_name: str = name + "_input"
        self.input_registers: function_implementation.RegistersType = (
            Register(name=self.input_register_name, qubits=tuple(range(qc.num_qubits))),
        )

        self.output_register_name: str = name + "_output"
        self.output_registers: function_implementation.RegistersType = (
            Register(
                name=self.output_register_name, qubits=tuple(range(qc.num_qubits))
            ),
        )

    @cached_property
    def function_data(self) -> FunctionData:
        function_data = FunctionData(
            name=self.name,
            implementations=function_implementation.FunctionImplementation(
                serialized_circuit=self.qc.qasm(),
                input_registers=self.input_registers,
                output_registers=self.output_registers,
            ),
        )

        return function_data
