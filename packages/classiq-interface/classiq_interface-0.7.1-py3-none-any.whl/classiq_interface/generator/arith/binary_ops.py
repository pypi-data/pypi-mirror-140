from typing import Any, Dict, Generic, List, Optional, Tuple, TypeVar, Union

import pydantic
from pydantic import BaseModel
from pydantic.generics import GenericModel
from typing_extensions import Literal

from classiq_interface.generator.arith.arithmetic import DEFAULT_OUT_NAME
from classiq_interface.generator.arith.fix_point_number import FixPointNumber
from classiq_interface.generator.arith.register_user_input import RegisterUserInput
from classiq_interface.generator.function_params import FunctionParams

DEFAULT_RIGHT_ARG_NAME = "right_arg"
DEFAULT_LEFT_ARG_NAME = "left_arg"
DEFAULT_GARBAGE_OUT_NAME = "deleted_qubits"
LeftDataT = TypeVar("LeftDataT")
RightDataT = TypeVar("RightDataT")
Numeric = (float, int)


class BinaryOpParams(GenericModel, FunctionParams, Generic[LeftDataT, RightDataT]):
    left_arg: LeftDataT
    right_arg: RightDataT
    output_size: Optional[pydantic.PositiveInt]
    output_name: str = DEFAULT_OUT_NAME

    @pydantic.validator("left_arg")
    def set_left_arg_name(cls, left_arg):
        if isinstance(left_arg, RegisterUserInput) and left_arg.name is None:
            left_arg.name = DEFAULT_LEFT_ARG_NAME
        return left_arg

    @pydantic.validator("right_arg")
    def set_right_arg_name(cls, right_arg):
        if isinstance(right_arg, RegisterUserInput) and right_arg.name is None:
            right_arg.name = DEFAULT_RIGHT_ARG_NAME
        return right_arg

    @pydantic.root_validator(pre=True)
    def validate_one_is_register(cls, values):
        left_arg = values.get("left_arg")
        right_arg = values.get("right_arg")
        if isinstance(left_arg, Numeric) and isinstance(right_arg, Numeric):
            raise ValueError("One argument must be a register")
        if left_arg is right_arg and isinstance(left_arg, BaseModel):
            # In case both arguments refer to the same object, copy it.
            # This prevents changes performed on one argument to affect the other.
            values["right_arg"] = left_arg.copy(deep=True)
        return values

    def _create_io_names(self):
        self._create_input_names()
        self._create_output_names()

    def _create_input_names(self) -> None:
        input_name_list = self._input_register_name_list(
            [self.left_arg, self.right_arg, getattr(self, "target", None)]
        )
        assert input_name_list, "At least one argument should be a register"
        self._input_names = input_name_list

    def _create_output_names(self) -> None:
        output_name_list: List[str] = self._carried_inputs_name_dict()
        output_name_list.append(self.output_name)
        if hasattr(self, "garbage_output_name"):
            output_name_list.append(self.garbage_output_name)  # type: ignore[attr-defined]
        self._output_names = output_name_list

    def _carried_inputs_name_dict(self) -> List[str]:
        return self._input_register_name_list(list(self._carried_arguments()))

    def _carried_arguments(self) -> Tuple[Optional[LeftDataT], Optional[RightDataT]]:
        if getattr(self, "inplace", False):
            if isinstance(self.right_arg, RegisterUserInput):
                return self.left_arg, None
            else:
                return None, None
        return self.left_arg, self.right_arg

    @staticmethod
    def _input_register_name_list(possible_register_args: List[Any]) -> List[str]:
        return [
            arg.name
            for arg in possible_register_args
            if isinstance(arg, RegisterUserInput) and arg.name
        ]

    class Config:
        arbitrary_types_allowed = True


class BinaryOpWithIntInputs(
    BinaryOpParams[Union[int, RegisterUserInput], Union[int, RegisterUserInput]]
):
    @pydantic.root_validator()
    def validate_int_registers(cls, values):
        left_arg = values.get("left_arg")
        is_left_arg_float_register = (
            isinstance(left_arg, RegisterUserInput) and left_arg.fraction_places > 0
        )
        right_arg = values.get("right_arg")
        is_right_arg_float_register = (
            isinstance(right_arg, RegisterUserInput) and right_arg.fraction_places > 0
        )
        if is_left_arg_float_register or is_right_arg_float_register:
            raise ValueError("Boolean operation are defined only for integer")

        return values


class BinaryOpWithFloatInputs(
    BinaryOpParams[
        Union[float, FixPointNumber, RegisterUserInput],
        Union[float, FixPointNumber, RegisterUserInput],
    ]
):
    @pydantic.validator("left_arg", "right_arg")
    def convert_numeric_to_fix_point_number(cls, val):
        if isinstance(val, Numeric):
            val = FixPointNumber(float_value=val)
        return val


class BitwiseAnd(BinaryOpWithIntInputs):
    pass


class BitwiseOr(BinaryOpWithIntInputs):
    pass


class BitwiseXor(BinaryOpWithIntInputs):
    pass


class Adder(BinaryOpWithFloatInputs):
    inplace: bool = True


class Subtractor(BinaryOpWithFloatInputs):
    inplace: bool = True


class Multiplier(BinaryOpWithFloatInputs):
    pass


class Comparator(BinaryOpWithFloatInputs):
    output_size: Literal[1] = 1
    _include_equal: bool = pydantic.PrivateAttr(default=True)
    target: Optional[RegisterUserInput]

    @pydantic.validator("target", always=True)
    def _validate_target(
        cls, target: Optional[RegisterUserInput], values: Dict[str, Any]
    ) -> Optional[RegisterUserInput]:
        if target:
            cls._assert_boolean_register(target)
            target.name = (
                target.name
                if target.name
                else values.get("output_name", DEFAULT_OUT_NAME)
            )
        return target


class Equal(Comparator):
    pass


class NotEqual(Comparator):
    pass


class GreaterThan(Comparator):
    pass


class GreaterEqual(Comparator):
    pass


class LessThan(Comparator):
    pass


class LessEqual(Comparator):
    pass


class Extremum(BinaryOpWithFloatInputs):
    _is_min: bool = pydantic.PrivateAttr(default=True)


class Min(Extremum):
    pass


class Max(Extremum):
    pass


class BinaryOpWithLeftRegRightInt(
    BinaryOpParams[RegisterUserInput, pydantic.NonNegativeInt]
):
    inplace: Literal[True] = True


class LShift(BinaryOpWithLeftRegRightInt):
    pass


class RShift(BinaryOpWithLeftRegRightInt):
    use_arithmetic_bit_shift: bool = True
    garbage_output_name: str = DEFAULT_GARBAGE_OUT_NAME


class CyclicShift(BinaryOpParams[RegisterUserInput, int]):
    inplace: Literal[True] = True
