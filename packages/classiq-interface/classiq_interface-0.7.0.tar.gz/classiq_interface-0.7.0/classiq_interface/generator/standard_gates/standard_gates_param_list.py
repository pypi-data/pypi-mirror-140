from typing import Set, Type

from classiq_interface.generator.function_params import FunctionParams
from classiq_interface.generator.standard_gates.controlled_standard_gates import (
    C3XGate,
    C4XGate,
    CCXGate,
    CHGate,
    CPhaseGate,
    CRXGate,
    CRYGate,
    CRZGate,
    CSXGate,
    CXGate,
    CYGate,
    CZGate,
    MCPhaseGate,
)
from classiq_interface.generator.standard_gates.standard_angled_gates import (
    PhaseGate,
    RGate,
    RXGate,
    RXXGate,
    RYGate,
    RYYGate,
    RZGate,
    RZZGate,
)
from classiq_interface.generator.standard_gates.standard_gates import (
    HGate,
    IGate,
    SdgGate,
    SGate,
    SwapGate,
    SXdgGate,
    SXGate,
    TdgGate,
    TGate,
    XGate,
    YGate,
    ZGate,
    iSwapGate,
)

_standard_function_param_list: Set[Type[FunctionParams]] = {
    XGate,
    YGate,
    ZGate,
    HGate,
    IGate,
    SGate,
    SdgGate,
    SXGate,
    SXdgGate,
    TGate,
    TdgGate,
    iSwapGate,
    SwapGate,
    RXGate,
    RXXGate,
    RYGate,
    RYYGate,
    RZGate,
    RZZGate,
    RGate,
    PhaseGate,
    CXGate,
    CCXGate,
    C3XGate,
    C4XGate,
    CYGate,
    CZGate,
    CHGate,
    CRXGate,
    CRYGate,
    CRZGate,
    CSXGate,
    CPhaseGate,
    MCPhaseGate,
}


def get_qiskit_standard_function_param_list() -> Set[Type[FunctionParams]]:
    return _standard_function_param_list
