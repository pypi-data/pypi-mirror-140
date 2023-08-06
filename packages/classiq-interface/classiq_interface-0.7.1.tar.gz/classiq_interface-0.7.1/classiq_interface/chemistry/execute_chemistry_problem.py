import pydantic

from classiq_interface.chemistry.ground_state_problem import GroundStateProblem
from classiq_interface.executor.execution_preferences import ExecutionPreferences
from classiq_interface.generator.model import Model


class GroundStateProblemExecution(pydantic.BaseModel):
    molecule: GroundStateProblem
    model: Model
    preferences: ExecutionPreferences
