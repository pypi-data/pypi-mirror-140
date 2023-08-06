from typing import List, Optional, Union

import pydantic


class HamiltonianReduction(pydantic.BaseModel):
    two_qubit_reduction: Optional[bool] = pydantic.Field(default=False)
    number_particle_reduction: Optional[bool] = pydantic.Field(default=False)
    freeze_core: Optional[bool] = pydantic.Field(default=False)
    remove_orbitals: Optional[List[int]] = pydantic.Field(
        default=None, description="list of orbitals to remove"
    )
    z2_symmetries: Optional[Union[str, List[int]]] = pydantic.Field(
        default=None,
        description="possible values are: None, 'auto' or a list of 1 and -1",
    )
