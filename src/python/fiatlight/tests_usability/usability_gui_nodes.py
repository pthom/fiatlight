"""Usability example for GUI nodes

This usability example will show how to use GUI nodes in Fiatlight.
It uses the class GuiNode (a specialization of FunctionWithGui) to display GUI functions in the function graph.

GuiNode can be created from a GUI function that takes no parameters, or from a GUI function that takes inputs.
A Gui function has this signature:

    GuiFunctionWithInputs = Callable[..., None]

What to verify:

- The GUI functions are displayed in the GUI.
- The GUI functions are called at each frame.
- The GUI functions take into account the input values.
- Upon restarting, the application should reload the last factor value.
- The output of a standard function can be customized via Fiatlight callbacks:
  check that the output of the x_times_2_gui function is displayed correctly.
"""

import fiatlight as fl
from imgui_bundle import imgui
from pydantic import BaseModel


def input_x(x: int) -> int:
    """a function that will be displayed in the function graph, in order to let the user input a value."""
    return x


#
def x_times_2(x: int) -> int:
    """A standard function that multiplies the input by 2.
    It uses the standard Fiatlight principle: it is called only when the input changes,
    and Fiatlight will take care of the GUI for the output.
    """
    return x * 2


# ========================== GUI FUNCTIONS ==========================
def gui_no_param() -> None:
    """A GUI function that will be displayed in the function graph.
    It will be added via graph.add_gui_node(gui_no_param).
    """
    imgui.text("This is a GUI function with no parameters.")


def gui_x_times_2(x: int) -> None:
    """A GUI function that displays the result of the multiplication by 2.
    It will be added via graph.add_gui_node(gui_x_times_2).
    It returns nothing because it is a GUI function.
    It will be called at each frame (i.e. 120 times per second for example)
    """
    imgui.text(f"Here is the result: x * 2 ={x * 2}")


class WhatToMultiply(BaseModel):
    """A serializable data class that will be used to store the options of the GUI function `gui_x_times_factor"""

    factor: int = 3


WHAT_TO_MULTIPLY = WhatToMultiply()


def gui_x_times_factor(x: int) -> None:
    """A GUI function that multiplies the input by a serializable factor.
    It will be added via graph.add_gui_node(gui_x_times_factor, gui_serializable_data=WHAT_TO_MULTIPLY).
    It uses a serializable data class to store its options, which will be reloaded upon restarting the application.
    """
    _, WHAT_TO_MULTIPLY.factor = imgui.input_int("Factor", WHAT_TO_MULTIPLY.factor)
    imgui.text(f"Multiply by a factor: x * {WHAT_TO_MULTIPLY.factor} ={x * WHAT_TO_MULTIPLY.factor}")


# =========== MAIN ===========

# Create a new graph
graph = fl.FunctionsGraph()

# Add the input function to the graph
graph.add_function(input_x)
# Add the function that multiplies the input by 2 (a standard Fiatlight function) and link it to the input function
graph.add_function(x_times_2)
graph.add_link(input_x, x_times_2)

# Add the GUI function with no parameters to the graph
graph.add_gui_node(gui_no_param)

# Add the gui function that displays the result of the multiplication by 2 and link it to the input function
graph.add_gui_node(gui_x_times_2)
graph.add_link(input_x, gui_x_times_2)

# Add the GUI function that multiplies the input by a serializable factor and link it to the input function
graph.add_gui_node(gui_x_times_factor, gui_serializable_data=WHAT_TO_MULTIPLY)
graph.add_link(input_x, gui_x_times_factor)

# As an example, we here show that the way the output of a standard function (x_times_2) is presented
# can also be heavily customized via Fiatlight callbacks.
x_times_2_gui = fl.FunctionWithGui(x_times_2)
x_times_2_gui.output().callbacks.present = lambda value: imgui.text_wrapped(
    f"This is a customized present callback\n{value=}"
)

# Run the graph
fl.run(graph)
