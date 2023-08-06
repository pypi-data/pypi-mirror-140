from __future__ import annotations

import functools
import random
import re
import string
from typing import Dict, Iterable, List, Match, Optional, Tuple

import pydantic

from classiq_interface.generator import function_param_list, function_params as f_params
from classiq_interface.generator.user_defined_function_params import CustomFunction
from classiq_interface.helpers.custom_pydantic_types import pydanticNonEmptyString

DEFAULT_SUFFIX_LEN: int = 6
BAD_FUNCTION_ERROR_MSG = "Unknown function"
BAD_INPUT_ERROR_MSG = "Bad input name given"
BAD_OUTPUT_ERROR_MSG = "Bad output name given"
# TODO - separate name token and slice token errors
BAD_INPUT_EXPRESSION_MSG = "Bad input expression given"
BAD_OUTPUT_EXPRESSION_MSG = "Bad output expression given"

ALLOWED_IO_NAME_REGEX = r"\w+"
NAME = "name"
START_OR_INDEX = "start_or_index"
STOP = "stop"
SLICE_REGEX = rf"(?P<{NAME}>{ALLOWED_IO_NAME_REGEX})(\[(?P<{START_OR_INDEX}>\d+)(:(?P<{STOP}>\d+))?\])?"
_ALPHANUM_CHARACTERS = string.ascii_letters + string.digits

RegNameAndSlice = Tuple[str, slice]
ParsedIOs = Iterable[Tuple[str, slice, str]]

ZERO_INDICATOR = "0"


def randomize_suffix(suffix_len: int = DEFAULT_SUFFIX_LEN) -> str:
    return "".join(
        random.choice(_ALPHANUM_CHARACTERS) for _ in range(suffix_len)  # noqa: S311
    )


