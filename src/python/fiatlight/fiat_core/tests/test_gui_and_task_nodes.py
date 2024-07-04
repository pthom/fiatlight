import fiatlight as fl
from imgui_bundle import imgui
import time
import pytest


def test_refuse_no_output() -> None:
    # A function that returns nothing should not be accepted as a GUI function
    # unless it is a task or a GUI function
    def f() -> None:
        pass

    with pytest.raises(fl.FiatToGuiException):
        _f_gui = fl.FunctionWithGui(f)

    def f2(_x: int) -> None:
        pass

    with pytest.raises(fl.FiatToGuiException):
        _f_gui = fl.FunctionWithGui(f2)


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


def test_task_node() -> None:
    def task_function(x: int) -> None:
        time.sleep(0.1)
        print(f"Task function: {x}")

    task_node = fl.TaskNode(task_function)

    assert task_node.function_name == "task_function"
    assert task_node.label == "task_function"
