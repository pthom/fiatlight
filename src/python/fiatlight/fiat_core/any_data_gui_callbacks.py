from fiatlight.fiat_types import DataType, VoidFunction, BoolFunction, JsonDict
from typing import Callable, Generic, Any


class AnyDataGuiCallbacks(Generic[DataType]):
    """
    Collection of callbacks for a given type
    - edit and present: the GUI implementation of the type
    - default_value_provider: the function that provides a default value for the type
    - to_dict and from_dict: the serialization and deserialization functions (optional)
    """

    # present_str: (Mandatory if str() is not enough, optional otherwise)
    # Provide a function that returns a string info about the data content
    # This string will be presented as a short description of the data in the GUI
    #
    # If possible, it should be short enough to fit in a single line inside a node (20 chars max).
    # If the result string is too long, or occupies more than one line, it will be truncated and followed by "..."
    # (and the rest of the string will be displayed in a tooltip)
    # For example, on complex types such as images, return something like "128x128x3 uint8"
    # If not provided, the data will be presented using str()
    present_str: Callable[[DataType], str] | None = None

    # present_custom: (Optional)
    # Provide a draw function that presents the data content for more complex types (images, etc.)
    # It will be presented in "expanded" mode, and can use imgui widgets on several lines.
    # If not provided, the data will be presented using present_str
    present_custom: VoidFunction | None = None

    # present_custom_popup_required (Optional: leave to False in most cases)
    # If True, the present_custom function needs to be called in a popup window.
    # This is due to a limitation of the node editor, which cannot render complex widgets
    # in the node itself.
    # By complex widgets, we mean widgets that require a scrollable area, or a child window, such as:
    #      - imgui.input_text_multiline
    #      - imgui.combo
    #      - imgui.begin_child
    present_custom_popup_required: bool = False

    # present_custom_popup_possible (Optional: leave to False in most cases)
    # If True, the present_custom function can be called in a popup window.
    # Only used if you want to allow the user to see the data in a popup window
    # (for example, to provide more space for a large text input, or for an image viewer)
    # Note: if present_custom_popup_required is True, this flag is ignored
    present_custom_popup_possible: bool = False

    # edit: (Mandatory if edition is required)
    # Provide a draw function that presents an editable interface for the data, and returns True if changed.
    # If not provided, the data will be presented as read-only
    edit: BoolFunction | None = None

    # edit_popup_required (Optional: leave to False in most cases)
    # If True, the edit function needs to be called in a popup window.
    # This is due to a limitation of the node editor, which cannot render complex widgets
    # in the node itself.
    # By complex widgets, we mean widgets that require a scrollable area, or a child window, such as:
    #      - imgui.input_text_multiline
    #      - imgui.combo
    #      - imgui.begin_child
    edit_popup_required: bool = False

    # edit_popup_possible (Optional: leave to False in most cases)
    # If True, the edit function can be called in a popup window.
    # Only used if you want to allow the user to edit the data in a popup window
    # (for example, to provide more space for a large text input)
    # Note: if edit_popup_required is True, this flag is ignored
    edit_popup_possible: bool = False

    # default value provider (Mandatory if edition is required)
    # this function will be called to provide a default value if needed
    default_value_provider: Callable[[], DataType] | None = None

    # on_change (Optional)
    # if provided, this function will be called when the value changes.
    # Used in more advanced cases, when `present_custom` has an internal cache that needs to be updated.
    on_change: VoidFunction | None = None

    # save/load_gui_options_from_json (Optional)
    # Optional serialization and deserialization of the GUI presentation options
    # (i.e. anything that deals with how the data is presented in the GUI, not the data itself)
    # If provided, these functions will be used to recreate the GUI presentation options when loading a graph,
    # so that the GUI looks the same when the application is restarted.
    save_gui_options_to_json: Callable[[], JsonDict] | None = None
    load_gui_options_from_json: Callable[[JsonDict], None] | None = None

    # create_from_value (Optional)
    # Only used in more advanced cases, when the data type can not directly be constructed from a value.
    # (example: Enum when serialized as a string, when we need to convert the string back to the Enum class)
    create_from_value: Callable[[Any], DataType] | None = None

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
