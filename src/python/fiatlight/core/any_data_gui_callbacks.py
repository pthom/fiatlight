from fiatlight.core import DataType, VoidFunction, BoolFunction
from typing import Callable, Generic


class AnyDataGuiCallbacks(Generic[DataType]):
    """
    Collection of callbacks for a given type
    - edit and present: the GUI implementation of the type
    - default_value_provider: the function that provides a default value for the type
    - to_dict and from_dict: the serialization and deserialization functions (optional)
    """

    # Provide a draw function that presents the data content.
    # If not provided, the data will be presented using versatile_gui_present
    present: VoidFunction | None = None

    # Provide a draw function that presents an editable interface for the data, and returns True if changed
    edit: BoolFunction | None = None

    # (On hold)
    # Optional serialization and deserialization functions for DataType
    # If provided, these functions will be used to serialize and deserialize the data with a custom dict format.
    # If not provided, "value" will be serialized as a dict of its __dict__ attribute,
    # or as a json string (for int, float, str, bool, and None)
    # to_dict_impl: Callable[[DataType], JsonDict] | None = None
    # from_dict_impl: Callable[[JsonDict], DataType] | None = None

    # default value provider: this function will be called to provide a default value if needed
    default_value_provider: Callable[[], DataType] | None = None

    # on_change: if provided, this function will be called when the value changes
    on_change: VoidFunction | None = None

    @staticmethod
    def no_handlers() -> "AnyDataGuiCallbacks[DataType]":
        return AnyDataGuiCallbacks[DataType]()
