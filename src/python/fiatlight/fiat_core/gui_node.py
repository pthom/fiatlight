"""GuiNode: A node that simply displays a GUI function.
It is implemented as a function node with an internal gui function.
"""
from fiatlight.fiat_core.function_with_gui import FunctionWithGui
from fiatlight.fiat_types.base_types import JsonDict
from fiatlight.fiat_types.function_types import GuiFunction
from pydantic import BaseModel


def _empty_function() -> None:
    pass


def _populate_base_model_from_dict(dst: BaseModel, data_dict: JsonDict) -> None:
    """
    Populate the fields of an existing BaseModel instance from a dictionary.
    This has the advantage that it does not change the id (memory address) of the instance.

    Parameters:
    dst (BaseModel): The destination BaseModel instance to populate.
    data_dict (dict): The dictionary containing the data to populate the instance with.
    """
    # Validate the dictionary against the model's schema
    data_dict_instance = type(dst).model_validate(data_dict)  # Will raise an error if the data_dict is not valid

    # Update the fields of the destination instance
    for field in dst.__fields__.keys():
        assert hasattr(data_dict_instance, field)
        setattr(dst, field, getattr(data_dict_instance, field))


class GuiNode(FunctionWithGui):
    """A node that simply displays a GUI function, with optional serializable data.
    If gui_serializable_data is provided, the GUI options will be saved and loaded from JSON,
    and restored upon restarting the application.
    gui_serializable_data must be a pydantic BaseModel instance (because it is serializable by default).
    """

    gui_serializable_data: BaseModel | None

    def __init__(
        self,
        gui_function: GuiFunction,
        label: str | None = None,
        gui_node_compatible: bool = True,
        gui_serializable_data: BaseModel | None = None,
    ) -> None:
        super().__init__(_empty_function)

        def gui_as_bool() -> bool:
            gui_function()
            return False

        self.internal_state_gui = gui_as_bool
        self.internal_state_gui_node_compatible = gui_node_compatible

        self.function_name = gui_function.__name__
        self.label = label if label is not None else self.function_name

        if gui_serializable_data is not None:
            self.gui_serializable_data = gui_serializable_data
            self.save_internal_gui_options_to_json = self.save_gui_serializable_data
            self.load_internal_gui_options_from_json = self.load_gui_serializable_data

    def save_gui_serializable_data(self) -> JsonDict:
        assert self.gui_serializable_data is not None
        return self.gui_serializable_data.model_dump(mode="json")

    def load_gui_serializable_data(self, json_data: JsonDict) -> None:
        assert self.gui_serializable_data is not None
        _populate_base_model_from_dict(self.gui_serializable_data, json_data)
