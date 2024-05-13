from fiatlight.fiat_types.base_types import DataType, ExplainedValues
from fiatlight.fiat_widgets import fiat_osd
from imgui_bundle import imgui, imgui_ctx
from typing import Tuple, Callable


def _edit_explained_value_impl(
    label_id: str, value: DataType, explained_values: ExplainedValues[DataType]
) -> Tuple[bool, DataType]:
    changed = False
    with imgui_ctx.begin_horizontal(label_id):
        for i, explained_value in enumerate(explained_values):
            selected = explained_value.value == value
            if imgui.radio_button(explained_value.label, selected):
                value = explained_value.value
                changed = True
            fiat_osd.set_widget_tooltip(explained_value.tooltip)
    return changed, value


def edit_explained_value(
    label_id: str, value: DataType, explained_values: ExplainedValues[DataType]
) -> tuple[bool, DataType]:
    changed, new_value = _edit_explained_value_impl(label_id, value, explained_values)
    return changed, new_value


def make_explained_value_edit_callback(
    label_id: str, explained_values: ExplainedValues[DataType]
) -> Callable[[DataType], Tuple[bool, DataType]]:
    def callback(value: DataType) -> tuple[bool, DataType]:
        return edit_explained_value(label_id, value, explained_values)

    return callback
