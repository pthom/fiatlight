# In  this version, we reuse Fiatlight's GUI in a standalone application.

"""Sorting Algorithm Competition
================================
This program shows a competition between different sorts algorithms.

**Latency**

Here, you can set the speed of memory access: this drastically reduces the speed of the algorithms,
so that you can visually see their behavior. The latency can be changed while the sorting algorithms are running.

You can also stop the sorting algorithms in their tracks (a slight delay might be needed)

**Number Generation Options**

Here, you can generate the list that will be sorted with different shapes.
Click on "Call Manually" to generate a new list.

**Visualizations**

The visualizations will show various sorting algorithms. You can see their status in real time.
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


# The code before this is identical to the "Function Graph" code in tutorial_sort_finished_graph.py
# (except for the docstring which is a bit different)
# ======================================================================================================================
# The code below is new and is used to create a standalone application
# (The additional imports are voluntarily placed here to make the diff easier to read:
#    noqa: E402 is used to ignore the "Module level import not at top of file" error)
from fiatlight.demos.tutorials.sort_competition.numbers_generator import NumbersGenerationOptions  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from threading import Thread  # noqa: E402
from imgui_bundle import imspinner, imgui_md, immapp  # noqa: E402


@dataclass
class ThreadedSortFunctionVisualizer:
    sort_visualizer: Callable[[NumbersList], float]
    sort_thread: Thread | None = None
    duration: float | None = None


class AppGui:
    """AppGui is the main class of the application."""

    # numbers_generation_options: options for the generation of the numbers
    numbers_generation_options: NumbersGenerationOptions

    # threaded_visualizers:
    #   Our sort functions will be run in a thread: here, we store for each sort function
    #   the thread, its thread proc (sort_visualizer) and the duration of the thread
    threaded_visualizers: list[ThreadedSortFunctionVisualizer]

    # Current numbers list
    current_numbers_list: NumbersList

    show_theme_window: bool = False

    def __init__(self) -> None:
        self.numbers_generation_options = NumbersGenerationOptions()
        self.threaded_visualizers = []

        # add all the sorting algorithms, and link them to the random numbers generator
        sort_functions = [
            bubble_sort,
            selection_sort,
            insertion_sort,
            merge_sort,
            quick_sort,
            quick_sort_median_of_three,
        ]
        for sort_function in sort_functions:
            sort_view = make_sort_function_visualizer(sort_function)
            self.threaded_visualizers.append(ThreadedSortFunctionVisualizer(sort_view))

        # A first run with 10 values to initialize the visualizers
        self._launch_sort_threads()

    def _is_any_sort_thread_running(self) -> bool:
        r = False
        for thread in self.threaded_visualizers:
            if thread.sort_thread is not None and thread.sort_thread.is_alive():
                r = True
                break
        return r

    def _launch_sort_threads(self) -> None:
        self.current_numbers_list = make_random_number_list(self.numbers_generation_options)

        def launch_thread(tv: ThreadedSortFunctionVisualizer) -> None:
            def thread_proc() -> None:
                tv.duration = tv.sort_visualizer(self.current_numbers_list)
                tv.sort_thread = None

            tv.duration = None
            tv.sort_thread = Thread(target=thread_proc)
            tv.sort_thread.start()

        for tv_ in self.threaded_visualizers:
            launch_thread(tv_)

    def gui_numbers_generation(self) -> None:
        _changed, self.numbers_generation_options = fl.immediate_edit(
            "Gen. options", self.numbers_generation_options, edit_collapsible=False
        )
        is_running = self._is_any_sort_thread_running()
        if is_running:
            imgui.begin_disabled(True)
        if imgui.button("Generate new numbers and sort them"):
            self._launch_sort_threads()
        if is_running:
            imgui.end_disabled()

    def gui_visualizations(self) -> None:
        # Shows the visualization of the sorting algorithms + their status and duration
        for i, threaded_visualizer in enumerate(self.threaded_visualizers):
            # We place each visualizer in a group, so that the call to imgui.same_line()
            # after this will align with the whole group
            # This enables us to display 3 visualizers per row, in a grid-like fashion
            with imgui_ctx.begin_group():
                sort_name = threaded_visualizer.sort_visualizer.__name__
                imgui_md.render(f"## {sort_name}")

                if hasattr(threaded_visualizer.sort_visualizer, "fiat_tuning"):
                    # We reuse the fiat_tuning attribute
                    fiat_tuning = threaded_visualizer.sort_visualizer.fiat_tuning
                    if "sort_status" in fiat_tuning:
                        # In our case, fiat_tuning["sort_status"] contains a GUI
                        # that will show the numbers being sorted. We just call its present method
                        view_gui: NumbersListWithGui = fiat_tuning["sort_status"]
                        view_gui.gui_present()
                    if threaded_visualizer.sort_thread is not None and threaded_visualizer.sort_thread.is_alive():
                        # If the thread is running, we show a spinner
                        imgui.same_line()
                        imspinner.spinner_clock("spinner", 10, 1)

                if threaded_visualizer.duration is not None:
                    # If the thread is finished, we show the duration
                    imgui.text(f"Duration: {threaded_visualizer.duration:.2f} s")

            # Display 3 visualizers per row
            if i % 3 != 2:
                imgui.same_line()

    def layout_guis(self) -> None:
        # Full GUI function of the application: it does the layout by using groups
        # We use begin_group() to create "groups" that we can then align horizontally (using same_line())

        # Left column: doc + theme window
        with imgui_ctx.begin_group():
            # Show doc in a child window, to force the width
            with imgui_ctx.begin_child("doc", hello_imgui.em_to_vec2(15, 50)):
                imgui_md.render(__doc__)
            # Button to the theme window
            _, self.show_theme_window = imgui.checkbox("Show Theme Window", self.show_theme_window)
            if self.show_theme_window:
                hello_imgui.show_theme_tweak_gui_window()

        # We call same_line() before showing the right column
        # (ImGui adds a new line by default)
        imgui.same_line()

        # Right column: commands and visualization
        with imgui_ctx.begin_group():
            # Commands: we have three blocks on the same line
            #           (see calls to imgui.same_line() below)
            with imgui_ctx.begin_group():
                imgui_md.render("# Latency")
                gui_latency()
            imgui.same_line()
            with imgui_ctx.begin_group():
                imgui_md.render("# Numbers generation options")
                self.gui_numbers_generation()
            imgui.same_line()
            with imgui_ctx.begin_group():
                imgui.text("Generated numbers")
                draw_bars(self.current_numbers_list)

            # Visualizations: we have a single block
            imgui_md.render("# Visualization")
            self.gui_visualizations()


def main() -> None:
    # Main function of the application
    # 1. We create an instance of AppGui and we run the application
    app_gui = AppGui()

    # 2. We run the application using HelloImGui and ImmApp
    # 2.a Set the AddOns we will be using
    addons = immapp.AddOnsParams()
    addons.with_implot = True
    addons.with_markdown = True
    # 2.b Set the Hello ImGui runner params
    runner_params = immapp.RunnerParams()
    runner_params.app_window_params.window_title = "Sort Competition"
    runner_params.app_window_params.window_geometry.size = (1600, 900)
    runner_params.fps_idling.enable_idling = False
    runner_params.imgui_window_params.tweaked_theme.theme = hello_imgui.ImGuiTheme_.material_flat
    # 2.c Set the GUI function
    runner_params.callbacks.show_gui = app_gui.layout_guis

    # 2.d Run the application
    immapp.run(runner_params, addons)


if __name__ == "__main__":
    main()
