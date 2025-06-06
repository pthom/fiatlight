import fiatlight as fl
from fiatlight.demos.tutorials.sort_competition.numbers_generator import make_random_number_list
from fiatlight.demos.tutorials.sort_competition.number_list import NumbersList
from imgui_bundle import hello_imgui, imgui_ctx, implot


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


# Here we register the type NumbersList with its GUI
fl.register_type(NumbersList, NumbersListWithGui)

# Simply run the function with Fiatlight
fl.run(make_random_number_list)
