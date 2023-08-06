import pydantic

from classiq_interface.generator.standard_gates.standard_gates import StandardGate


class RXGate(StandardGate):
    """
    Rotation by theta about the X axis
    """

    theta: float


class RYGate(StandardGate):
    """
    Rotation by theta about the Y axis
    """

    theta: float


class RZGate(StandardGate):
    """
    Rotation by phi about the Z axis
    """

    phi: float


class RGate(StandardGate):
    """
    Rotation by theta about the cos(phi)X + sin(phi)Y axis
    """

    theta: float
    phi: float


class PhaseGate(StandardGate):
    """
    Add relative phase of lambda
    """

    theta: float


class DoubleRotationGate(StandardGate):
    """
    Base class for RXX, RYY, RZZ
    """

    theta: float
    _num_target_qubits: pydantic.PositiveInt = pydantic.PrivateAttr(default=2)


class RXXGate(DoubleRotationGate):
    """
    Rotation by theta about the XX axis
    """


class RYYGate(DoubleRotationGate):
    """
    Rotation by theta about the YY axis
    """


class RZZGate(DoubleRotationGate):
    """
    Rotation by theta about the ZZ axis
    """
