from fiatlight.fiat_config import get_fiat_config
from fiatlight.fiat_types import DataType, Unspecified, Error
from fiatlight.fiat_core import AnyDataWithGui
from fiatlight.fiat_widgets import fiat_osd
from imgui_bundle import hello_imgui, imgui, imgui_node_editor as ed  # noqa
from enum import Enum
from typing import Type, List


class OptionalWithGui(AnyDataWithGui[DataType | None]):
    inner_gui: AnyDataWithGui[DataType]

    def __init__(self, inner_gui: AnyDataWithGui[DataType]) -> None:
        super().__init__()
        self.can_be_none = True
        self.inner_gui = inner_gui
        self.callbacks.present_str = self.present_str
        self.callbacks.edit = self.edit
        self.callbacks.on_change = self.on_change
        self.callbacks.default_value_provider = self.default_provider
        self.callbacks.clipboard_copy_possible = inner_gui.callbacks.clipboard_copy_possible
        if self.inner_gui.callbacks.present_custom is not None:
            self.callbacks.present_custom = self.present_custom

    def default_provider(self) -> DataType | None:
        if self.inner_gui.callbacks.default_value_provider is None:
            return None
        else:
            return self.inner_gui.callbacks.default_value_provider()

    def present_str(self, value: DataType | None) -> str:
        if value is None:
            return "None"
        else:
            inner_present_str = self.inner_gui.callbacks.present_str
            if inner_present_str is not None:
                return inner_present_str(value)
            else:
                return str(value)

    def present_custom(self, value: DataType | None) -> None:
        assert self.inner_gui.callbacks.present_custom is not None
        if value is None:
            imgui.text("Optional: None")
        else:
            self.inner_gui.value = value
            self.inner_gui.callbacks.present_custom(value)

    def edit(self) -> bool:
        value = self.value
        assert not isinstance(value, (Unspecified, Error))

        changed = False

        if value is None:
            imgui.begin_horizontal("##OptionalH")
            imgui.text("Optional: None")
            if imgui.button("Set"):
                default_value_provider = self.inner_gui.callbacks.default_value_provider
                assert default_value_provider is not None
                self.value = default_value_provider()
                changed = True
            fiat_osd.set_widget_tooltip("Set Optional to default value for this type.")
            imgui.end_horizontal()
        else:
            imgui.begin_vertical("##OptionalV")
            imgui.begin_horizontal("##OptionalH")
            imgui.text("Optional: Set")
            if imgui.button("Unset"):
                self.value = None
                changed = True
            fiat_osd.set_widget_tooltip("Unset Optional.")
            imgui.end_horizontal()
            fn_edit = self.inner_gui.callbacks.edit
            if fn_edit is not None:
                changed_in_edit = fn_edit()
                if changed_in_edit:
                    self.value = self.inner_gui.value
                    changed = True
            else:
                imgui.text("No edit function!")
            imgui.end_vertical()

        return changed

    def on_change(self, value: DataType | None) -> None:
        if value is not None:
            self.inner_gui.value = value


class ListWithGui(AnyDataWithGui[List[DataType]]):
    inner_gui: AnyDataWithGui[DataType]

    popup_max_elements: int = 300
    show_idx: bool = True

    def __init__(self, inner_gui: AnyDataWithGui[DataType]) -> None:
        super().__init__()
        self.inner_gui = inner_gui
        self.callbacks.present_str = self.present_str
        self.callbacks.edit = self.edit
        self.callbacks.default_value_provider = lambda: []
        self.callbacks.present_custom = self.present_custom
        self.callbacks.clipboard_copy_str = self.clipboard_copy_str
        self.callbacks.clipboard_copy_possible = inner_gui.callbacks.clipboard_copy_possible

    @staticmethod
    def clipboard_copy_str(v: List[DataType]) -> str:
        return str(v)

    def _elements_str(self, value: List[DataType], max_presented_elements: int) -> str:
        nb_elements = len(value)
        nb_digits = len(str(nb_elements))
        strings = []
        for i, element in enumerate(value):
            value_str = self.inner_gui.datatype_value_to_str(element)
            idx_str = str(i).rjust(nb_digits, "0")
            if i >= max_presented_elements:
                strings.append(f"...{nb_elements - max_presented_elements} more elements")
                break
            if self.show_idx:
                strings.append(f"{idx_str}: {value_str}")
            else:
                strings.append(value_str)
        return "\n".join(strings)

    def present_str(self, value: List[DataType]) -> str:
        nb_elements = len(value)
        if nb_elements == 0:
            return "Empty list"
        r = f"List of {nb_elements} elements\n" + self._elements_str(
            value, get_fiat_config().style.list_maximum_elements_in_node
        )
        return r

    def edit(self) -> bool:  # noqa
        imgui.text("Edit not implemented for ListWithGui")
        return False

    def popup_details(self) -> None:
        assert not isinstance(self.value, (Unspecified, Error))
        imgui.text("List elements")
        _, self.show_idx = imgui.checkbox("Show index", self.show_idx)
        txt = self._elements_str(self.value, self.popup_max_elements)
        imgui.input_text_multiline("##ListElements", txt, hello_imgui.em_to_vec2(0, 20))

        if self.popup_max_elements < len(self.value):
            if imgui.button("Show more"):
                self.popup_max_elements += 300

    def present_custom(self, value: List[DataType]) -> None:
        max_elements = get_fiat_config().style.list_maximum_elements_in_node

        fiat_osd.show_void_detached_window_button(
            "Details",
            "List details",
            self.popup_details,
        )

        txt = self._elements_str(value, max_elements)
        imgui.text(txt)


class EnumWithGui(AnyDataWithGui[Enum]):
    enum_type: Type[Enum]

    def __init__(self, enum_type: Type[Enum]) -> None:
        super().__init__()
        self.enum_type = enum_type

        nb_values = len(list(self.enum_type))
        assert nb_values > 0

        self.callbacks.edit = self.edit
        self.callbacks.default_value_provider = lambda: list(self.enum_type)[0]
        self.callbacks.create_from_value = self.create_from_name
        self.callbacks.clipboard_copy_possible = True

    def edit(self) -> bool:
        assert not isinstance(self.value, (Unspecified, Error))
        changed = False

        for enum_value in list(self.enum_type):
            if imgui.radio_button(enum_value.name, self.value == enum_value):
                self.value = enum_value
                changed = True
        return changed

    def create_from_name(self, name: str) -> Enum:
        return self.enum_type[name]


# ---------------------------- Sandbox ----------------------------
def sandbox_optional() -> None:
    from fiatlight import fiat_run_graph, FunctionsGraph

    def foo(x: int | None) -> int:
        if x is None:
            return 0
        else:
            return x + 2

    graph = FunctionsGraph.from_function_composition([foo])
    fiat_run_graph(graph)


def sandbox_enum() -> None:
    from fiatlight import fiat_run_graph, FunctionsGraph

    class MyEnum(Enum):
        A = 1
        B = 2
        C = 3

    def foo(x: MyEnum) -> int:
        return x.value

    graph = FunctionsGraph.from_function_composition([foo])
    fiat_run_graph(graph)


if __name__ == "__main__":
    # sandbox_optional()
    sandbox_enum()
