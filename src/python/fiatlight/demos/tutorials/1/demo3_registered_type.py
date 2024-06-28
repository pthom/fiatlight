import fiatlight as fl
from imgui_bundle import implot, hello_imgui, imgui_ctx
from fiatlight.demos.tutorials.sort_competition.number_list import NumbersList
from fiatlight.demos.tutorials.sort_competition.numbers_generator import make_random_number_list


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
    """NumbersListWithGui is used to present a NumbersList object.
    It does so by inheriting from AnyDataWithGui and setting the present callback to draw_bars.
    """

    def __init__(self) -> None:
        super().__init__(NumbersList)
        # Show how to set the present callback
        self.callbacks.present = draw_bars


# Here we register the type NumbersList with its GUI NumbersListWithGui
fl.register_type(NumbersList, NumbersListWithLatency_Gui)
# Simply run the function with Fiatlight
fl.run(make_random_number_list)
