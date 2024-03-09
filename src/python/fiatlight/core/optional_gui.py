from fiatlight.core import AnyDataWithGui, DataType, Unspecified, Error
from imgui_bundle import imgui


class OptionalWithGui(AnyDataWithGui[DataType | None]):
    inner_gui: AnyDataWithGui[DataType]

    def __init__(self, inner_gui: AnyDataWithGui[DataType]) -> None:
        super().__init__()
        self.inner_gui = inner_gui
        self.callbacks.present = self.present
        self.callbacks.edit = self.edit
        self.callbacks.on_change = self.on_change
        self.callbacks.default_value_provider = lambda: None

    def present(self):
        value = self.value
        if value is None:
            imgui.text("None")
        else:
            assert not isinstance(value, (Unspecified, Error))
            self.inner_gui.value = self.value
            self.inner_gui.call_gui_present()

    def edit(self) -> bool:
        value = self.value
        assert not isinstance(value, (Unspecified, Error))

        if value is None:
            imgui.text("Optional: None")
            imgui.same_line()
            if imgui.button("Set"):
                self.value = self.inner_gui.callbacks.default_value_provider()
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


# ---------------------------- Sandbox ----------------------------
def sandbox() -> None:
    from fiatlight import fiat_run, FunctionsGraph

    def foo(x: int | None) -> int:
        if x is None:
            return 0
        else:
            return x + 2

    graph = FunctionsGraph.from_function_composition([foo])
    fiat_run(graph)


if __name__ == "__main__":
    sandbox()
