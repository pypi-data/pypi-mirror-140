from typing import Optional

import pydantic

from classiq_interface.generator import function_params

"""
To add new standard gates, refer to the following guide
https://docs.google.com/document/d/1Nt9frxnPkSn8swNpOQ983E95eaEiDWaiuWAKglGtUAA/edit#heading=h.e9g9309bzkxt
"""


class StandardGate(function_params.FunctionParams):
    _num_target_qubits: pydantic.PositiveInt = pydantic.PrivateAttr(default=1)

    _num_ctrl_qubits: Optional[pydantic.PositiveInt] = pydantic.PrivateAttr(
        default=None
    )

    _input_names = pydantic.PrivateAttr(default=[function_params.DEFAULT_INPUT_NAME])
    _output_names = pydantic.PrivateAttr(default=[function_params.DEFAULT_OUTPUT_NAME])

    @property
    def num_ctrl_qubit(self):
        return self._num_ctrl_qubits

    @property
    def num_target_qubits(self):
        return self._num_target_qubits


class XGate(StandardGate):
    """
    creates a X gate
    """

    pass


class YGate(StandardGate):
    """
    creates a Y gate
    """

    pass


class ZGate(StandardGate):
    """
    create a Z gate
    """

    pass


class HGate(StandardGate):
    """
    creates a Hadamard gate
    """

    pass


class IGate(StandardGate):
    """
    creates the identity gate
    """

    pass


class SGate(StandardGate):
    """
    Z**0.5
    """

    pass


class SdgGate(StandardGate):
    """
    creates the inverse S gate
    """

    pass


class SXGate(StandardGate):
    """
    X**0.5
    """

    pass


class SXdgGate(StandardGate):
    """
    creates the inverse SX gate
    """

    pass


class TGate(StandardGate):
    """
    Z**0.25
    """

    pass


class TdgGate(StandardGate):
    """
    creates the inverse T gate
    """

    pass


class SwapGate(StandardGate):
    _num_target_qubits: pydantic.PositiveInt = pydantic.PrivateAttr(default=2)
    """
    Swaps between two qubit states
    """


class iSwapGate(StandardGate):
    _num_target_qubits: pydantic.PositiveInt = pydantic.PrivateAttr(default=2)
    """
    Swaps between two qubit states and add phase of i to the amplitudes of |01> and |10>
    """
