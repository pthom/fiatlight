from fiatlight.core import DataType, VoidFunction, BoolFunction, StrFunction
from typing import Callable, Generic


class AnyDataGuiCallbacks(Generic[DataType]):
    """
    Collection of callbacks for a given type
    - edit and present: the GUI implementation of the type
    - default_value_provider: the function that provides a default value for the type
    - to_dict and from_dict: the serialization and deserialization functions (optional)
    """

    # Provide a function that returns a *short* one-line string info about the data content
    # This string will be presented as a short description of the data in the GUI
    # (it should be short enough to fit in a single line inside a node: max 40 chars)
    # If not provided, the data will be presented using versatile_gui_present
    # For example, on complex types such as images, return something like "Image 128x128x3 uint8"
    present_short_str: StrFunction | None = None

    # Provide a draw function that presents the data content for more complex types (images, etc.)
    # It will be presented in "expanded" mode, and can use imgui widgets on several lines.
    # If not provided, the data will be presented using present_str
    present: VoidFunction | None = None

    # Provide a draw function that presents an editable interface for the data, and returns True if changed
    edit: BoolFunction | None = None

    # default value provider: this function will be called to provide a default value if needed
    default_value_provider: Callable[[], DataType] | None = None

    # on_change: if provided, this function will be called when the value changes
    on_change: VoidFunction | None = None

    # (On hold)
    # Optional serialization and deserialization functions for DataType
    # If provided, these functions will be used to serialize and deserialize the data with a custom dict format.
    # If not provided, "value" will be serialized as a dict of its __dict__ attribute,
    # or as a json string (for int, float, str, bool, and None)
    # to_dict_impl: Callable[[DataType], JsonDict] | None = None
    # from_dict_impl: Callable[[JsonDict], DataType] | None = None

    @staticmethod
    def no_handlers() -> "AnyDataGuiCallbacks[DataType]":
        return AnyDataGuiCallbacks[DataType]()
