"""Sorting Algorithm Competition
================================
This program shows a competition between different sorts algorithms.

**"gui_latency" node**

In this node you can set the speed of memory access: this drastically reduces the speed of the algorithms,
so that you can visually see their behavior. The latency can be changed while the sorting algorithms are running.

You can also stop the sorting algorithms in their tracks (a slight delay might be needed)

**"make_random_number_list" node**

In this node you can generate the list that will be sorted with different shapes.
Click on "Call Manually" to generate a new list.

** **Other nodes**

The other function nodes will show various sorting algorithms. You can see their status in real time.
Their output is the total execution time after the sorting is finished.
"""

import fiatlight as fl
from fiatlight.demos.tutorials.sort_competition.numbers_generator import make_random_number_list
from fiatlight.demos.tutorials.sort_competition.sort_algorithms import (
    bubble_sort,
    selection_sort,
    insertion_sort,
    merge_sort,
    quick_sort,
    quick_sort_median_of_three,
)
from fiatlight.demos.tutorials.sort_competition.number_list import NumbersList
from imgui_bundle import hello_imgui, imgui_ctx, implot, imgui
import time
from typing import Callable


def draw_bars(numbers: NumbersList) -> None:
    """Draw a bar chart of the numbers"""

    # The ID passed to implot.begin_plot should be unique, or use ##
    # As an alternative, we can use imgui_ctx.push_obj_id to change the ImGui ID context before calling begin_plot
    with imgui_ctx.push_obj_id(numbers):
        # In order to have a plot size which is independent of the screen DPI scaling,
        # we will specify its size in EM units. 1 EM unit is the height of the font.
        plot_size = hello_imgui.em_to_vec2(25, 15)

        # Draw our plot (only if begin_plot returns True)
        # The title should be unique!!! Solutions:
        #    - either use a title like "Label##SomeHiddenId"
        #    - or imgui_ctx.push_obj_id(some_object))
        if implot.begin_plot(title_id="Numbers", size=plot_size):
            # With those two lines we ensure that the plotted values will always be fully visible,
            # even if  their range changes after the initial drawing.
            axis_flags = implot.AxisFlags_.auto_fit.value
            implot.setup_axes(x_label="x", y_label="y", x_flags=axis_flags, y_flags=axis_flags)

            # Draw the set of numbers as a bar chart
            implot.plot_bars(label_id="", values=numbers.values)

            # Don't forget to call end_plot (iif begin_plot returned True)
            implot.end_plot()


class NumbersListWithGui(fl.AnyDataWithGui[NumbersList]):
    """NumbersListWithGui is used to present a NumbersList object. It does so by inheriting from AnyDataWithGui.
    In this case, we only want to change how this data is presented, and thus it is enough to set the present callback.
    """

    def __init__(self) -> None:
        super().__init__(NumbersList)
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
    @fl.with_fiat_attributes(invoke_async=True)
    def sort_wrapper(numbers: NumbersList) -> float:
        """Wrapper function of the sort function that visually track the current status and returns the elapsed time"""

        # Start a timer, to measure the elapsed time
        start_time = time.time()

        # We make a copy of the numbers because we do not want to modify the original set of numbers
        numbers_being_sorted = numbers.copy()

        # Add the current status to the fiat_tuning dictionary:
        # we simply add an attribute `fiat_tuning` to the function.
        # Notes:
        # - At each frame, Fiatlight will display the content of this dictionary.
        #   (even if the function is running asynchronously!)
        # - Inside this dictionary we can store:
        #   - either raw values (int, float, string, etc.)
        #   - or instance of classes that inherit from AnyDataWithGui
        # Step 1: create an instance of NumbersListWithGui
        current_status_gui = NumbersListWithGui()
        # The GUI will show the numbers being sorted (and they will be updated in the background)
        current_status_gui.value = numbers_being_sorted
        # Step 2: add the instance to the fiat_tuning dictionary
        fl.add_fiat_attributes(sort_wrapper, fiat_tuning={"sort_status": current_status_gui})

        # Finally call our sorting function
        # (the sorting function will modify the numbers_being_sorted in place,
        #  so that the sort_status GUI will be updated in real time)
        _sorted_numbers = sort_function(numbers_being_sorted)

        # Return the elapsed time
        return time.time() - start_time

    # Preserve the original function name and docstring, so that they can be displayed in the functions graph
    sort_wrapper.__doc__ = sort_function.__doc__
    sort_wrapper.__name__ = sort_function.__name__ + " visualization"
    return sort_wrapper


def gui_latency() -> None:
    """A GUI function to set the latency of the sorting algorithms"""
    from fiatlight.demos.tutorials.sort_competition.number_list import set_latency, get_latency

    latency_us = get_latency() * 1000000.0

    # Edit the latency via a slider
    # First we need to set its width because sliders will occupy the full window width by default
    # (the window width is much larger than the function node)
    # We will specify this within EM units. 1 EM unit is the height of the font.
    imgui.set_next_item_width(hello_imgui.em_size(10))
    changed, latency_ms = imgui.slider_float("Latency (us)", latency_us, 0.0, 50.0)

    if changed:
        set_latency(latency_ms / 1000000)

    # Also, abort
    from fiatlight.demos.tutorials.sort_competition.sort_algorithms import is_aborting, set_aborting

    if not is_aborting():
        if imgui.button("Abort Sort"):
            set_aborting(True)
    else:
        if imgui.button("Enable Sort"):
            set_aborting(False)


# ---------                   Main part of the script                   --------- #


# Here we register the type NumbersList with its GUI
fl.register_type(NumbersList, NumbersListWithGui)

# Now, run the function composition with Fiatlight
#   First, make sure that the GUI is updated as quickly as possible:
#     disable idling, to make animations smoother, even when the user is not interacting with the GUI
gui_params = fl.FiatRunParams(enable_idling=False)

# Create a FunctionGraph
graph = fl.FunctionsGraph()
# add the random numbers generator, and make its invocation manual...
fl.add_fiat_attributes(make_random_number_list, invoke_manually=True, invoke_always_dirty=True)
graph.add_function(make_random_number_list, label="Generate random numbers")
# Then add all the sorting algorithms, and link them to the random numbers generator
sort_functions = [bubble_sort, selection_sort, insertion_sort, merge_sort, quick_sort, quick_sort_median_of_three]
for sort_function in sort_functions:
    sort_view = make_sort_function_visualizer(sort_function)
    graph.add_function(sort_view)
    graph.add_link(make_random_number_list, sort_view)
# Add a GUI only node to set the latency
graph.add_gui_node(gui_latency, label="Set Latency")
# # Add a documentation node (which will display the docstring of this script)
graph.add_markdown_node(__doc__, label="Sort Competition", text_width_em=15)
# Finally run the graph with the given parameters
fl.run(graph, params=gui_params)
