from typing import Dict, List, Optional, Union

import pydantic
from typing_extensions import Literal

from classiq_interface.generator import finance, grover_operator


class FinanceModelMetadata(pydantic.BaseModel):
    metadata_type: Literal["finance_model"] = "finance_model"
    num_model_qubits: int
    distribution_range: List[float]


class FunctionMetadata(pydantic.BaseModel):
    metadata_type: Literal["function"] = "function"
    name: str
    parent: Optional[str]
    children: List[str]
    hierarchy_level: int
    _parents: Dict[int, str] = pydantic.PrivateAttr(default={})

    def add_parents(self, parents: Dict[int, str]):
        for parent_hierarchy_level in parents.keys():
            if parent_hierarchy_level >= self.hierarchy_level:
                raise ValueError("Parent's hierarchy level must be lower than child's")
        self._parents.update(parents)

    @property
    def parents(self):
        return self._parents


class GroverMetadata(grover_operator.GroverOperator):
    metadata_type: Literal["grover"] = "grover"


class FinanceMetadata(finance.Finance):
    metadata_type: Literal["finance"] = "finance"


MetadataUnion = Union[FinanceModelMetadata, GroverMetadata, FinanceMetadata]


class GenerationMetadata(pydantic.BaseModel):
    # Ideally, we would use a "__root__" attribute, but the typescript transpilation
    # does weird things when we use it.
    metadata: MetadataUnion
