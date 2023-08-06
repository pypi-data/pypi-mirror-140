from typing import Optional

import pydantic

from classiq_interface.generator.arith.arithmetic import (
    DEFAULT_ARG_NAME,
    DEFAULT_OUT_NAME,
)
from classiq_interface.generator.arith.register_user_input import RegisterUserInput
from classiq_interface.generator.function_params import FunctionParams


class UnaryOpParams(FunctionParams):
    arg: RegisterUserInput
    output_size: Optional[pydantic.PositiveInt]
    output_name: Optional[str] = DEFAULT_OUT_NAME
    inplace: bool = False

    def _create_io_names(self):
        output_names = [self.output_name if self.output_name else DEFAULT_OUT_NAME]
        arg_name = self.arg.name if self.arg.name else DEFAULT_ARG_NAME

        if not self.inplace:
            output_names.append(arg_name)

        self._output_names = output_names
        self._input_names = [arg_name]

    class Config:
        arbitrary_types_allowed = True


class BitwiseInvert(UnaryOpParams):
    pass


class Negation(UnaryOpParams):
    pass
