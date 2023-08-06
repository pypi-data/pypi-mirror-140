from typing import List, Optional, Tuple

import pydantic


class AtomicLocation(pydantic.BaseModel):
    x: float = pydantic.Field(description="The X location of an atom")
    y: float = pydantic.Field(description="The Y location of an atom")
    z: float = pydantic.Field(description="The Z location of an atom")

    def to_list(self) -> List[float]:
        return [self.x, self.y, self.z]


class Atom(pydantic.BaseModel):
    name: str = pydantic.Field(description="The name of the atom")
    location: AtomicLocation = pydantic.Field(description="The location of the atom")


class Molecule(pydantic.BaseModel):
    atoms: List[Atom] = pydantic.Field(description="List of atoms")
    spin: Optional[pydantic.NonNegativeInt] = pydantic.Field(
        default=1, description="spin of the molecule"
    )
    charge: Optional[pydantic.NonNegativeInt] = pydantic.Field(
        default=0, description="charge of the molecule"
    )

    @property
    def geometry(self) -> List[Tuple[str, List[float]]]:
        return [(atom.name, atom.location.to_list()) for atom in self.atoms]
