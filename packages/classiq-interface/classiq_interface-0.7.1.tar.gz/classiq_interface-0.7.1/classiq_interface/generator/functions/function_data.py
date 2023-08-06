import enum
from itertools import chain
from typing import Any, List, Optional, Set, Tuple, Union

import pydantic

from classiq_interface.generator import function_call
from classiq_interface.generator.functions.function_implementation import (
    FunctionImplementation,
    Register,
    to_tuple,
)
from classiq_interface.helpers.custom_pydantic_types import pydanticFunctionNameStr

ImplementationsType = Union[Tuple[FunctionImplementation, ...], FunctionImplementation]


class FunctionType(str, enum.Enum):
    ElementaryFunction = "ElementaryFunction"
    CompositeFunction = "CompositeFunction"


def _first_impl(impl_type: ImplementationsType) -> FunctionImplementation:
    if isinstance(impl_type, FunctionImplementation):
        return impl_type
    else:
        return impl_type[0]


class FunctionData(pydantic.BaseModel):
    """
    Facilitates the creation of a user-defined custom function
    """

    name: pydanticFunctionNameStr = pydantic.Field(
        description="The name of a custom function"
    )

    implementations: Optional[ImplementationsType] = pydantic.Field(
        description="The implementations of the custom function",
    )
    logic_flow: List[function_call.FunctionCall] = pydantic.Field(
        default=list(), description="List of function calls to perform."
    )

    _function_type: FunctionType = pydantic.PrivateAttr(default=None)
    _input_set: Set[str] = pydantic.PrivateAttr(default_factory=set)
    _output_set: Set[str] = pydantic.PrivateAttr(default_factory=set)

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.logic_flow:
            self._function_type = FunctionType.CompositeFunction
            self._input_set, self._output_set = self._deduce_composite_io_names(
                self.logic_flow
            )
            return

        inputs_regs: Tuple[Register, ...] = (
            to_tuple(_first_impl(self.implementations).input_registers)
            if self.implementations is not None
            else tuple()
        )
        output_regs: Tuple[Register, ...] = (
            to_tuple(_first_impl(self.implementations).output_registers)
            if self.implementations is not None
            else tuple()
        )

        self._function_type = FunctionType.ElementaryFunction
        self._input_set = set(register.name for register in inputs_regs)
        self._output_set = set(register.name for register in output_regs)

    @staticmethod
    def _deduce_composite_io_names(
        logic_flow: List[function_call.FunctionCall],
    ) -> Tuple[Set[str], Set[str]]:
        input_wires = list(chain(*(call.non_zero_input_wires for call in logic_flow)))
        output_wires = list(chain(*(call.non_zero_output_wires for call in logic_flow)))

        input_names = {name for name in input_wires if name not in output_wires}
        output_names = {name for name in output_wires if name not in input_wires}

        return input_names, output_names

    @property
    def input_set(self) -> Set[str]:
        return self._input_set

    @property
    def output_set(self) -> Set[str]:
        return self._output_set

    @property
    def function_type(self) -> FunctionType:
        return self._function_type

    @pydantic.validator("name")
    def validate_name(cls, name: str):
        validate_name_end_not_newline(name=name)
        return name

    @pydantic.validator("implementations")
    def validate_implementations(cls, implementations: ImplementationsType):
        if implementations is None:
            return implementations

        if not implementations:
            raise ValueError(
                "The implementations of a custom function must be non-empty."
            )

        if isinstance(implementations, FunctionImplementation):
            implementations = (implementations,)

        distinct_io_signatures = set(
            tuple(
                tuple(
                    sorted(
                        (register.name, register.width)
                        for register in to_tuple(registers)
                    )
                )
                for registers in (
                    implementation.input_registers,
                    implementation.output_registers,
                )
            )
            for implementation in implementations
        )
        if len(distinct_io_signatures) != 1:
            raise ValueError(
                "All implementations of a custom function must have matching IO "
                "register names and widths."
            )
        return implementations

    @pydantic.root_validator
    def validate_logic_flow(cls, values):
        implementations = values.get("implementations")
        logic_flow = values.get("logic_flow")
        elementary = bool(implementations is not None)
        composite = bool(len(logic_flow) > 0)
        if elementary == composite:
            raise ValueError(
                "Function must contain either implementations or calls, but not both"
            )

        return values


def validate_name_end_not_newline(name: str):
    _NEW_LINE = "\n"
    if name.endswith(_NEW_LINE):
        raise ValueError("Function name cannot end in a newline character")
