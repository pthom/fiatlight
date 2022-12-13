from typing import Any
from imgui_bundle import imgui, imgui_node_editor, immapp
from fiatlux_py import IntWithGui, FunctionWithGui, FunctionsCompositionGraph


class AddWithGui(FunctionWithGui):
    what_to_add: int

    def __init__(self) -> None:
        self.what_to_add = 1
        self.input_gui = IntWithGui()
        self.output_gui = IntWithGui()

    def f(self, x: Any) -> int:
        assert type(x) == int
        return x + self.what_to_add

    def name(self) -> str:
        return "Add"

    def gui_params(self) -> bool:
        imgui.set_next_item_width(100)
        changed, self.what_to_add = imgui.slider_int("", self.what_to_add, 0, 10)
        return changed


def main() -> None:
    functions = [AddWithGui(), AddWithGui(), AddWithGui()]
    functions_graph = FunctionsCompositionGraph(functions)

    functions_graph.set_input(1)

    def gui() -> None:
        functions_graph.draw()

    config_node = imgui_node_editor.Config()
    config_node.settings_file = "demo_fn_compose_add.json"
    immapp.run(gui, with_node_editor_config=config_node, window_size=(800, 600), window_title="Additions")  # type: ignore


if __name__ == "__main__":
    main()
