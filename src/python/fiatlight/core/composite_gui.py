from fiatlight.core import AnyDataWithGui, DataType, Unspecified, Error
from imgui_bundle import imgui
from enum import Enum
from typing import Type


class OptionalWithGui(AnyDataWithGui[DataType | None]):
    inner_gui: AnyDataWithGui[DataType]

    def __init__(self, inner_gui: AnyDataWithGui[DataType]) -> None:
        super().__init__()
        self.inner_gui = inner_gui
        self.callbacks.present = self.present
        self.callbacks.edit = self.edit
        self.callbacks.on_change = self.on_change
        self.callbacks.default_value_provider = lambda: None

    def present(self) -> None:
        value = self.value
        if value is None:
            imgui.text("None")
        else:
            assert not isinstance(value, (Unspecified, Error))
            self.inner_gui.value = value
            self.inner_gui.call_gui_present()

    def edit(self) -> bool:
        value = self.value
        assert not isinstance(value, (Unspecified, Error))

        if value is None:
            imgui.text("Optional: None")
            imgui.same_line()
            if imgui.button("Set"):
                default_value_provider = self.inner_gui.callbacks.default_value_provider
                assert default_value_provider is not None
                self.value = default_value_provider()
                return True
            return False
        else:
            imgui.text("Optional: Set")
            imgui.same_line()
            if imgui.button("Unset"):
                self.value = None
                return True
            changed = self.inner_gui.call_gui_edit(display_trash=False)
            if changed:
                self.value = self.inner_gui.value
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