class FunctionCall(pydantic.BaseModel):
    function: str = pydantic.Field(
        default="", description="The function that is called"
    )
    function_params: f_params.FunctionParams = pydantic.Field(
        description="The parameters necessary for defining the function"
    )
    is_inverse: bool = pydantic.Field(
        default=False, description="call to function inverse"
    )
    inputs: Dict[pydanticNonEmptyString, str] = pydantic.Field(
        default_factory=dict,
        description="A mapping from the input name to the wire it connects to",
    )
    outputs: Dict[pydanticNonEmptyString, str] = pydantic.Field(
        default_factory=dict,
        description="A mapping from the output name to the wire it connects to",
    )

    name: pydanticNonEmptyString = pydantic.Field(
        default=None,
        description="The name of the function call. Determined automatically.",
    )

    _non_zero_input_wires: List[str] = pydantic.PrivateAttr(default_factory=list)
    _non_zero_output_wires: List[str] = pydantic.PrivateAttr(default_factory=list)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._non_zero_input_wires = self._non_zero_wires(self.inputs.values())
        self._non_zero_output_wires = self._non_zero_wires(self.outputs.values())

    @property
    def non_zero_input_wires(self) -> List[str]:
        return self._non_zero_input_wires

    @property
    def non_zero_output_wires(self) -> List[str]:
        return self._non_zero_output_wires

    @pydantic.validator("name", pre=True, always=True)
    def create_name(cls, name, values):
        function = values.get("function")
        params = values.get("function_params")
        suffix = randomize_suffix()
        if not function or params is None:
            return name if name else suffix

        if isinstance(params, CustomFunction):
            return f"{params.name}_{suffix}"
        return f"{function}_{suffix}"

    @pydantic.validator("function_params", pre=True)
    def parse_function_params(cls, function_params, values):
        if isinstance(function_params, f_params.FunctionParams):
            values["function"] = type(function_params).__name__
            return function_params

        function = values.get("function")
        if not function:
            raise ValueError(
                "The function field must be provided to deduce function type"
            )

        func_class = [
            seg
            for seg in function_param_list.get_function_param_list()
            if seg.__name__ == function
        ]

        if not func_class:
            raise ValueError(f"{BAD_FUNCTION_ERROR_MSG}: {function}")

        return func_class[0].parse_obj(function_params)

    # TODO: note that this checks FunctionCall input register names
    # are PARTIAL to FuncionParams input register names, not EQUAL.
    # We might want to change that.
    @staticmethod
    def _validate_input_names(
        params: f_params.FunctionParams, inputs: Dict[str, str], is_inverse: bool
    ) -> None:

        invalid_expressions, invalid_names = FunctionCall._get_invalid_ios(
            inputs.keys(), params, f_params.input_io(is_inverse)
        )
        error_msg = []
        if invalid_expressions:
            error_msg.append(f"{BAD_INPUT_EXPRESSION_MSG}: {invalid_expressions}")
        if invalid_names:
            error_msg.append(f"{BAD_INPUT_ERROR_MSG}: {invalid_names}")
        if error_msg:
            raise ValueError("\n".join(error_msg))

    @pydantic.validator("inputs")
    def validate_inputs(cls, inputs: Dict[str, str], values) -> Dict[str, str]:
        params = values.get("function_params")
        is_inverse = values.get("is_inverse")
        if params is None:
            return inputs
        if isinstance(params, CustomFunction):
            return inputs
        cls._validate_input_names(params=params, inputs=inputs, is_inverse=is_inverse)
        return inputs

    @staticmethod
    def _validate_output_names(
        params: f_params.FunctionParams, outputs: Dict[str, str], is_inverse: bool
    ) -> None:

        invalid_expressions, invalid_names = FunctionCall._get_invalid_ios(
            outputs.keys(), params, f_params.output_io(is_inverse)
        )
        error_msg = []
        if invalid_expressions:
            error_msg.append(f"{BAD_OUTPUT_EXPRESSION_MSG}: {invalid_expressions}")
        if invalid_names:
            error_msg.append(f"{BAD_OUTPUT_ERROR_MSG}: {invalid_names}")
        if error_msg:
            raise ValueError("\n".join(error_msg))

    @pydantic.validator("outputs")
    def validate_outputs(cls, outputs, values):
        params = values.get("function_params")
        is_inverse = values.get("is_inverse")
        if params is None:
            return outputs
        if isinstance(params, CustomFunction):
            return outputs
        cls._validate_output_names(
            params=params, outputs=outputs, is_inverse=is_inverse
        )
        return outputs

    @staticmethod
    def _get_invalid_ios(
        expressions: Iterable[str], params: f_params.FunctionParams, io: f_params.IO
    ) -> Tuple[List[str], List[str]]:

        expression_matches: Iterable[Optional[Match]] = map(
            functools.partial(re.fullmatch, SLICE_REGEX), expressions
        )

        valid_matches: List[Match] = []
        invalid_expressions: List[str] = []
        for expression, expression_match in zip(expressions, expression_matches):
            invalid_expressions.append(
                expression
            ) if expression_match is None else valid_matches.append(expression_match)

        invalid_names: List[str] = []
        for match in valid_matches:
            name = match.groupdict().get(NAME)
            if name is None:
                raise AssertionError("Input/output name validation error")
            if not params.is_valid_io_name(name, io):
                invalid_names.append(name)

        return invalid_expressions, invalid_names

    def validate_custom_function_io(self) -> None:
        if not isinstance(self.function_params, CustomFunction):
            raise AssertionError("CustomFunction object expected.")
        FunctionCall._validate_input_names(
            params=self.function_params, inputs=self.inputs, is_inverse=self.is_inverse
        )
        FunctionCall._validate_output_names(
            params=self.function_params,
            outputs=self.outputs,
            is_inverse=self.is_inverse,
        )

    def parse_inputs(self) -> ParsedIOs:
        reg_names_and_slices = zip(*map(self._parse_io_slicing, self.inputs.keys()))
        wire_names = self.inputs.values()
        # types cannot be resolved from zip
        return zip(*reg_names_and_slices, wire_names)  # type: ignore[return-value]

    def parse_outputs(self) -> ParsedIOs:
        reg_names_and_slices = zip(*map(self._parse_io_slicing, self.outputs.keys()))
        wire_names = self.outputs.values()
        # types cannot be resolved from zip
        return zip(*reg_names_and_slices, wire_names)  # type: ignore[return-value]

    @staticmethod
    def _parse_io_slicing(io_str: str) -> RegNameAndSlice:
        match: Optional[Match] = re.fullmatch(SLICE_REGEX, io_str)
        if match is None:
            raise AssertionError("Input/output name validation error")

        name, start_or_index, stop = (
            match.groupdict().get(x) for x in [NAME, START_OR_INDEX, STOP]
        )

        if name is None:
            raise AssertionError("Input/output name validation error")
        if start_or_index is None:
            # full slicing
            return name, slice(None)
        if stop is not None:
            return name, slice(int(start_or_index), int(stop))
        else:
            # no stop means a single index
            return name, slice(int(start_or_index), int(start_or_index) + 1)

    @staticmethod
    def _non_zero_wires(wires: Iterable[str]) -> List[str]:
        return [wire for wire in wires if wire != ZERO_INDICATOR]

    def inverse(self) -> FunctionCall:
        return FunctionCall(
            function=self.function,
            function_params=self.function_params,
            inputs=self.outputs,
            outputs=self.inputs,
            name=self.name,
            is_inverse=not self.is_inverse,
        )
