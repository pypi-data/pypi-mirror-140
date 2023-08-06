from typing import Optional

from classiq_interface.generator.arith.arithmetic import ArithmeticOracle
from classiq_interface.generator.function_params import IO, FunctionParams
from classiq_interface.generator.state_preparation import StatePreparation


class GroverOperator(FunctionParams):
    oracle: ArithmeticOracle
    state_preparation: Optional[StatePreparation] = None
    diffuser: Optional[str] = None

    def _create_io_names(self) -> None:
        self._input_names = self.oracle.get_io_names(IO.Input)
        self._output_names = self.oracle.get_io_names(IO.Input)

    class Config:
        extra = "forbid"
