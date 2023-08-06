from typing import Set, Type

from classiq_interface.generator.amplitude_estimation import AmplitudeEstimation
from classiq_interface.generator.arith.arithmetic import Arithmetic, ArithmeticOracle
from classiq_interface.generator.arith.binary_ops import (
    Adder,
    BitwiseAnd,
    BitwiseOr,
    BitwiseXor,
    CyclicShift,
    Equal,
    GreaterEqual,
    GreaterThan,
    LessEqual,
    LessThan,
    LShift,
    Max,
    Min,
    Multiplier,
    NotEqual,
    RShift,
    Subtractor,
)
from classiq_interface.generator.arith.logical_ops import LogicalAnd, LogicalOr
from classiq_interface.generator.arith.unary_ops import BitwiseInvert, Negation
from classiq_interface.generator.credit_risk_example.cdf_comparator import CDFComparator
from classiq_interface.generator.credit_risk_example.linear_gci import LinearGCI
from classiq_interface.generator.credit_risk_example.weighted_adder import WeightedAdder
from classiq_interface.generator.entangler_params import (
    GridEntangler,
    HypercubeEntangler,
    TwoDimensionalEntangler,
)
from classiq_interface.generator.exponentiation import Exponentiation
from classiq_interface.generator.finance import Finance, FinanceModels, FinancePayoff
from classiq_interface.generator.function_params import FunctionParams
from classiq_interface.generator.grover_operator import GroverOperator
from classiq_interface.generator.hadamard_amp_load import HadamardAmpLoad
from classiq_interface.generator.hardware_efficient_ansatz import (
    HardwareEfficientAnsatz,
)
from classiq_interface.generator.hartree_fock import HartreeFock
from classiq_interface.generator.linear_pauli_rotations import LinearPauliRotations
from classiq_interface.generator.mcx import Mcx
from classiq_interface.generator.qft import QFT
from classiq_interface.generator.sparse_amp_load import SparseAmpLoad
from classiq_interface.generator.standard_gates.standard_gates_param_list import (
    get_qiskit_standard_function_param_list,
)
from classiq_interface.generator.state_preparation import StatePreparation
from classiq_interface.generator.state_propagator import StatePropagator
from classiq_interface.generator.ucc import UCC
from classiq_interface.generator.unitary_gate import UnitaryGate
from classiq_interface.generator.user_defined_function_params import CustomFunction

_function_param_list = {
    StatePreparation,
    StatePropagator,
    QFT,
    BitwiseAnd,
    BitwiseOr,
    BitwiseXor,
    BitwiseInvert,
    Adder,
    Arithmetic,
    ArithmeticOracle,
    Equal,
    NotEqual,
    GreaterThan,
    GreaterEqual,
    LessThan,
    LessEqual,
    Negation,
    LogicalAnd,
    LogicalOr,
    Subtractor,
    RShift,
    LShift,
    CyclicShift,
    TwoDimensionalEntangler,
    Finance,
    FinanceModels,
    FinancePayoff,
    HypercubeEntangler,
    AmplitudeEstimation,
    SparseAmpLoad,
    GridEntangler,
    HadamardAmpLoad,
    GroverOperator,
    Mcx,
    CustomFunction,
    HardwareEfficientAnsatz,
    UnitaryGate,
    WeightedAdder,
    LinearPauliRotations,
    Multiplier,
    LinearGCI,
    CDFComparator,
    HartreeFock,
    UCC,
    Min,
    Max,
    Exponentiation,
}


def get_function_param_list() -> Set[Type[FunctionParams]]:
    qiskit_standard_function_param_list = get_qiskit_standard_function_param_list()
    _function_param_list.update(qiskit_standard_function_param_list)
    return _function_param_list
