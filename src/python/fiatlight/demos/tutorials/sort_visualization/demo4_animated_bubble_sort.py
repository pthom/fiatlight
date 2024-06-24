import fiatlight as fl
from imgui_bundle import implot, hello_imgui, imgui_ctx
from fiatlight.demos.tutorials.sort_visualization.number_list import NumbersList
from fiatlight.demos.tutorials.sort_visualization.numbers_generator import make_random_number_list
from fiatlight.demos.tutorials.sort_visualization.sort_algorithms import bubble_sort
import time


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


class NumbersListWithLatency_Gui(fl.AnyDataWithGui[NumbersList]):
    """NumbersListWithLatency_Gui is used to present a NumbersList object.
    It does so by inheriting from AnyDataWithGui and setting the present callback to draw_bars.
    """

    def __init__(self) -> None:
        super().__init__(NumbersList)
        # Show how to set the present callback
        self.callbacks.present = draw_bars


# We use the decorator with_fiat_attributes to add an attribute "invoke_async=True" to the function
# With this attribute, the function will be called asynchronously, so that the GUI can be updated
# while the function is running
@fl.with_fiat_attributes(invoke_async=True)
def bubble_sort_wrapper(numbers: NumbersList) -> float:
    """Wrapper function for bubble_sort that
    - adds a Fiat tuning dictionary to visually track the current status of the numbers
    - returns the elapsed time in seconds
    """

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
    bubble_sort_wrapper.fiat_tuning = {  # type: ignore
        "sort_status": current_status_gui
    }

    # Finally call our sorting function
    # (the sorting function will modify the numbers_being_sorted in place,
    #  so that the sort_status GUI will be updated in real time)
    _sorted_numbers = bubble_sort(numbers_being_sorted)

    # Return the elapsed time
    return time.time() - start_time


# Here we register the type NumbersList with its GUI NumbersListWithLatency_Gui
fl.register_type(NumbersList, NumbersListWithLatency_Gui)

# Disable idling, to make animations smoother
gui_params = fl.FiatGuiParams()
gui_params.runner_params.fps_idling.enable_idling = False
# run the composition of the two functions with flat light and the given parameters
fl.run([make_random_number_list, bubble_sort_wrapper], params=gui_params)
