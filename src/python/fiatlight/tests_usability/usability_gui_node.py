"""Usability example of a GUI node with serializable data.

Upon restarting, the application should reload the last values of the GUI options.
"""

import fiatlight as fl
from imgui_bundle import imgui
from pydantic import BaseModel


class MyGuiOptions(BaseModel):
    my_int: int = 42


MY_GUI_OPTIONS = MyGuiOptions()


def my_gui() -> None:
    imgui.text("Hello, world!")
    _, MY_GUI_OPTIONS.my_int = imgui.input_int("My int", MY_GUI_OPTIONS.my_int)


graph = fl.FunctionsGraph()
graph.add_gui_node(my_gui, gui_serializable_data=MY_GUI_OPTIONS)
fl.run(graph)
