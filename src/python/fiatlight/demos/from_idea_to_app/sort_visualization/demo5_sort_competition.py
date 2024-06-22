"""An interactive visualization of different sorting algorithms, using Fiatlight
"""

from typing import Callable

import fiatlight as fl
from imgui_bundle import implot, hello_imgui, imgui_ctx, imgui
from fiatlight.demos.from_idea_to_app.sort_visualization.number_list import NumbersList
from fiatlight.demos.from_idea_to_app.sort_visualization.numbers_generator import make_random_number_list
from fiatlight.demos.from_idea_to_app.sort_visualization.sort_algorithms import (
    bubble_sort,
    selection_sort,
    insertion_sort,
    merge_sort,
    quick_sort,
)
import time


def draw_bars(numbers: NumbersList) -> None:
    """Draw a bar chart of the numbers"""

    # The ID passed to implot.begin_plot should be unique, or use ##
    # As an alternative, you can use imgui_ctx.push_obj_id
    with imgui_ctx.push_obj_id(numbers):
        # We will specify the block size
        # In order to have a size which is independent of the screen DPI scaling,
        # We will specify the size in EM units. 1 EM unit is the height of the font.
        plot_size = hello_imgui.em_to_vec2(25, 15)

        # Draw our plot (only if begin_plot returns True)
        # 3.1 Show definition of begin_plot:
        #    - the return value of begin_plot is a boolean
        #    - the title should be unique or (use ## or push_id)
        if implot.begin_plot("Numbers", plot_size):
            # With those two lines we ensure that the plotted values will always be fully visible,
            # even if  their range changes after the initial drawing.
            axis_flags = implot.AxisFlags_.auto_fit.value
            implot.setup_axes("x", "y", axis_flags, axis_flags)
            # Draw the set of numbers as a bar chart
            implot.plot_bars("", numbers.values)
            # Don't forget to call end_plot (iif begin_plot returned True)
            implot.end_plot()


class NumbersListWithLatency_Gui(fl.AnyDataWithGui[NumbersList]):
    """NumbersListWithLatency_Gui is used to present a NumbersList object.
    It does so by inheriting from AnyDataWithGui and setting the present callback to draw_bars.
    """

    def __init__(self) -> None:
        super().__init__(NumbersList)
        # Show how to set the present callback
        self.callbacks.present = draw_bars


def make_sort_function_visualizer(
    sort_function: Callable[[NumbersList], NumbersList],
) -> Callable[[NumbersList], float]:
    """Higher order function to create a wrapper function for a sorting function that
    - adds a Fiat tuning dictionary to visually track the current status of the numbers
    - returns the elapsed time in seconds
    """

    # We use the decorator with_fiat_attributes to add an attribute "invoke_async=True" to the function
    # With this attribute, the function will be called asynchronously, so that the GUI can be updated
    # while the function is running
    @fl.with_fiat_attributes(invoke_async=True, label=sort_function.__name__ + " - view")
    def sort_wrapper(numbers: NumbersList) -> float:
        # Start a timer, to measure the elapsed time
        start_time = time.time()

        # We need to make a copy of the numbers because we will be modifying them,
        # and we do not want to modify the original set of numbers
        numbers_being_sorted = numbers.copy()

        # Add the current status to the fiat_tuning dictionary:
        # we simply add a static attribute `fiat_tuning` to the function.
        # Notes:
        # - At each frame, Fiatlight will display the content of this dictionary.
        #   (even if the function is running asynchronously!)
        # - Inside this dictionary we can store:
        #   - either raw values (int, float, string, etc.)
        #   - or instance of classes that inherit from AnyDataWithGui
        # Step 1: create an instance of NumbersListWithLatency_Gui
        current_status_gui = NumbersListWithLatency_Gui()
        # The GUI will show the numbers being sorted.
        # (and they will be updated in the background by the sorting function)
        current_status_gui.value = numbers_being_sorted
        # Step 2: add the instance to the fiat_tuning dictionary
        # (we need to add type: ignore because the fiat_tuning attribute
        # is not expected by type checkers such as mypy)
        sort_wrapper.fiat_tuning = {  # type: ignore
            "sort_status": current_status_gui
        }

        # Finally call our sorting function
        # (the sorting function will modify the numbers_being_sorted in place,
        #  so that the sort_status GUI will be updated in real time)
        _sorted_numbers = sort_function(numbers_being_sorted)

        # Return the elapsed time
        return time.time() - start_time

    sort_function_visualizer = sort_wrapper
    # sort_function_visualizer.__name__ = sort_function.__name__ + " visualization"
    return sort_function_visualizer


# Here we register the type NumbersList with its GUI NumbersListWithLatency_Gui
fl.register_type(NumbersList, NumbersListWithLatency_Gui)


def gui_latency() -> None:
    """A GUI function to set the latency of the sorting algorithms"""
    from fiatlight.demos.from_idea_to_app.sort_visualization.number_list import set_latency, get_latency

    latency_us = get_latency() * 1000000.0
    # Edit the latency via a slider
    # First we need to set its width because sliders will occupy the full window width by default
    # (the window width is much larger than the function node)
    # We will specify this within EM units. 1 EM unit is the height of the font.
    imgui.set_next_item_width(hello_imgui.em_size(10))
    changed, latency_ms = imgui.slider_float("Latency (us)", latency_us, 0.0, 1000.0)

    if changed:
        set_latency(latency_ms / 1000000)

    # Also, abort
    from fiatlight.demos.from_idea_to_app.sort_visualization.sort_algorithms import is_aborting, set_aborting

    if not is_aborting():
        if imgui.button("Abort Sort"):
            set_aborting(True)
    else:
        if imgui.button("Enable Sort"):
            set_aborting(False)


# Disable idling, to make animations smoother
gui_params = fl.FiatGuiParams()
gui_params.runner_params.fps_idling.enable_idling = False
# Create a FunctionGraph and add the random numbers generator
graph = fl.FunctionsGraph()
graph.add_function(make_random_number_list)
# Then add all the sorting algorithms, and link them to the random numbers generator
sort_functions = [bubble_sort, selection_sort, insertion_sort, merge_sort, quick_sort]
for sort_function in sort_functions:
    sort_view = make_sort_function_visualizer(sort_function)
    graph.add_function(sort_view)
    graph.add_link(make_random_number_list, sort_view)
# Add a GUI only node to set the latency
graph.add_gui_node(gui_latency)
# Finally run the graph with the given parameters
fl.run(graph, params=gui_params)
