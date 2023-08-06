import ast
import enum
import keyword
import re
from typing import Dict, Optional, Union

import pydantic

from classiq_interface.generator.arith.fix_point_number import (
    MAX_FRACTION_PLACES,
    FixPointNumber,
)
from classiq_interface.generator.arith.register_user_input import RegisterUserInput
from classiq_interface.generator.function_params import FunctionParams
from classiq_interface.helpers.custom_pydantic_types import pydanticExpressionStr

DEFAULT_OUT_NAME = "out"
DEFAULT_ARG_NAME = "in_arg"

SUPPORTED_FUNC_NAMES = ("CLShift", "CRShift", "min", "max")

white_list = {"or", "and"}.union(SUPPORTED_FUNC_NAMES)
black_list = set(keyword.kwlist) - white_list


class MappingMethods(str, enum.Enum):
    topological = "naive"
    pebble = "optimized"


SingleArithmeticDefinition = Union[
    pydantic.StrictInt, pydantic.StrictFloat, FixPointNumber, RegisterUserInput
]
ArithmeticDefinitions = Dict[str, SingleArithmeticDefinition]


class ArithmeticTemplate(FunctionParams):
    max_fraction_places: pydantic.NonNegativeInt = MAX_FRACTION_PLACES
    expression: pydanticExpressionStr
    definitions: ArithmeticDefinitions
    method: MappingMethods = MappingMethods.pebble
    qubit_count: Optional[pydantic.NonNegativeInt] = None
    output_name: str = DEFAULT_OUT_NAME

    @pydantic.validator("expression")
    def check_expression_is_legal(cls, expression):
        try:
            ast.parse(expression, "", "eval")
        except SyntaxError:
            raise ValueError(f"Failed to parse expression '{expression}'")
        return expression

    @pydantic.root_validator()
    def check_all_variable_are_defined(cls, values):
        expression, definitions = values.get("expression"), values.get("definitions")

        literals = set(re.findall("[A-Za-z][A-Za-z0-9]*", expression))

        not_allowed = literals.intersection(black_list)
        undefined_literals = literals.difference(definitions, white_list)
        if not_allowed:
            raise ValueError(f"The following names: {not_allowed} are not allowed")

        if undefined_literals:
            raise ValueError(f"{undefined_literals} need to be defined in definitions")
        return values

    @pydantic.root_validator()
    def substitute_expression(cls, values):
        # TODO there isn't a secure way to simplify the expression which does not involve using eval.
        #  Can be done with sdk on client side
        try:
            expression = values["expression"]
            definitions = values["definitions"]
        except KeyError:
            raise ValueError("Valid expression and definition are required")
        new_definition = dict()
        for var_name, value in definitions.items():
            if isinstance(value, RegisterUserInput):
                new_definition[var_name] = value
                continue
            elif isinstance(value, int):
                pass
            elif isinstance(value, float):
                value = FixPointNumber(float_value=value).actual_float_value
            elif isinstance(value, FixPointNumber):
                value = value.actual_float_value
            else:
                raise ValueError(f"{type(value)} type is illegal")

            expression = re.sub(r"\b" + var_name + r"\b", str(value), expression)
        values["expression"] = expression
        values["definitions"] = new_definition
        return values

    @pydantic.validator("definitions")
    def set_register_names(cls, definitions):
        for k, v in definitions.items():
            if isinstance(v, RegisterUserInput):
                v.name = k
        return definitions

    def _create_io_names(self):
        literals = set(re.findall("[A-Za-z][A-Za-z0-9]*", self.expression))
        self._input_names = [
            literal for literal in literals if literal not in white_list
        ]
        self._output_names = [self.output_name]

    class Config:
        extra = "forbid"


class Arithmetic(ArithmeticTemplate):
    target: Optional[RegisterUserInput]


class ArithmeticOracle(ArithmeticTemplate):
    @pydantic.validator("expression")
    def validate_compare_expression(cls, value):
        ast_obj = ast.parse(value, "", "eval")
        if not isinstance(ast_obj, ast.Expression):
            raise ValueError("Must be an expression")
        if not isinstance(ast_obj.body, (ast.Compare, ast.BoolOp)):
            raise ValueError("Must be a comparison expression")

        return value
