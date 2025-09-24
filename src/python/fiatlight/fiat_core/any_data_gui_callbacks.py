from fiatlight.fiat_types.base_types import DataType, JsonDict, FiatAttributes
from fiatlight.fiat_types.function_types import VoidFunction, BoolFunction
from typing import Callable, Generic


class AnyDataGuiCallbacks(Generic[DataType]):
    """AnyDataGuiCallbacks: Collection of callbacks for a given type

    AnyDataGuiCallbacks
    ===================

    This class provides a set of callbacks that define how a particular data type should be
    presented, edited, and managed within the Fiatlight GUI framework.

    These callbacks are used by [AnyDataWithGui](any_data_with_gui).
    """

    # Note about Node Editor compatibility
    # ------------------------------------
    #   - Child windows, and widgets that open a child window are *incompatible*
    #     with being rendered in a node. If you need to use them, open a popup and
    #     render them there.
    #   - `imgui.input_text_multiline` was made compatible by adding a "..." button
    #     to open the multiline editor in a popup
    #   - You can query `fiatlight.is_rendering_in_node()` to know if you are rendering in a node.
    #   - When inside a Node, you may want to render a smaller version, to save space
    #   - Widgets that open a popup are compatible with being rendered in a node

    #                        Presentation
    # ---------------------------------------------------------------------------------------------
    # present_str: (Mandatory if str() is not enough, optional otherwise)
    # Provide a function that returns a short string info about the data content
    # This string will be presented as a short description of the data in the GUI
    #
    # If possible, it should be short enough to fit in a single line inside a node (40 chars max).
    # If the result string is too long, or occupies more than one line, it will be truncated and followed by "..."
    # (and the rest of the string will be displayed in a tooltip)
    # For example, on complex types such as images, return something like "128x128x3 uint8"
    # If not provided, the data will be presented using str()
    present_str: Callable[[DataType], str] | None = None

    # present: (Optional)
    # a function that provides a more complex, custom GUI representation of the data. Used for detailed views.
    # It will be presented when a function param is in "expanded" mode, and can use imgui widgets on several lines.
    # If not provided, the data will be presented using present_str
    present: Callable[[DataType], None] | None = None

    # present_collapsible:
    # Set this to False if your custom presentation is small and fits in one line
    # (i.e. it does not need to be collapsible)
    # If True, the gui presentation will either:
    #     - show present_str + an expand button
    #     - show the custom presentation + a collapse button
    present_collapsible: bool = True

    # present_detachable
    # Set this to True if your custom presentation is complex
    # and would benefit from being shown in a separate window
    # (in this case, a button will be added for that)
    present_detachable: bool = False

    # ---------------------------------------------------------------------------------------------

    #                        Edition
    # ---------------------------------------------------------------------------------------------
    # edit: (Mandatory if edition is required)
    # Provide a function that presents an editable interface for the data, and returns
    #     (True, new_value) if changed
    #     (False, old_value) if not changed
    # If not provided, the data will be presented as read-only
    edit: Callable[[DataType], tuple[bool, DataType]] | None = None

    # edit_collapsible:
    # Set this to False if your custom edition is small, and does not need to be collapsible (i.e. it fits one line)
    # If True, the gui edition will either:
    #     - show present_str + an expand button
    #     - show the custom edition + a collapse button
    edit_collapsible: bool = True

    # edit_detachable
    # Set this to True if your custom edition is complex
    # and would benefit from being shown in a separate window
    # (in this case, a button will be added for that)
    edit_detachable: bool = False

    # ---------------------------------------------------------------------------------------------

    #                        Default value
    # ---------------------------------------------------------------------------------------------
    # default value provider (Needed only for a type without default constructor)
    # this function will be called to provide a default value if needed
    default_value_provider: Callable[[], DataType] | None = None
    # ---------------------------------------------------------------------------------------------

    #                        Events callbacks
    # ---------------------------------------------------------------------------------------------
    # on_change (Optional)
    # if provided, this function will be called when the value changes
    # (iif the value was changed, and is not Error/Unspecified/Invalid)
    # Can be used in more advanced cases,
    # for example when `present` has an internal cache that needs to be updated,
    # or other side effects.
    on_change: Callable[[DataType], None] | None = None

    # validators (Optional)
    # List of functions that will be called when the user tries to set a value.
    # You can add to it a validation function to check if the value is valid:
    #     - It should raise a ValueError exception with a nice error message if the value is invalid.
    #       (the error message will be shown to the user)
    #     - It should return the value if it is valid (or a modified version of it)
    validators: list[Callable[[DataType], DataType]]

    # on_exit (Optional)
    # if provided, this function will be called when the application is closed.
    # Used in more advanced cases, typically when some resources need to be released.
    on_exit: VoidFunction | None = None

    # on_heartbeat: (Optional)
    # If provided, this function will be called at each heartbeat of the function node.
    # (before the value is drawn). It should return True if any change has been made to the data.
    on_heartbeat: BoolFunction | None = None

    # on_fiat_attributes_changed (Optional)
    # if provided, this function will be called when the fiat attributes of the data change.
    # Used in more advanced cases, when the data presentation depends on fiat attributes.
    on_fiat_attributes_changed: Callable[[FiatAttributes], None] | None = None

    # ---------------------------------------------------------------------------------------------

    #                        Serialization and deserialization
    # ---------------------------------------------------------------------------------------------
    # Of the GUI presentation options (not the data itself)
    #
    # save/load_gui_options_from_json (Optional)
    # Optional serialization and deserialization of the GUI presentation options
    # (i.e. anything that deals with how the data is presented in the GUI, *not the data itself*)
    # If provided, these functions will be used to recreate the GUI presentation options when loading a graph,
    # so that the GUI looks the same when the application is restarted.
    save_gui_options_to_json: Callable[[], JsonDict] | None = None
    load_gui_options_from_json: Callable[[JsonDict], None] | None = None

    # Of the data itself
    #
    # Optional serialization and deserialization functions for DataType
    # If provided, these functions will be used to serialize and deserialize the data with a custom dict format.
    # If not provided, "value" will be serialized as a dict of its __dict__ attribute,
    # or as a json string (for int, float, str, bool, and None)
    save_to_dict: Callable[[DataType], JsonDict] | None = None
    load_from_dict: Callable[[JsonDict], DataType] | None = None
    # ---------------------------------------------------------------------------------------------

    #                        Clipboard
    # ---------------------------------------------------------------------------------------------
    # clipboard_copy_str (Optional)
    # if provided, this function will be called when the value is copied to the clipboard.
    # Used in more advanced cases, when the data is not a simple string, or when present_str or str() is not enough.
    clipboard_copy_str: Callable[[DataType], str] | None = None

    # clipboard_copy_possible (Optional)
    # True by default
    # If False, the user can not copy the data to the clipboard
    clipboard_copy_possible: bool = True
    # ---------------------------------------------------------------------------------------------

    def __init__(self) -> None:
        self.validators = []
