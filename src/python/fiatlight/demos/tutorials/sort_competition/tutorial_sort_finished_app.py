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
from typing import Callable

import fiatlight as fl
from imgui_bundle import implot, hello_imgui, imgui_ctx, imgui, immapp, imgui_md, imspinner, ImVec2
from fiatlight.demos.tutorials.sort_competition.number_list import NumbersList
from fiatlight.demos.tutorials.sort_competition.numbers_generator import (
    make_random_number_list,
    NumbersGenerationOptions,
)
from fiatlight.demos.tutorials.sort_competition.sort_algorithms import (
    bubble_sort,
    selection_sort,
    insertion_sort,
    merge_sort,
    quick_sort,
    quick_sort_median_of_three,
)
import time
from threading import Thread
from dataclasses import dataclass


def draw_bars(numbers: NumbersList) -> None:
    """Draw a bar chart of the numbers"""

    # The ID passed to implot.begin_plot should be unique, or use ##
    # As an alternative, you can use imgui_ctx.push_obj_id
    with imgui_ctx.push_obj_id(numbers):
        # We will specify the block size
        # In order to have a size which is independent of the screen DPI scaling,
        # We will specify the size in EM units. 1 EM unit is the height of the font.
        plot_size = hello_imgui.em_to_vec2(22, 15)

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


class NumbersListWithGui(fl.AnyDataWithGui[NumbersList]):
    """NumbersListWithGui is used to present a NumbersList object.
    It does so by inheriting from AnyDataWithGui and setting the present callback to draw_bars.
    """

    def __init__(self) -> None:
        super().__init__(NumbersList)
        # Show how to set the present callback
        self.callbacks.present = draw_bars


# Here we register the type NumbersList with its GUI NumbersListWithGui
fl.register_type(NumbersList, NumbersListWithGui)


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
    @fl.with_fiat_attributes(
        invoke_async=True,
        label=sort_function.__name__ + " - view",
        doc_display=True,
    )
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
        # Step 1: create an instance of NumbersListWithGui
        current_status_gui = NumbersListWithGui()
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
    sort_function_visualizer.__name__ = sort_function.__name__ + " visualization"
    sort_function_visualizer.__doc__ = sort_function.__doc__
    return sort_function_visualizer


def gui_latency() -> None:
    """A GUI function to set the latency of the sorting algorithms"""
    from fiatlight.demos.tutorials.sort_competition.number_list import set_latency, get_latency

    latency_us = get_latency() * 1000000.0
    # Edit the latency via a slider
    # First we need to set its width because sliders will occupy the full window width by default
    # (the window width is much larger than the function node)
    # We will specify this within EM units. 1 EM unit is the height of the font.
    imgui.set_next_item_width(hello_imgui.em_size(10))
    changed, latency_ms = imgui.slider_float("Latency (us)", latency_us, 0.0, 100.0)

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


# The code before this is identical to the "Function Graph" code in demo5_sort_competition.py
# ======================================================================================================================
# The code below is new and is used to create a standalone application


@dataclass
class ThreadedSortFunctionVisualizer:
    sort_visualizer: Callable[[NumbersList], float]
    sort_thread: Thread | None = None
    duration: float | None = None


