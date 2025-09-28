"""Handwrite a widget for a simple param

Let's see how to manually write a widget for a function parameter.

We continue from the previous image example.
We added an integer aperture_size parameter to the Canny edge detector function.
However, the OpenCV documentation specifies that the only valid values for this parameter are 3, 5, and 7.

In this part, we will solve this problem by manually writing the GUI for this parameter, so that the user can only select one of the valid values.

In order to create our custom widget, we will write a custom edition callback for this parameter: it accepts the current value, and returns a tuple:
    - a bool indicating if the value was changed
    - the new value (or the old value if not changed)
We will be using the Immediate Mode GUI (imgui) paradigm (with Dear ImGui Bundle).

Refer to the section "Immediate Mode GUI with Python" of the manual for more info about this paradigm and about Dear ImGui.

Here our function simply presents a radio button for each valid value, and returns the selected value.
It uses "same line" to align the radio buttons horizontally.

Then, we transform the detect_edges function into a FunctionWithGui, and
so that we set the edit callback for the "aperture size" parameter to our custom function.

There are many more callbacks (for edition, presentation, default value, events, etc.). Refer to the documentation of AnyDataGuiCallbacks for more details.

Then, we run the app with our two functions (using the customized detect_edges_gui).

"""
import cv2
import fiatlight as fl
from fiatlight.fiat_types import ImagePath
from fiatlight.fiat_kits.fiat_image import ImageRgb

# We import imgui, to be able to write our custom widget using imgui
from imgui_bundle import imgui


@fl.with_fiat_attributes(label="Read Image from File")
def read_image(image_path: ImagePath) -> ImageRgb:
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img


def detect_edges(
    image: ImageRgb,
    low_threshold: float = 100.0,
    high_threshold: float = 200.0,
    aperture_size: int = 3,  # Valid values are (3, 5, 7) !
) -> ImageRgb:
    """Detects edges in an image and returns a new image with the edges
    Following OpenCV documentation, the only valid values for aperture_size are 3, 5, and 7.
    """
    return cv2.Canny(image, low_threshold, high_threshold, apertureSize=aperture_size)


def edit_aperture_size(aperture_size: int) -> tuple[bool, int]:
    """Custom edition of the aperture_size parameter.
    This function will be used as an edit callback for the aperture_size parameter of the detect_edges function.
    It accepts an int (the aperture size), and returns a tuple:
        - a bool indicating if the value was changed
        - the new value (or the old value if not changed)

    This function uses the Immediate Mode GUI (imgui) paradigm (with Dear ImGui Bundle).
    Refer to the section "Immediate Mode GUI with Python" of the manual for more details,
    or to this page:
    https://github.com/pthom/imgui_bundle/blob/main/docs/docs_md/imgui_python_intro.md
    """
    valid_values = [3, 5, 7]
    assert aperture_size in valid_values
    was_changed = False
    for value in valid_values:
        selected = aperture_size == value
        clicked = imgui.radio_button(str(value), selected)
        if clicked:
            was_changed = True
            aperture_size = value
        imgui.same_line()
    imgui.new_line()
    return was_changed, aperture_size


# Transform the detect_edges function into a FunctionWithGui,
# so that we can customize the edit callback for the aperture_size parameter
detect_edges_gui = fl.FunctionWithGui(detect_edges)
detect_edges_gui.input("aperture_size").callbacks.edit = edit_aperture_size

# Run the app with our two functions (using the customized detect_edges_gui)
fl.run([read_image, detect_edges_gui], app_name="Your app name here")
