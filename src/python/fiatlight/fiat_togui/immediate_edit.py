from imgui_bundle import imgui
from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui
from fiatlight.fiat_utils.value_per_imgui_frame import ValuePerImGuiFrame
from fiatlight.fiat_config import get_fiat_config
from .to_gui import to_data_with_gui
from typing import Any, TypeVar

SomeDataType = TypeVar("SomeDataType")


def immediate_edit(
    label_id: str,
    data: SomeDataType,
    force_refresh: bool = False,
    **fiat_attributes: Any,
) -> tuple[bool, SomeDataType]:
    """
    A generic immediate mode editing function: it can edit any
    data type that has a GUI representation in FiatLight.

    Args:
        label_id (str):
            label to be displayed in the GUI.
            Used as a unique ID (use push_id if needed, or a "##" suffix).
        data (SomeDataType):
            The data to be edited.
        force_refresh (bool):
            If True, the GUI will be refreshed with the current data value.
            (This is useful when the data is changed outside the GUI.)
            If False (default), the GUI might retain user editions
            that are still invalid (waiting for the user to fix them).
        **fiat_attributes (Any):
            Attributes to customize the GUI widget (depends on the data type)

    Returns:
       (changed, new_value)
       - changed (bool): True if the value was edited.
       - new_value: The updated value,
            or the original value if no changes were made
            or if the edited value is invalid.

    Alias:
        immedit is a shorter alias for immediate_edit
    """
    static = immediate_edit

    # Create a global cache if not already defined.
    if not hasattr(static, "GUI_CACHE"):
        static.GUI_CACHE: dict[int, AnyDataWithGui[SomeDataType]] = {}  # type: ignore # noqa
        static.USED_IDS_THIS_FRAME: ValuePerImGuiFrame[set[str]] = ValuePerImGuiFrame()  # type: ignore # noqa

    # # if edit_collapsible is not set in fiat_attributes, set it to False?
    # if "edit_collapsible" not in fiat_attributes:
    #     fiat_attributes["edit_collapsible"] = False

    get_fiat_config().style.update_colors_from_imgui_colors()

    # Look up the GUI wrapper using the label.
    imgui.push_id(label_id)
    cache_key = imgui.get_id(label_id)

    # Shout if we are reusing an id a second time in the same ImGui frame
    if static.USED_IDS_THIS_FRAME.get() is None:  # type: ignore
        static.USED_IDS_THIS_FRAME.set(set())  # type: ignore
    used_ids = static.USED_IDS_THIS_FRAME.get()  # type: ignore
    assert used_ids is not None
    if label_id in used_ids:
        raise ValueError(
            f"""
            When using `fiatlight.immediate_edit` make sure that label_id is unique!
                Used twice: "{label_id}"
            Hint: Use a unique suffix like "##" to avoid conflicts, or use push_id to create a unique id.
    """
        )
    used_ids.add(label_id)

    # Reuse GUI wrapper is already cached, otherwise create a new one.
    if cache_key in static.GUI_CACHE:  # type: ignore
        gui_wrapper = static.GUI_CACHE[cache_key]  # type: ignore
    else:
        # Create a new GUI wrapper and cache it.
        gui_wrapper = to_data_with_gui(data, label=label_id, **fiat_attributes)
        static.GUI_CACHE[cache_key] = gui_wrapper  # type: ignore

    if force_refresh:
        gui_wrapper.value = data

    # Render the GUI and check if the user has edited the value.
    changed = gui_wrapper.gui_edit()
    is_valid = gui_wrapper.has_valid_value()

    imgui.pop_id()

    if changed and is_valid:
        new_value = gui_wrapper.value
        # If the new value is a new instance, we might consider updating the cache.
        # For now, we assume the label remains constant.
        return changed, new_value
    else:
        return False, data


immedit = immediate_edit
