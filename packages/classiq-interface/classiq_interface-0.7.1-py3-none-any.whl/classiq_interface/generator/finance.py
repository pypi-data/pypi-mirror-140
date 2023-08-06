from typing import Tuple, Union

import pydantic

from classiq_interface.finance.function_input import FinanceFunctionInput
from classiq_interface.finance.model_input import FinanceModelInput
from classiq_interface.generator import function_params


class Finance(function_params.FunctionParams):
    model: FinanceModelInput = pydantic.Field(description="Load a financial model")
    finance_function: Union[FinanceFunctionInput] = pydantic.Field(
        description="The finance function to solve the model"
    )

    _input_names = pydantic.PrivateAttr(default_factory=list)
    _output_names = pydantic.PrivateAttr(default=["out"])


class FinanceModels(function_params.FunctionParams):
    model: FinanceModelInput = pydantic.Field(description="Load a financial model")
    _input_names = pydantic.PrivateAttr(default=["in"])
    _output_names = pydantic.PrivateAttr(default=["out"])


class FinancePayoff(function_params.FunctionParams):
    finance_function: FinanceFunctionInput = pydantic.Field(
        description="The finance function to solve the model"
    )
    num_qubits: pydantic.PositiveInt
    distribution_range: Tuple[float, float]

    _input_names = pydantic.PrivateAttr(default=["in"])
    _output_names = pydantic.PrivateAttr(default=["out"])
