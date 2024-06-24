"""# Sorting Algorithm Competition
This script contains the final code for the sort algorithm competition tutorial,
without the comments to show how short it can be. In total, there are 74 code lines (excluding blank lines).
"""
from typing import Callable
import fiatlight as fl
from imgui_bundle import implot, hello_imgui, imgui_ctx, imgui
from fiatlight.demos.tutorials.sort_visualization.number_list import NumbersList
from fiatlight.demos.tutorials.sort_visualization.numbers_generator import make_random_number_list
from fiatlight.demos.tutorials.sort_visualization.sort_algorithms import (
    bubble_sort,
    selection_sort,
    insertion_sort,
    merge_sort,
    quick_sort,
    quick_sort_median_of_three,
)
import time


def draw_bars(numbers: NumbersList) -> None:
    with imgui_ctx.push_obj_id(numbers):
        plot_size = hello_imgui.em_to_vec2(25, 15)
        if implot.begin_plot("Numbers", plot_size):
            axis_flags = implot.AxisFlags_.auto_fit.value
            implot.setup_axes("x", "y", axis_flags, axis_flags)
            implot.plot_bars("", numbers.values)
            implot.end_plot()


class NumbersListWithLatency_Gui(fl.AnyDataWithGui[NumbersList]):
    def __init__(self) -> None:
        super().__init__(NumbersList)
        self.callbacks.present = draw_bars


def make_sort_function_visualizer(
    sort_function: Callable[[NumbersList], NumbersList],
) -> Callable[[NumbersList], float]:
    @fl.with_fiat_attributes(invoke_async=True, label=sort_function.__name__ + " - view")
    def sort_wrapper(numbers: NumbersList) -> float:
        start_time = time.time()
        numbers_being_sorted = numbers.copy()
        current_status_gui = NumbersListWithLatency_Gui()
        current_status_gui.value = numbers_being_sorted
        sort_wrapper.fiat_tuning = {  # type: ignore
            "sort_status": current_status_gui
        }
        _sorted_numbers = sort_function(numbers_being_sorted)
        return time.time() - start_time

    sort_function_visualizer = sort_wrapper
    return sort_function_visualizer


fl.register_type(NumbersList, NumbersListWithLatency_Gui)


def gui_latency() -> None:
    from fiatlight.demos.tutorials.sort_visualization.number_list import set_latency, get_latency

    latency_us = get_latency() * 1000000.0
    imgui.set_next_item_width(hello_imgui.em_size(10))
    changed, latency_ms = imgui.slider_float("Latency (us)", latency_us, 0.0, 1000.0)

    if changed:
        set_latency(latency_ms / 1000000)

    from fiatlight.demos.tutorials.sort_visualization.sort_algorithms import is_aborting, set_aborting

    if not is_aborting():
        if imgui.button("Abort Sort"):
            set_aborting(True)
    else:
        if imgui.button("Enable Sort"):
            set_aborting(False)


gui_params = fl.FiatGuiParams()
gui_params.runner_params.fps_idling.enable_idling = False
graph = fl.FunctionsGraph()
graph.add_function(make_random_number_list)
sort_functions = [bubble_sort, selection_sort, insertion_sort, merge_sort, quick_sort, quick_sort_median_of_three]
for sort_function in sort_functions:
    sort_view = make_sort_function_visualizer(sort_function)
    graph.add_function(sort_view)
    graph.add_link(make_random_number_list, sort_view)
graph.add_gui_node(gui_latency)
graph.add_markdown_node(__doc__, label="Sort Competition", text_width_em=15)
fl.run(graph, params=gui_params)
