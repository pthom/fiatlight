"""# Sorting Algorithm Competition - Condensed version: 53 non-empty GUI code lines """
# fmt: off
from typing import Callable
import fiatlight as fl
from imgui_bundle import implot, hello_imgui, imgui_ctx, imgui
from fiatlight.demos.tutorials.sort_competition.number_list import NumbersList, set_latency, get_latency
from fiatlight.demos.tutorials.sort_competition.numbers_generator import make_random_number_list
from fiatlight.demos.tutorials.sort_competition.sort_algorithms import bubble_sort, selection_sort, insertion_sort, merge_sort, quick_sort, quick_sort_median_of_three, is_aborting, set_aborting
import time


def draw_bars(numbers: NumbersList) -> None:
    with imgui_ctx.push_obj_id(numbers):
        plot_size = hello_imgui.em_to_vec2(25, 15)  # specify the plot size in EM units
        if implot.begin_plot("Numbers", plot_size):  # always draw plots between begin_plot and end_plot
            axis_flags = implot.AxisFlags_.auto_fit.value  # ensure that the plotted values will always be fully visible
            implot.setup_axes("x", "y", axis_flags, axis_flags)
            implot.plot_bars("", numbers.values)  # draw the set of numbers as a bar chart
            implot.end_plot()


class NumbersListWithLatency_Gui(fl.AnyDataWithGui[NumbersList]):  # A class which presents a NumbersList object
    def __init__(self) -> None:  # And which will be registered as the GUI for NumbersList
        super().__init__(NumbersList)
        self.callbacks.present = draw_bars  # We only need to set the present callback to draw_bars


def make_sort_function_visualizer(sort_fn: Callable[[NumbersList], NumbersList]) -> Callable[[NumbersList], float]:
    """Returns a wrapper function which will sort, add real-time visualization, and return elapsed time"""
    @fl.with_fiat_attributes(invoke_async=True, label=sort_fn.__name__ + " - view")
    def sort_wrapper(numbers: NumbersList) -> float:
        start_time = time.time()  # start the timer
        numbers_being_sorted = numbers.copy()  # copy the list, so that each algorithm sorts its own list
        current_status_gui = NumbersListWithLatency_Gui()  # instantiate a GUI for real-time visualization, which will
        current_status_gui.value = numbers_being_sorted  # display the numbers (which are updated in a separate thread)
        fl.add_fiat_attributes(sort_wrapper, fiat_tuning={"sort_status": current_status_gui})
        _sorted_numbers = sort_fn(numbers_being_sorted)  # launch the sorting algorithm
        return time.time() - start_time  # return the elapsed time in seconds
    sort_wrapper.__doc__ = sort_fn.__doc__  # copy the docstring of the sorting function
    sort_wrapper.__doc__ = sort_function.__doc__
    sort_wrapper.__name__ = sort_function.__name__ + " visualization"
    return sort_wrapper


def gui_latency() -> None:
    latency_us = get_latency() * 1000000.0  # get the latency in microseconds, edit it with a slider
    imgui.set_next_item_width(hello_imgui.em_size(10))
    changed, latency_ms = imgui.slider_float("Latency (us)", latency_us, 0.0, 50.0)
    if changed:
        set_latency(latency_ms / 1000000)  # And update the latency in the application if the slider was moved
    sort_button_label = "Abort Sort" if not is_aborting() else "Enable Sort"  # display a button to abort...
    if imgui.button(sort_button_label):  # ... or enable the sorting algorithms.
        set_aborting(not is_aborting())  # And change the aborting status if the button was clicked


fl.register_type(NumbersList, NumbersListWithLatency_Gui)  # register the GUI for NumbersList
gui_params = fl.FiatRunParams(enable_idling=False)  # Refresh the GUI as quickly as possible
graph = fl.FunctionsGraph()  # Create a graph of functions
fl.add_fiat_attributes(make_random_number_list, invoke_manually=True, invoke_always_dirty=True)
graph.add_function(make_random_number_list, label="Generate random numbers")  # Add the numbers generator, and make its invocation manual (see above)
sort_functions = [bubble_sort, selection_sort, insertion_sort, merge_sort, quick_sort, quick_sort_median_of_three]
for sort_function in sort_functions:  # For each sorting function, create a wrapper function which will sort, display...
    sort_view = make_sort_function_visualizer(sort_function)  # ... real-time visualization, and return elapsed time.
    graph.add_function(sort_view)  # Add the wrapper function to the graph
    graph.add_link(make_random_number_list, sort_view)  # Link the random numbers generator to the sorting function
graph.add_gui_node(gui_latency,  label="Set Latency")  # Add a GUI node to set the latency
graph.add_markdown_node(__doc__, label="Sort Competition", text_width_em=15)  # Add a node with the documentation
fl.run(graph, params=gui_params)  # And run the graph
