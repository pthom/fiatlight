import fiatlight as fl
from fiatlight.demos.tutorials.sort_competition.numbers_generator import make_random_number_list
from fiatlight.demos.tutorials.sort_competition.sort_algorithms import bubble_sort
from fiatlight.demos.tutorials.sort_competition.number_list import NumbersList
from imgui_bundle import hello_imgui, imgui_ctx, implot
import time


# Add Fiat attribute to the function make_random_number_list
#   - invoke_manually=True: the function will not be called automatically
#   - invoke_always_dirty=True: the function will be called even if the input has not changed
#     (so that we can re-launch the generation of random numbers, and the sorting algorithms)
fl.add_fiat_attributes(
    make_random_number_list,
    label="Generate random numbers",
    invoke_manually=True,
    invoke_always_dirty=True,
)


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


# We use the decorator with_fiat_attributes to add an attribute "invoke_async=True" to the function
# With this attribute, the function will be called asynchronously, so that the GUI can be updated
# while the function is running
@fl.with_fiat_attributes(invoke_async=True)
def bubble_sort_wrapper(numbers: NumbersList) -> float:
    """Wrapper function for bubble_sort that visually track the current status and returns the elapsed time"""

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
    # The GUI will show the numbers being sorted (and they will be updated in the background by the sorting function)
    current_status_gui.value = numbers_being_sorted
    # Step 2: add the instance to the fiat_tuning dictionary
    fl.add_fiat_attributes(bubble_sort_wrapper, fiat_tuning={"sort_status": current_status_gui})

    # Finally call our sorting function
    # (the sorting function will modify the numbers_being_sorted in place,
    #  so that the sort_status GUI will be updated in real time)
    _sorted_numbers = bubble_sort(numbers_being_sorted)

    # Return the elapsed time
    return time.time() - start_time


# Here we register the type NumbersList with its GUI
fl.register_type(NumbersList, NumbersListWithGui)

# Now, run the function composition with Fiatlight
#   First, make sure that the GUI is updated as quickly as possible,
#   by disabling idling, to make animations smoother, even when the user is not interacting with the GUI
gui_params = fl.FiatRunParams(enable_idling=False)
# Then, run the composition of functions
fl.run([make_random_number_list, bubble_sort_wrapper], params=gui_params)
