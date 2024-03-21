from fiatlight.core import AnyDataWithGui, DataType, Unspecified, Error
from fiatlight import widgets
from imgui_bundle import imgui
from enum import Enum
from typing import Type


class OptionalWithGui(AnyDataWithGui[DataType | None]):
    inner_gui: AnyDataWithGui[DataType]

    def __init__(self, inner_gui: AnyDataWithGui[DataType]) -> None:
        super().__init__()
        self.inner_gui = inner_gui
        self.callbacks.present_str = self.present_str
        self.callbacks.edit = self.edit
        self.callbacks.on_change = self.on_change
        self.callbacks.default_value_provider = self.default_provider

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
            if imgui.is_item_hovered():
                widgets.osd_widgets.set_tooltip("Set Optional to default value for this type.")
            imgui.end_horizontal()
        else:
            imgui.begin_vertical("##OptionalV")
            imgui.begin_horizontal("##OptionalH")
            imgui.text("Optional: Set")
            if imgui.button("Unset"):
                self.value = None
                changed = True
            if imgui.is_item_hovered():
                widgets.osd_widgets.set_tooltip("Unset Optional.")
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

    def on_change(self) -> None:
        value = self.value
        assert not isinstance(value, (Unspecified, Error))
        if value is not None:
            self.inner_gui.value = value


class EnumWithGui(AnyDataWithGui[Enum]):
    enum_type: Type[Enum]

    def __init__(self, enum_type: Type[Enum]) -> None:
        super().__init__()
        self.enum_type = enum_type

        nb_values = len(list(self.enum_type))
        assert nb_values > 0

        self.callbacks.present = self.present
        self.callbacks.edit = self.edit
        self.callbacks.default_value_provider = lambda: list(self.enum_type)[0]

    def present(self) -> None:
        imgui.text(str(self.value))

    def edit(self) -> bool:
        assert not isinstance(self.value, (Unspecified, Error))
        changed = False

        for enum_value in list(self.enum_type):
            if imgui.radio_button(enum_value.name, self.value == enum_value):
                self.value = enum_value
                changed = True
        return changed


# ---------------------------- Sandbox ----------------------------
def sandbox_optional() -> None:
    from fiatlight import fiat_run, FunctionsGraph

    def foo(x: int | None) -> int:
        if x is None:
            return 0
        else:
            return x + 2

    graph = FunctionsGraph.from_function_composition([foo])
    fiat_run(graph)


def sandbox_enum() -> None:
    from fiatlight import fiat_run, FunctionsGraph

    class MyEnum(Enum):
        A = 1
        B = 2
        C = 3

    def foo(x: MyEnum) -> int:
        return x.value

    graph = FunctionsGraph.from_function_composition([foo], globals(), locals())
    fiat_run(graph)


if __name__ == "__main__":
    # sandbox_optional()
    sandbox_enum()
