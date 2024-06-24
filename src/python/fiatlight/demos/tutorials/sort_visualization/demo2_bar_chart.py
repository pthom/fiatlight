import fiatlight as fl

# 2. Explain bundle, implot
from imgui_bundle import implot, hello_imgui, imgui_ctx
from fiatlight.demos.tutorials.sort_visualization.number_list import NumbersList
from fiatlight.demos.tutorials.sort_visualization.numbers_generator import make_random_number_list


# 3.
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


# 1.
# show definition of FunctionWithGui
make_random_number_list_gui = fl.FunctionWithGui(make_random_number_list)
# show definition of output & present
make_random_number_list_gui.output(0).callbacks.present = draw_bars
# Simply run the function with Fiatlight
fl.run(make_random_number_list_gui)
