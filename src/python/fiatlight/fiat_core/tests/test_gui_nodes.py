import fiatlight as fl
from imgui_bundle import imgui


def test_gui_node() -> None:
    def gui_function() -> None:
        imgui.text("This is a GUI function")

    gui_node = fl.GuiNode(gui_function)

    assert gui_node.function_name == "gui_function"

    # A function with an input should be accepted as a GUI function
    def gui_function_with_input(x: int) -> None:
        imgui.text(f"Input: {x}")

    gui_node_with_input = fl.GuiNode(gui_function_with_input)

    assert gui_node_with_input.function_name == "gui_function_with_input"