class AppGui:
    """AppGui is the main class of the application."""

    # numbers_generation_options_gui:
    # A GUI for the NumbersGenerationOptions class (it contains an instance of NumbersGenerationOptions)
    numbers_generation_options_gui: fl.AnyDataWithGui[NumbersGenerationOptions]
    # threaded_visualizers:
    #   Our sort functions will be run in a thread: here, we store for each sort function
    #   the thread, its thread proc (sort_visualizer) and the duration of the thread
    threaded_visualizers: list[ThreadedSortFunctionVisualizer]

    # Current numbers list
    current_numbers_list: NumbersList

    def __init__(self) -> None:
        self.numbers_generation_options_gui = fl.to_data_with_gui(NumbersGenerationOptions())
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
        self.current_numbers_list = make_random_number_list(self.numbers_generation_options_gui.get_actual_value())

        def launch_thread(tv: ThreadedSortFunctionVisualizer) -> None:
            def thread_proc() -> None:
                tv.duration = tv.sort_visualizer(self.current_numbers_list)
                tv.sort_thread = None

            tv.duration = None
            tv.sort_thread = Thread(target=thread_proc)
            tv.sort_thread.start()

        for tv_ in self.threaded_visualizers:
            launch_thread(tv_)

    def gui_commands(self) -> None:
        # Shows
        # - the GUI of the NumbersGenerationOptions (this uses the GUI generated by Fiatlight)
        # - a button to generate new numbers and launch the sorting algorithms

        with imgui_ctx.begin_group():
            self.gui_latency()

        imgui.same_line()

        with imgui_ctx.begin_group():
            imgui_md.render("# Numbers generation options")
            _changed = self.numbers_generation_options_gui.gui_edit()
            is_running = self._is_any_sort_thread_running()
            if is_running:
                imgui.begin_disabled(True)
            if imgui.button("Generate new numbers and sort them"):
                self._launch_sort_threads()
            if is_running:
                imgui.end_disabled()

        imgui.same_line()

        with imgui_ctx.begin_group():
            imgui.text("Generated numbers")
            draw_bars(self.current_numbers_list)

    @staticmethod
    def gui_latency() -> None:
        # Shows the latency GUI
        imgui_md.render("# Latency")
        gui_latency()

    def gui_visualizations(self) -> None:
        # Shows the visualization of the sorting algorithms + their status and duration
        imgui_md.render("# Visualization")

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

    @staticmethod
    def gui_doc() -> None:
        # Render the documentation as Markdown
        imgui.begin_child("doc", ImVec2(200, 0))
        imgui_md.render(__doc__)
        imgui.end_child()

    def gui(self) -> None:
        # Full GUI function of the application: it does the layout by using groups
        # We use begin_group() to create "groups" that we can then align horizontally (using same_line())

        # Left columns: doc
        with imgui_ctx.begin_group():
            self.gui_doc()

        imgui.same_line()

        # Right columns: commands and visualization
        with imgui_ctx.begin_group():
            self.gui_commands()
            self.gui_visualizations()


def main_using_standard_layout() -> None:
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
    # 2.c Set the GUI function
    runner_params.callbacks.show_gui = app_gui.gui

    # 2.d Run the application
    immapp.run(runner_params, addons)


def main_using_dockable_windows() -> None:
    # An alternative version where we use dockable windows

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
    runner_params.app_window_params.window_geometry.size = (1600, 1100)
    runner_params.fps_idling.enable_idling = False

    # 3. Set the dockable windows
    runner_params.imgui_window_params.default_imgui_window_type = (
        hello_imgui.DefaultImGuiWindowType.provide_full_screen_dock_space
    )
    # We want this to create this Dockable spaces:
    #    ___________________________________________
    #    |         |                                |  # The Dockable Space "MainDockSpace" is provided automatically,
    #    | Doc     |    Commands                    |  # The Commands will be place here
    #    |         |    (aka "MainDockSpace")       |  # after it was split into three parts with the code below.
    #    |         |________________________________|
    #    |         |                                |
    #    |         |     Visualizations             |
    #    |         |                                |
    #    --------------------------------------------
    split_main_doc = hello_imgui.DockingSplit()
    split_main_doc.initial_dock = "MainDockSpace"
    split_main_doc.new_dock = "Doc"
    split_main_doc.direction = imgui.Dir_.left
    split_main_doc.ratio = 0.2

    split_commands_and_visualization = hello_imgui.DockingSplit()
    split_commands_and_visualization.initial_dock = "MainDockSpace"
    split_commands_and_visualization.new_dock = "Visualizations"
    split_commands_and_visualization.direction = imgui.Dir_.down
    split_commands_and_visualization.ratio = 0.75

    runner_params.docking_params.docking_splits = [split_main_doc, split_commands_and_visualization]

    # 4. show more elements
    runner_params.imgui_window_params.show_menu_bar = True
    runner_params.imgui_window_params.show_status_bar = True

    # D. Dockable windows content
    # * Doc window
    doc_window = hello_imgui.DockableWindow()
    doc_window.label = "Doc"
    doc_window.dock_space_name = "Doc"
    doc_window.gui_function = app_gui.gui_doc
    # * Commands window
    commands_window = hello_imgui.DockableWindow()
    commands_window.label = "Commands"
    commands_window.dock_space_name = "MainDockSpace"
    commands_window.gui_function = app_gui.gui_commands
    # * Visualizations window
    visualizations_window = hello_imgui.DockableWindow()
    visualizations_window.label = "Visualizations"
    visualizations_window.dock_space_name = "Visualizations"
    visualizations_window.gui_function = app_gui.gui_visualizations

    runner_params.docking_params.dockable_windows = [doc_window, commands_window, visualizations_window]

    # 2.c Run the application
    immapp.run(runner_params, addons)


if __name__ == "__main__":
    # main_using_standard_layout()
    main_using_dockable_windows()