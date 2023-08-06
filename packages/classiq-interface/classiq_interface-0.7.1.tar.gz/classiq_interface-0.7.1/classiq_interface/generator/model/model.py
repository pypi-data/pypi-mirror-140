from typing import Any, Dict, List, Optional, _Final  # type: ignore[attr-defined]

import pydantic

import classiq_interface.generator.validations.flow_graph as flow_graph
from classiq_interface._version import VERSION as _VERSION
from classiq_interface.generator.function_call import FunctionCall
from classiq_interface.generator.functions import FunctionLibraryData, FunctionType
from classiq_interface.generator.functions.function_data import FunctionData
from classiq_interface.generator.model.constraints import Constraints
from classiq_interface.generator.model.preferences.preferences import Preferences
from classiq_interface.generator.user_defined_function_params import CustomFunction

LOGIC_FLOW_DUPLICATION_ERROR_MSG = (
    "The same function call was included several times in the logic flow"
)


class BackwardsCompatibleBaseModel(pydantic.BaseModel):
    def __init__(__pydantic_self__, **data: Any) -> None:
        data_for_this_object = {
            key: value
            for key, value in data.items()
            if key in __pydantic_self__.__annotations__
        }
        data_for_child_objects = {
            key: value
            for key, value in data.items()
            if key not in __pydantic_self__.__annotations__
        }

        # First, initialize this object
        super().__init__(**data_for_this_object)

        # Then, populate all the rest of the data
        __pydantic_self__._set_extra_params(**data_for_child_objects)

    def _set_extra_params(self, **kwargs) -> None:
        """
        populate the children of this class with the values from kwargs
        """
        # Iterate every item that we wish to populate
        for key, value in kwargs.items():
            # Iterate every child this class has
            for obj_name, obj_cls in self.__annotations__.items():
                obj_cls_properties = self._get_properties_of_class(obj_cls)

                # Check if the item we wish to populate is a child of this obj
                if key in obj_cls_properties:
                    self._set_properties_for_child_class(
                        child_obj_name=obj_name, key=key, value=value
                    )
                    break
            # If no child was found to contain this key
            else:  # else, in for-else, is entered when no `break` was called
                raise ValueError(
                    f'"{self.__class__.__name__}" object has no field "{key}"'
                )

        # Note: when sending multiple items in `kwargs`,
        # and, in the case where the 2nd item in `kwarg` will raise an error,
        # Then the first key will be set, and this (mutable) object will change,
        # And only then will the for-loop reach the 2nd key and raise an error
        #   I'm okay with that

    @staticmethod
    def _get_properties_of_class(obj_cls) -> dict:
        # If the child is coming from typing (e.g. Union, List, etc.)
        #   Specifically, `Optional`, which is `Union[something, None]` is what's expected.
        if isinstance(obj_cls, _Final):
            # Get the parameters that were sent to the union
            obj_cls_sub_classes = obj_cls.__args__
            # get the children of each sub-class
            obj_cls_sub_properties: List[Dict[str, Any]] = [
                getattr(cls, "__annotations__", dict()) for cls in obj_cls_sub_classes
            ]
            # combine all the dictionaries
            obj_cls_properties: Dict[str, Any] = dict()
            for d in obj_cls_sub_properties:
                obj_cls_properties.update(d)
        # If the child is a pydantic object
        else:
            # Get the childred of the child
            obj_cls_properties = getattr(obj_cls, "__annotations__", {})

        return obj_cls_properties

    def _set_properties_for_child_class(
        self, child_obj_name: str, key: str, value: Any
    ) -> None:
        child_obj = getattr(self, child_obj_name)
        # First, set the attribute
        setattr(child_obj, key, value)
        # Then, manually validate the attribute
        child_obj.__init__(**child_obj.__dict__)
        # Next, patch `__fields_set` in order to support calls to
        #   self.dict(exclude_unset=True)
        object.__setattr__(
            self,
            "__fields_set__",
            set.union(self.__fields_set__, {child_obj_name}),
        )
        # Additionally, update child_obj's __fields_set__
        object.__setattr__(
            child_obj, "__fields_set__", set.union(child_obj.__fields_set__, {key})
        )

    def __getattr__(self, key):
        """
        Allow access to the grand-children of this object.
        """
        # Not supporting private attributes
        # Additionaly, this prevents an infinite loop of accessing `__getattribute__`
        if key[0] == "_":
            return super().__getattribute__(key)

        # Next, iterate every child object
        for obj_name in self.__annotations__.keys():
            # And access its child, if it exists
            if key in getattr(self, obj_name).__dir__():
                # Yes, we can use `getattr(self, obj_name).key`
                #   But I prefer calling the overwriten function explicitly
                return getattr(self, obj_name).__getattribute__(key)

        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{key}'"
        )


class Model(BackwardsCompatibleBaseModel):
    """
    All the relevand data for generating quantum circuit in one place.
    """

    version: str = _VERSION

    # Must be validated before logic_flow
    function_library: Optional[FunctionLibraryData] = pydantic.Field(
        default=None,
        description="The user-defined custom function library.",
    )

    logic_flow: List[FunctionCall] = pydantic.Field(
        default_factory=list,
        description="List of function calls to be applied in the circuit",
    )

    constraints: Constraints = pydantic.Field(default_factory=Constraints)
    preferences: Preferences = pydantic.Field(default_factory=Preferences)

    class Config:
        extra = "forbid"

    @pydantic.validator("logic_flow")
    def validate_logic_flow(
        cls, logic_flow: List[FunctionCall], values: Dict[str, Any]
    ) -> List[FunctionCall]:
        if not logic_flow:
            return logic_flow

        function_call_names = set(call.name for call in logic_flow)
        if len(function_call_names) != len(logic_flow):
            raise ValueError(LOGIC_FLOW_DUPLICATION_ERROR_MSG)

        functions_to_validate = logic_flow.copy()
        library = values.get("function_library")

        while functions_to_validate:
            function_call = functions_to_validate.pop()
            params = function_call.function_params
            if not isinstance(params, CustomFunction):
                continue

            FunctionLibraryData.validate_function_in_library(
                library=library, function_params=params
            )
            assert isinstance(library, FunctionLibraryData)
            function_data = library.function_dict[params.name]
            params.generate_io_names(
                input_set=function_data.input_set,
                output_set=function_data.output_set,
            )
            function_call.validate_custom_function_io()
            if function_data.function_type == FunctionType.CompositeFunction:
                functions_to_validate.extend(function_data.logic_flow)

        flow_graph.validate_flow_graph(logic_flow)

        return logic_flow


# TODO: Delete this method after importing tools from SDK to classiq_interface and use ModelSynthesizer instead
def insert_function_data_to_logic_flow(
    logic_flow: List[FunctionCall],
    function_library: FunctionLibraryData,
    function_data: FunctionData,
    outputs: Dict[str, str],
    inputs: Dict[str, str],
):
    function_library.function_dict[function_data.name] = function_data
    function_library.functions += (function_data,)
    function_params = CustomFunction(name=function_data.name)
    function_params.generate_io_names(
        input_set=function_data.input_set, output_set=function_data.output_set
    )

    function_call = FunctionCall(
        function_params=function_params, outputs=outputs, inputs=inputs
    )
    logic_flow.append(function_call)
