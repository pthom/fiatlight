"""FunctionWithGui: add GUI to a function

FunctionWithGui
===============

 `FunctionWithGui` is one of the core classes of FiatLight: it wraps a function with a GUI that presents its
 inputs and its output(s).

 See its full code [online](../fiat_core/function_with_gui.py).

Creating a FunctionWithGui object
=================================

 For most functions, fiatlight will automatically create the GUI for the inputs and outputs of your functions.

 ### Automatic creation example:
 The code below will provide a GUI for the function `foo` where the user can enter an integer and a float, and
 it will display the result of the function.

     ```python
     import fiatlight as fl
     def foo(a: int, b: float = 1.5) -> float:
         return a + b
     # When invoking fiat_run, fiatlight will automatically wrap the function into a FunctionWithGui object
     fl.fiat_run(foo, app_name="Automatic creation")
     ```

     *Note: fiatlight handles the default values of the parameters, so the user can leave the float parameter empty,
            or click on the "+" button to set it to the default value, and further change it*

 ### Manual creation example
 If you want to create the GUI manually, you can use the `FunctionWithGui` class.
 The previous example can be rewritten as follows:

     ```python
     import fiatlight as fl
     def foo(a: int, b: float) -> float:
         return a + b

     foo_gui = fl.FunctionWithGui(foo)

     # Method 1: directly run the function
     # fl.fiat_run(foo_gui)

     # Method 2: create a graph and run it
     graph = fl.FunctionsGraph()
     graph.add_function(foo_gui)
     fl.fiat_run_graph(graph, app_name="Manual creation")
     ```

Use registered types
--------------------

If you use registered types, the GUI will be automatically created for the parameters and outputs.
In the example below:
  - `fl.fiat_types.TextPath` is an alias for str, but it is registered to be displayed with a file selection dialog.
  - `matplotlib.figure.Figure` is registered to be displayed as a plot in the GUI

    ```python
    import fiatlight as fl
    import matplotlib.figure
    import matplotlib.pyplot as plt

    def words_length_histogram(text_file: fl.fiat_types.TextPath) -> matplotlib.figure.Figure:
        "Create a histogram of the lengths of words in a text file."
        with open(text_file) as f:
            text = f.read()
        words = text.split()
        lengths = [len(word) for word in words]
        fig, ax = plt.subplots()
        ax.hist(lengths, bins=range(0, 20))
        ax.set_title("Word Length Histogram")
        ax.set_xlabel("Word Length")
        ax.set_ylabel("Frequency")
        return fig


    fl.fiat_run(words_length_histogram, app_name="Registered types")
    ```

Customizing parameters GUI
==========================

 As an example, let's consider the function "my_asin" below: if you run this function with `fiat_run()`,
 the GUI will allow the user to enter any float value for x.
 This lets the user enter values that may not be valid for the function.

     ```python
     import fiatlight as fl

     # Ideally, we would like to restrict the range of x to [-1, 1]
     def my_asin(x: float = 0.5) -> float:
         import math
         return math.asin(x)

     fl.fiat_run(my_asin, app_name="No range restriction")
     ```


Customize the range of a numeric parameter
------------------------------------------

It is possible to customize the GUI for parameters using function attributes:
below, we set the range for x. As a consequence it will be displayed with a slider widget
with a range from -1 to 1.

    ```python
    import fiatlight as fl

    # Use the `with_custom_attrs` decorator to set custom attributes for the function:
    # Here, we set the range of the x parameter.
    # Important: note the double underscore ("_") after the parameter name!
    @fl.with_custom_attrs(x__range=(-1, 1))
    def my_asin(x: float = 0.5) -> float:
        import math
        return math.asin(x)

    # Note: we could have obtained the same effect with the commented line below:
    #    my_asin.x__range = (-1, 1)

    fl.fiat_run(my_asin, app_name="Range restriction")
    ```

Available customization options
-------------------------------

### For int parameters:

```python
from fiatlight.fiat_togui.primitives_gui import int_custom_attributes_documentation
print(int_custom_attributes_documentation())
```

### For float parameters:

```python
from fiatlight.fiat_togui.primitives_gui import float_custom_attributes_documentation
print(float_custom_attributes_documentation())
```

### For bool parameters:

```python
from fiatlight.fiat_togui.primitives_gui import bool_custom_attributes_documentation
print(bool_custom_attributes_documentation())
```

### For images:

```python
from fiatlight.fiat_kits.fiat_image.image_gui import image_custom_attributes_documentation
print(image_custom_attributes_documentation())
```


A full example with custom attributes for function parameters
-------------------------------------------------------------

    ```python
    import fiatlight
    from matplotlib.figure import Figure

    @fiatlight.with_custom_attrs(
        # Edit the number of bars with a knob
        n_bars__edit_type="knob",
        n_bars__range=(1, 300),
        # Edit the mean with an input field
        mu__edit_type="input",
        mu__range=(-5, 5),
        # Edit the standard deviation with a drag
        sigma__edit_type="drag",
        sigma__range=(0.1, 5),
        # Edit the average with a slider for a float value with any range
        # (the slider range will adapt interactively, when dragging far to the left or to the right)
        average__edit_type="slider_float_any_range",
        # Edit the number of data points with a logarithmic slider
        # Note: by default, you can ctrl+click on a slider to input a value directly,
        #       this is disabled here with nb_data__slider_no_input
        nb_data__edit_type="slider",
        nb_data__range=(100, 1_000_000),
        nb_data__slider_logarithmic=True,
        nb_data__slider_no_input=True,
    )
    def interactive_histogram(
        n_bars: int = 50, mu: float = 0, sigma: float = 1, average: float = 500, nb_data: int = 4000
    ) -> Figure:
        '''Generate an interactive histogram with adjustable number of bars, mean, and standard deviation.'''
        import numpy as np
        import matplotlib.pyplot as plt

        data = np.random.normal(mu, sigma, int(nb_data)) + average
        bins = np.linspace(np.min(data), np.max(data), n_bars)
        fig, ax = plt.subplots()
        ax.hist(data, bins=bins, color="blue", alpha=0.7)
        return fig

    fiatlight.fiat_run(interactive_histogram, app_name="Custom attributes")
    ```

Customizing the GUI for a function parameter or output
------------------------------------------------------

You can also customize the GUI for a parameter or output by setting a custom callback function, using
`set_present_custom_callback` or `set_edit_callback` on the parameter or output.

    ```python
    import fiatlight as fl


    def fahrenheit_to_celsius(fahrenheit: float = 0) -> float:
        return (fahrenheit - 32) * 5 / 9

    # This will be our edit callback: it accepts a float and returns a tuple (bool, float)
    # where the first element is True if the value has changed, and the second element is the new value
    def edit_temperature(fahrenheit: float) -> tuple[bool, float]:
        from imgui_bundle import imgui, hello_imgui

        # Set the width of the slider field to 10 em units (using em units is a good practice to make the GUI dpi aware)
        imgui.set_next_item_width(hello_imgui.em_size(10))
        changed, new_value = imgui.slider_float("Fahrenheit", fahrenheit, -100, 200)
        return changed, new_value

    # This will be our present callback: it accepts a float and returns None
    def present_temperature(celsius: float) -> None:
        from imgui_bundle import imgui, ImVec4

        note = "Cold" if celsius < 20 else "Hot" if celsius > 40 else "Warm"
        color = ImVec4(0, 0.4, 1, 1) if celsius < 20 else ImVec4(1, 0.4, 0, 1) if celsius > 40 else ImVec4(0, 1, 0, 1)
        imgui.text_colored(color, f"{celsius:.2f} °C ({note})")


    fahrenheit_to_celsius_gui = fl.FunctionWithGui(fahrenheit_to_celsius)
    fahrenheit_to_celsius_gui.output(0).set_present_custom_callback(present_temperature)
    fahrenheit_to_celsius_gui.input("fahrenheit").set_edit_callback(edit_temperature)

    fl.fiat_run(fahrenheit_to_celsius_gui, app_name="Custom callbacks")
    ```


Control function behavior
=========================

By default, the function will be called only when one of its inputs has changed (either because the user
entered a new value, or because an input is connected to another function that has changed).

You can control the behavior of the function by setting attributes on the function object.

* `invoke_async`: if True, the function will be called asynchronously
* `invoke_manually`: if True, the function will be called only if the user clicks on the "invoke" button
* `invoke_always_dirty`: if True, the function output will always be considered out of date, and
    - if "invoke_manually" is True, the "Refresh needed" label will be displayed
    - if "invoke_manually" is False, the function will be called at each frame

Note: a "live" function is thus a function with `invoke_manually=False` and `invoke_always_dirty=True`

**Example: a live function that display a camera image**

*Note:`fiatlight.fiat_kits.fiat_image.ImageU8_3` is a registered type,
synonym of numpy.ndarray with shape (h, w, 3) and dtype uint8.
Fiatlight will display it as an image in the GUI with a sophisticated image widget (you can zoom in/out,
pan, examine pixel values, etc.)*

```python
import fiatlight as fl
from fiatlight.fiat_kits.fiat_image import ImageU8_3
import cv2  # we use OpenCV to capture the camera image (pip install opencv-python)
cap = cv2.VideoCapture(0)  # you will need a camera!

def get_camera_image() -> ImageU8_3 | None:
    ret, frame = cap.read()
    return ImageU8_3(frame) if ret else None

# Set flags to make this a live function (called automatically at each frame)
get_camera_image.invoke_always_dirty = True

fl.fiat_run(get_camera_image, app_name="Live camera image")
```

**Example: an async function**

When your function is slow, you can set the `invoke_async` flag to True.
In the image below, the yellow spinner indicates that the function is running,
and the GUI remains responsive.

```python
import fiatlight as fl
import time
def slow_function() -> int:
    time.sleep(5)
    return 42

slow_function.invoke_async = True
fl.fiat_run(slow_function, app_name="Async function")
```

**Example: a function that needs to be called manually**

If you set the `invoke_manually` flag to True, the function will be called
only if the user clicks on the "invoke" button (i.e. the button with a "recycle" icon).
If the inputs were changed, a "Refresh needed" label will be displayed.

```python
import fiatlight as fl
def my_function(a: int, b: float) -> float:
    return a + b

my_function.invoke_manually = True
fl.fiat_run(my_function, app_name="Manual invocation")
```


Fully customizing a FunctionWithGui object
==========================================

By subclassing `FunctionWithGui`, you can fully customize the behavior of the function:
- you can add a GUI for the internal state of the function (e.g. displaying a live plot of a sound signal)
- you can add a heartbeat function that will be called at each frame (e.g. get the latest data from a sensor)
- you can save and load the internal GUI presentation options to/from a JSON file (e.g. to save the layout of a plot)

**Example: a camera provider with an internal state and saved options**

[fiatlight.fiat_kits.fiat_image.CameraImageProviderGui](../fiat_kits/fiat_image/camera_image_provider.py)
is a good example of a custom FunctionWithGui class.

You can see it in action with the following code:
    ```python
    import fiatlight as fl
    from fiatlight.fiat_kits.fiat_image import CameraImageProviderGui, ImageU8_3
    import cv2

    def rotate_45(image: ImageU8_3) -> ImageU8_3:
        transform = cv2.getRotationMatrix2D((image.shape[1] / 2, image.shape[0] / 2), 45, 1)
        return cv2.warpAffine(image, transform, (image.shape[1], image.shape[0]))  # type: ignore

    camera_provider_gui = CameraImageProviderGui()
    fl.fiat_run_composition([camera_provider_gui, rotate_45], app_name="Camera provider with rotation")
    ```

**Commented extracts of [camera_image_provider.py](../fiat_kits/fiat_image/camera_image_provider.py)**

Look at the `CameraImageProviderGui` class that extends `FunctionWithGui`:

    ```python
    from fiatlight.fiat_doc import look_at_code
    %look_at_python_code fiatlight.fiat_kits.fiat_image.camera_image_provider.CameraImageProviderGui
    ```

Note: CameraImageProviderGui uses a `CameraImageProvider` class that provides images from a camera,
      as well `CameraParams`, as a Pydantic model for the camera parameters that will be displayed in the GUI,
      and saved to a JSON file.

We use the `enum_with_gui_registration` and `base_model_with_gui_registration` decorators to automatically create
a GUI for the enums and the Pydantic model (note: `dataclass_with_gui_registration` is also available for dataclasses)

    ```python
    from fiatlight.fiat_togui.to_gui import enum_with_gui_registration, base_model_with_gui_registration
    from enum import Enum
    from pydantic import BaseModel
    import cv2

    @enum_with_gui_registration
    class CameraResolution(Enum):
        HD_1280_720 = [1280, 720]
        FULL_HD_1920_1080 = [1920, 1080]
        VGA_640_480 = [640, 480]

    @base_model_with_gui_registration(device_number__range= (0, 5), brightness__range= (0, 1), contrast__range= (0, 1))
    class CameraParams(BaseModel):
        device_number: int = 0
        brightness: float = 0.5
        contrast: float = 0.5
        camera_resolution: CameraResolution = CameraResolution.VGA_640_480


    class CameraImageProvider:
        '''A class that provides images from a camera'''
        camera_params: CameraParams
        cv_cap: cv2.VideoCapture | None = None
        ...
    ```

Debug function internals
========================

fiatlight provides you with powerful tools to visually debug the intermediate states of your function.

[demos/images/toon_edges.py](../demos/images/toon_edges.py) is a good example of how to use the `fiat_internals` attribute.

This is a complex function that adds a toon effect to an image, by adding colored edges to the image contours.

Here are some commented extracts of the function:

```python
from fiatlight.fiat_kits.fiat_image import ImageU8_3, ImageU8_1

def add_toon_edges(
image: ImageU8_3,
# ... lots of parameters ...
) -> ImageU8_3:
    edges: ImageU8_1 # = ...             (compute the edges)
    dilated_edges: ImageU8_1 #  = ...    (dilate the edges)
    image_with_edges: ImageU8_3  # = ... (superimpose the edges on the image)

    # Add internals for debugging
    from fiatlight.fiat_kits.fiat_image import ImageWithGui
    from fiatlight import AnyDataWithGui
    if not hasattr(add_toon_edges, "fiat_internals"):
        add_toon_edges.fiat_internals: dict[str, AnyDataWithGui] = {  # type: ignore
            "edges": ImageWithGui(),
            "dilated_edges": ImageWithGui(),
            "image_with_edges": ImageWithGui(),
        }
    add_toon_edges.fiat_internals["edges"].value = edges  # type: ignore
    add_toon_edges.fiat_internals["dilated_edges"].value = dilated_edges  # type: ignore
    add_toon_edges.fiat_internals["image_with_edges"].value = image_with_edges  # type: ignore

    # return the image with edges
    return image_with_edges
```

Once these internals are set, you can see the function "Internals" in the GUI:

```python
import fiatlight as fl
from fiatlight.fiat_kits.fiat_image import ImageU8_GRAY, ImageU8_3, image_source
from fiatlight.demos.images.toon_edges import add_toon_edges

fl.fiat_run_composition([image_source, add_toon_edges], app_name="Toon edges")
```

-------------------------------------------------------------------------------

FunctionWithGui signature
=========================

Below, you will find the "signature" of the `FunctionWithGui` class,
with its main attributes and methods (but not their bodies)

Its full source code is [available online](../fiat_core/function_with_gui.py).

    ```python
    from fiatlight.fiat_doc import look_at_code
    %look_at_class_header fiatlight.fiat_core.FunctionWithGui
    ```

Architecture
============

Below is a PlantUML diagram showing the architecture of the `fiat_core` module.
See the [architecture page](architecture) for the full architecture diagrams.

    ```python
    from fiatlight.fiat_doc import plantuml_magic
    %plantuml_include class_diagrams/fiat_core.puml
    ```


"""

from fiatlight.fiat_config import get_fiat_config
from fiatlight.fiat_core.togui_exception import FiatToGuiException
from fiatlight.fiat_types import UnspecifiedValue, ErrorValue, JsonDict, GuiType
from fiatlight.fiat_types.error_types import Unspecified, Error, InvalidValue
from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui
from fiatlight.fiat_types.function_types import BoolFunction
from fiatlight.fiat_core.param_with_gui import ParamWithGui, ParamKind
from fiatlight.fiat_core.output_with_gui import OutputWithGui
from fiatlight.fiat_core.possible_custom_attributes import PossibleCustomAttributes
from fiatlight.fiat_types.base_types import CustomAttributesDict
from typing import Any, List, final, Callable, Optional, Type, TypeAlias

import logging


class FunctionPossibleCustomAttributes(PossibleCustomAttributes):
    def __init__(self) -> None:
        super().__init__("FunctionWithGui")

        self.add_explained_section("Behavioral Flags")
        self.add_explained_attribute(
            "invoke_async",
            bool,
            "If True, the function shall be called asynchronously",
            False,
        )
        self.add_explained_attribute(
            "invoke_manually",
            bool,
            "If True, the function will be called only if the user clicks on the 'invoke' button",
            False,
        )
        self.add_explained_attribute(
            "invoke_always_dirty",
            bool,
            "If True, the function output will always be considered out of date, and "
            "  - if invoke_manually is True, the 'Refresh needed' label will be displayed"
            "  - if invoke_manually is False, the function will be called at each frame",
            False,
        )
        self.add_explained_attribute(
            "doc_display",
            bool,
            "If True, the doc string is displayed in the GUI",
            False,
        )
        self.add_explained_attribute(
            "doc_markdown",
            bool,
            "If True, the doc string is in Markdown format",
            True,
        )
        self.add_explained_attribute(
            "doc_user", str, "The documentation string. If not provided, the function docstring will be used", ""
        )
        self.add_explained_attribute(
            "doc_show_source", bool, "If True, the source code of the function will be displayed in the GUI", False
        )


_FUNCTION_POSSIBLE_CUSTOM_ATTRIBUTES = FunctionPossibleCustomAttributes()


class FunctionWithGui:
    """FunctionWithGui: add GUI to a function

    `FunctionWithGui` is one of the core classes of FiatLight: it wraps a function with a GUI that presents its
    inputs and its output(s).

    Public Members
    ==============
    # the name of the function
    name: str = ""

    #
    # Behavioral Flags
    # ----------------
    # invoke_async: if true, the function shall be called asynchronously
    invoke_async: bool = False

    # invoke_manually: if true, the function will be called only if the user clicks on the "invoke" button
    # (if inputs were changed, a "Refresh needed" label will be displayed)
    invoke_manually: bool = False

    # invoke_always_dirty: if true, the function output will always be considered out of date, and
    #   - if invoke_manually is true, the "Refresh needed" label will be displayed
    #   - if invoke_manually is false, the function will be called at each frame
    # Note: a "live" function is thus a function with invoke_manually=False and invoke_always_dirty=True
    invoke_always_dirty: bool = False

    # Optional user documentation to be displayed in the GUI
    #     - doc_display: if True, the doc string is displayed in the GUI (default: False)
    #     - doc_is_markdown: if True, the doc string is in Markdown format (default: True)
    #     - doc_user: the documentation string. If not provided, the function docstring will be used
    #     - doc_show_source: if True, the source code of the function will be displayed in the GUI
    doc_display: bool = True
    doc_markdown: bool = True
    doc_user: str = ""
    doc_show_source: bool = False

    #
    # Internal state GUI
    # ------------------
    # internal_state_gui: optional Gui for the internal state of the function
    # (this function may display a GUI to show the internal state of the function,
    #  and return True if the state has changed, and the function needs to be called)
    internal_state_gui: BoolFunction | None = None

    #
    # Heartbeat
    # ---------
    # on_heartbeat: optional function that will be called at each frame
    # (and return True if the function needs to be called to update the output)
    on_heartbeat: BoolFunction | None = None

    #
    # Serialization
    # -------------
    # save/load_internal_gui_options_from_json (Optional)
    # Optional serialization and deserialization of the internal state GUI presentation options
    # (i.e. anything that deals with how the GUI is presented, not the data itself)
    # If provided, these functions will be used to recreate the GUI presentation options when loading a graph,
    # so that the GUI looks the same when the application is restarted.
    save_internal_gui_options_to_json: Callable[[], JsonDict] | None = None
    load_internal_gui_options_from_json: Callable[[JsonDict], None] | None = None

    """

    # --------------------------------------------------------------------------------------------
    #        Public Members
    # --------------------------------------------------------------------------------------------
    # the name of the function
    name: str = ""

    #
    # Behavioral Flags
    # ----------------
    # invoke_async: if true, the function shall be called asynchronously
    invoke_async: bool = False

    # invoke_manually: if true, the function will be called only if the user clicks on the "invoke" button
    # (if inputs were changed, a "Refresh needed" label will be displayed)
    invoke_manually: bool = False

    # invoke_always_dirty: if true, the function output will always be considered out of date, and
    #   - if invoke_manually is true, the "Refresh needed" label will be displayed
    #   - if invoke_manually is false, the function will be called at each frame
    # Note: a "live" function is thus a function with invoke_manually=False and invoke_always_dirty=True
    invoke_always_dirty: bool = False

    # Optional user documentation to be displayed in the GUI
    #     - doc_display: if True, the doc string is displayed in the GUI (default: False)
    #     - doc_is_markdown: if True, the doc string is in Markdown format (default: True)
    #     - doc_user: the documentation string. If not provided, the function docstring will be used
    #     - doc_show_source: if True, the source code of the function will be displayed in the GUI
    doc_display: bool = True
    doc_markdown: bool = True
    doc_user: str = ""
    doc_show_source: bool = False

    #
    # Internal state GUI
    # ------------------
    # internal_state_gui: optional Gui for the internal state of the function
    # (this function may display a GUI to show the internal state of the function,
    #  and return True if the state has changed, and the function needs to be called)
    internal_state_gui: BoolFunction | None = None

    #
    # Heartbeat
    # ---------
    # on_heartbeat: optional function that will be called at each frame
    # (and return True if the function needs to be called to update the output)
    on_heartbeat: BoolFunction | None = None

    #
    # Serialization
    # -------------
    # save/load_internal_gui_options_from_json (Optional)
    # Optional serialization and deserialization of the internal state GUI presentation options
    # (i.e. anything that deals with how the GUI is presented, not the data itself)
    # If provided, these functions will be used to recreate the GUI presentation options when loading a graph,
    # so that the GUI looks the same when the application is restarted.
    save_internal_gui_options_to_json: Callable[[], JsonDict] | None = None
    load_internal_gui_options_from_json: Callable[[JsonDict], None] | None = None

    # --------------------------------------------------------------------------------------------
    #        Private Members
    # --------------------------------------------------------------------------------------------
    # if True, this indicates that the inputs have changed since the last call, and the function needs to be called
    _dirty: bool = True

    # This is the implementation of the function, i.e. the function that will be called
    _f_impl: Callable[..., Any] | None = None

    # _inputs_with_gui and _outputs_with_gui should be filled soon after construction
    _inputs_with_gui: List[ParamWithGui[Any]]
    _outputs_with_gui: List[OutputWithGui[Any]]

    # if the last call raised an exception, the message is stored here
    _last_exception_message: Optional[str] = None
    _last_exception_traceback: Optional[str] = None

    @staticmethod
    def _Construct_Section() -> None:  # Dummy function to create a section in the IDE # noqa
        """
        # --------------------------------------------------------------------------------------------
        #        Construction
        #  input_with_gui and output_with_gui should be filled soon after construction
        # --------------------------------------------------------------------------------------------
        """
        pass

    def __init__(
        self,
        fn: Callable[..., Any] | None,
        fn_name: str | None = None,
        *,
        signature_string: str | None = None,
        custom_attributes: CustomAttributesDict | None = None,
    ) -> None:
        """Create a FunctionWithGui object, with the given function as implementation

        The function signature is automatically parsed, and the inputs and outputs are created
        with the correct GUI types.

        :param fn: the function for which we want to create a FunctionWithGui

        Notes:
        This function will capture the locals and globals of the caller to be able to evaluate the types.
        Make sure to call this function *from the module where the function and its input/output types are defined*

        If the function has attributes like invoke_manually or invoke_async, they will be taken into account:
            - if `invoke_async` is True, the function will be called asynchronously
            - if `invoke_manually` is True, the function will be called only if the user clicks on the "invoke" button


        Advanced parameters:
        ********************
        :param signature_string: a string representing the signature of the function
                                 used when the function signature cannot be retrieved automatically
        """
        from fiatlight.fiat_togui.to_gui import (
            _add_input_outputs_to_function_with_gui_globals_locals_captured,
        )

        self._inputs_with_gui = []
        self._outputs_with_gui = []
        self._f_impl = fn
        self.name = fn_name or ""

        if fn is not None:
            if self.name == "":
                self.name = fn.__name__ if hasattr(fn, "__name__") else ""
            if custom_attributes is None:
                custom_attributes = fn.__dict__ if hasattr(fn, "__dict__") else {}
            _add_input_outputs_to_function_with_gui_globals_locals_captured(
                self,
                signature_string=signature_string,
                custom_attributes=custom_attributes,
            )

            if custom_attributes is not None:
                self._handle_custom_attributes(custom_attributes)

        if self.name == "":
            raise FiatToGuiException("FunctionWithGui: function name is empty")

    def _handle_custom_attributes(self, custom_attributes: dict[str, Any]) -> None:
        """Handle custom attributes for the function"""
        # Filter out the custom attributes for parameters and outputs
        # (they contain a double underscore "__" in their name)
        fn_custom_attributes = {key: value for key, value in custom_attributes.items() if "__" not in key}
        # We accept wrong keys, because other libraries, such as Pydantic, may add custom attributes
        # that would not be recognized by FiatLight
        _FUNCTION_POSSIBLE_CUSTOM_ATTRIBUTES.raise_exception_if_bad_custom_attrs(
            fn_custom_attributes, accept_wrong_keys=True
        )

        # Check that there are no custom attributes for a non-existing parameter or output
        params_custom_attributes = [key for key in custom_attributes if "__" in key and not key.startswith("__")]
        for custom_attribute in params_custom_attributes:
            assert "__" in custom_attribute
            param_name = custom_attribute.split("__")[0]
            if custom_attribute.startswith("return__"):
                if len(self._outputs_with_gui) == 0:
                    raise FiatToGuiException(
                        f"""
                        FunctionWithGui({self.name}): custom attribute '{custom_attribute}' invalid. The function has no output!
                        """
                    )
            else:
                if not self.has_param(param_name):
                    raise FiatToGuiException(
                        f"""
                        FunctionWithGui({self.name}): custom attribute '{custom_attribute}' is associated to a parameter {param_name} that does not exist!
                        """
                    )

        # Set the custom attributes for the function
        if "invoke_async" in fn_custom_attributes:
            self.invoke_async = fn_custom_attributes["invoke_async"]
        if "invoke_manually" in fn_custom_attributes:
            self.invoke_manually = fn_custom_attributes["invoke_manually"]
        if "invoke_always_dirty" in fn_custom_attributes:
            self.invoke_always_dirty = fn_custom_attributes["invoke_always_dirty"]
        if "doc_display" in fn_custom_attributes:
            self.doc_display = fn_custom_attributes["doc_display"]
        if "doc_markdown" in fn_custom_attributes:
            self.doc_markdown = fn_custom_attributes["doc_markdown"]
        if "doc_user" in fn_custom_attributes:
            self.doc_user = fn_custom_attributes["doc_user"]
        if "doc_show_source" in fn_custom_attributes:
            self.doc_show_source = fn_custom_attributes["doc_show_source"]

    def set_invoke_live(self) -> None:
        """Set flags to make this a live function (called automatically at each frame)"""
        self.invoke_manually = False
        self.invoke_always_dirty = True

    def set_invoke_manually(self) -> None:
        """Set flags to make this a function that needs to be called manually"""
        self.invoke_manually = True

    def set_invoke_manually_io(self) -> None:
        """Set flags to make this a IO function that needs to be called manually
        and that is always considered dirty, because it depends on an external device
        or state (and likely has no input)"""
        self.invoke_manually = True
        self.invoke_always_dirty = True

    def is_invoke_manually_io(self) -> bool:
        """Return True if the function is an IO function that needs to be called manually"""
        return self.invoke_manually and self.invoke_always_dirty

    def set_invoke_async(self) -> None:
        """Set flags to make this a function that is called asynchronously"""
        self.invoke_async = True

    def is_live(self) -> bool:
        """Return True if the function is live"""
        return not self.invoke_manually and self.invoke_always_dirty

    @staticmethod
    def _Utilities_Section() -> None:  # Dummy function to create a section in the IDE # noqa
        """
        # --------------------------------------------------------------------------------------------
        #        Utilities
        # --------------------------------------------------------------------------------------------
        """
        pass

    # There is intentionally no __call__ function!
    # To call the function, set its params via set_param_value, then call the invoke() function

    def call_for_tests(self, **params: Any) -> Any:
        """Call the function with the given parameters, for testing purposes"""
        self._dirty = True
        for name, value in params.items():
            self.set_param_value(name, value)
        self.invoke()
        if self.nb_outputs() == 1:
            return self.output().value
        return tuple([output.data_with_gui.value for output in self._outputs_with_gui])

    def is_dirty(self) -> bool:
        """Return True if the function needs to be called, because the inputs have changed since the last call"""
        return self._dirty

    def set_dirty(self) -> None:
        """Set the function as dirty."""
        self._dirty = True

    def get_last_exception_message(self) -> str | None:
        """Return the last exception message, if any"""
        return self._last_exception_message

    def shall_display_refresh_needed_label(self) -> bool:
        """Return True if the "Refresh needed" label should be displayed
        i.e. if the function is dirty and invoke_manually is True"""
        return self.invoke_manually and self._dirty and not self.is_invoke_manually_io()

    @staticmethod
    def _Inputs_Section() -> None:  # Dummy function to create a section in the IDE # noqa
        """
        # --------------------------------------------------------------------------------------------
        #        Inputs, aka parameters
        # --------------------------------------------------------------------------------------------
        """
        pass

    def nb_inputs(self) -> int:
        """Return the number of inputs of the function"""
        return len(self._inputs_with_gui)

    def all_inputs_names(self) -> List[str]:
        """Return the names of all the inputs of the function"""
        return [param.name for param in self._inputs_with_gui]

    def input(self, name: str) -> AnyDataWithGui[Any]:
        """Return the input with the given name as a AnyDataWithGui[Any]
        The inner type of the returned value is Any in this case.
        You may have to cast it to the correct type, if you rely on type hints.

        Use input_as() if you want to get the input with the correct type.
        """
        for param in self._inputs_with_gui:
            if param.name == name:
                return param.data_with_gui
        assert False, f"input {name} not found"

    def input_as(self, name: str, gui_type: Type[GuiType]) -> GuiType:
        """Return the input with the given name as a GuiType

        GuiType can be any descendant of AnyDataWithGui, like
            fiatlight.fiat_core.IntWithGui, fiatlight.fiat_core.FloatWithGui, etc.

        Raises a ValueError if the input is not found, and a TypeError if the input is not of the correct type.
        """
        for param in self._inputs_with_gui:
            if param.name == name:
                r = param.data_with_gui
                if not isinstance(r, gui_type):
                    raise TypeError(f"Expected type {gui_type.__name__}, got {type(r).__name__} instead.")
                return r
        raise ValueError(f"Parameter {name} not found")

    def input_of_idx(self, idx: int) -> ParamWithGui[Any]:
        """Return the input with the given index as a ParamWithGui[Any]"""
        return self._inputs_with_gui[idx]

    def input_of_idx_as(self, idx: int, gui_type: Type[GuiType]) -> GuiType:
        """Return the input with the given index as a GuiType"""
        r = self._inputs_with_gui[idx].data_with_gui
        if not isinstance(r, gui_type):
            raise TypeError(f"Expected type {gui_type.__name__}, got {type(r).__name__} instead.")
        return r

    def set_input_gui(self, name: str, gui: AnyDataWithGui[Any]) -> None:
        """Set the GUI for the input with the given name"""
        for param in self._inputs_with_gui:
            if param.name == name:
                param.data_with_gui = gui
                return
        raise ValueError(f"Parameter {name} not found")

    def has_param(self, name: str) -> bool:
        """Return True if the function has a parameter with the given name"""
        return any(param.name == name for param in self._inputs_with_gui)

    def param(self, name: str) -> ParamWithGui[Any]:
        """Return the input with the given name as a ParamWithGui[Any]"""
        for param in self._inputs_with_gui:
            if param.name == name:
                return param
        raise ValueError(f"Parameter {name} not found")

    def param_gui(self, name: str) -> AnyDataWithGui[Any]:
        """Return the input with the given name as a AnyDataWithGui[Any]"""
        return self.param(name).data_with_gui

    def set_param_value(self, name: str, value: Any) -> None:
        """Set the value of the input with the given name
        This is useful to set the value of an input programmatically, for example in tests.
        """
        for param in self._inputs_with_gui:
            if param.name == name:
                param.data_with_gui.value = value
                return
        raise ValueError(f"Parameter {name} not found")

    @staticmethod
    def _Outputs_Section() -> None:  # Dummy function to create a section in the IDE # noqa
        """
        # --------------------------------------------------------------------------------------------
        #        Outputs
        # --------------------------------------------------------------------------------------------
        """
        pass

    def nb_outputs(self) -> int:
        """Return the number of outputs of the function.
        A function typically has 0 or 1 output, but it can have more if it returns a tuple.
        """
        return len(self._outputs_with_gui)

    def output(self, output_idx: int = 0) -> AnyDataWithGui[Any]:
        """Return the output with the given index as a AnyDataWithGui[Any]
        The inner type of the returned value is Any in this case.
        You may have to cast it to the correct type, if you rely on type hints.

        Use output_as() if you want to get the output with the correct type.
        """
        if output_idx >= len(self._outputs_with_gui):
            raise ValueError(f"output_idx {output_idx} out of range")
        return self._outputs_with_gui[output_idx].data_with_gui

    def output_as(self, output_idx: int, gui_type: Type[GuiType]) -> GuiType:
        """Return the output with the given index as a GuiType

        GuiType can be any descendant of AnyDataWithGui, like
            fiatlight.fiat_core.IntWithGui, fiatlight.fiat_core.FloatWithGui, etc.

        Raises a ValueError if the output is not found, and a TypeError if the output is not of the correct type.
        """
        r = self._outputs_with_gui[output_idx].data_with_gui
        if not isinstance(r, gui_type):
            raise TypeError(f"Expected type {gui_type.__name__}, got {type(r).__name__} instead.")
        return r

    @staticmethod
    def _Invoke_Section() -> None:  # Dummy function to create a section in the IDE # noqa
        """
        # --------------------------------------------------------------------------------------------
        #        Invoke the function
        # This is the heart of fiatlight: it calls the function with the current inputs
        # and stores the result in the outputs, stores the exception if any, etc.
        # --------------------------------------------------------------------------------------------
        """
        pass

    @final
    def invoke(self) -> None:
        """Invoke the function with the current inputs, and store the result in the outputs.

        Will call the function if:
         - the inputs have changed since the last call
         - the function is dirty
         - none of the inputs is an error or unspecified

        If an exception is raised, the outputs will be set to ErrorValue, and the exception will be stored.

        If the function returned None and the output is not allowed to be None, a ValueError will be raised
        (this is inferred from the function signature)
        """
        assert self._f_impl is not None

        if not self._dirty:
            return

        self._last_exception_message = None
        self._last_exception_traceback = None

        positional_only_values = []
        for param in self._inputs_with_gui:
            if param.param_kind == ParamKind.PositionalOnly:
                positional_only_values.append(param.get_value_or_default())

        keyword_values = {}
        for param in self._inputs_with_gui:
            if param.param_kind != ParamKind.PositionalOnly:
                keyword_values[param.name] = param.get_value_or_default()

        # if any of the inputs is an error or unspecified, we do not call the function
        all_params = positional_only_values + list(keyword_values.values())
        if any(isinstance(value, (Error, Unspecified, InvalidValue)) for value in all_params):
            for output_with_gui in self._outputs_with_gui:
                output_with_gui.data_with_gui.value = UnspecifiedValue
            self._dirty = False
            return

        try:
            fn_output = self._f_impl(*positional_only_values, **keyword_values)

            if fn_output is None and not self._can_emit_none_output():
                msg = f"Function {self.name} returned None, which is not allowed"
                logging.warning(msg)
                # If you are trying to debug and find the root cause of your problem,
                # be informed that a user was just called a few lines before, with this call:
                #     fn_output = self._f_impl(*positional_only_values, **keyword_values)
                # This user function returned none and this was not expected.
                # In the debugger, look at self.name to know which function this was.
                raise ValueError(msg)

            if not isinstance(fn_output, tuple):
                assert len(self._outputs_with_gui) <= 1
                if len(self._outputs_with_gui) == 1:
                    self._outputs_with_gui[0].data_with_gui.value = fn_output
            else:
                assert len(fn_output) == len(self._outputs_with_gui)
                for i, output_with_gui in enumerate(self._outputs_with_gui):
                    output_with_gui.data_with_gui.value = fn_output[i]
        except Exception as e:
            if not get_fiat_config().run_config.catch_function_exceptions:
                raise e
            else:
                self._last_exception_message = str(e)
                import traceback
                import sys

                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback_details = traceback.format_exception(exc_type, exc_value, exc_traceback)
                self._last_exception_traceback = "".join(traceback_details)
                for output_with_gui in self._outputs_with_gui:
                    output_with_gui.data_with_gui.value = ErrorValue

        self._dirty = False

    def on_exit(self) -> None:
        """Called when the application is exiting
        Will call the on_exit callback of all the inputs and outputs
        """
        for output_with_gui in self._outputs_with_gui:
            if output_with_gui.data_with_gui.callbacks.on_exit is not None:
                output_with_gui.data_with_gui.callbacks.on_exit()
        for input_with_gui in self._inputs_with_gui:
            if input_with_gui.data_with_gui.callbacks.on_exit is not None:
                input_with_gui.data_with_gui.callbacks.on_exit()

    def _can_emit_none_output(self) -> bool:
        """Return True if the function can emit None as output
        i.e.
        - either the function has no output
        - or the output can be None (i.e. the signature looks like `def f() -> int | None:`)
        if the function has multiple outputs, we consider that it can not emit None
        """
        if len(self._outputs_with_gui) > 1:
            return False
        if len(self._outputs_with_gui) == 0:
            return True
        output = self._outputs_with_gui[0]
        r = output.data_with_gui.can_be_none
        return r

    @staticmethod
    def _Serialize_Section() -> None:  # Dummy function to create a section in the IDE # noqa
        """
        # --------------------------------------------------------------------------------------------
        #        Save and load to json
        # Here, we only save the options that the user entered manually in the GUI:
        #   - the options of the inputs
        #   - the options of the outputs
        # --------------------------------------------------------------------------------------------
        """
        pass

    def _save_gui_options_to_json(self) -> JsonDict:
        """Save the GUI options to a JSON file
        (i.e. any presentation options of the inputs and outputs, as well as of the internal GUI)
        """
        input_options = {}
        for input_with_gui in self._inputs_with_gui:
            if input_with_gui.data_with_gui.callbacks.save_gui_options_to_json is not None:
                input_options[input_with_gui.name] = input_with_gui.data_with_gui.callbacks.save_gui_options_to_json()

        output_options = {}
        for i, output_with_gui in enumerate(self._outputs_with_gui):
            if output_with_gui.data_with_gui.callbacks.save_gui_options_to_json is not None:
                output_options[i] = output_with_gui.data_with_gui.callbacks.save_gui_options_to_json()

        internal_gui_options = {}
        if self.save_internal_gui_options_to_json is not None:
            internal_gui_options = self.save_internal_gui_options_to_json()

        r = {
            "inputs": input_options,
            "outputs": output_options,
            "internal_gui_options": internal_gui_options,
        }
        return r

    def _load_gui_options_from_json(self, json_data: JsonDict) -> None:
        """Load the GUI options from a JSON file"""
        input_options = json_data.get("inputs", {})
        for input_name, input_option in input_options.items():
            for input_with_gui in self._inputs_with_gui:
                callback_load = input_with_gui.data_with_gui.callbacks.load_gui_options_from_json
                if input_with_gui.name == input_name and callback_load is not None:
                    callback_load(input_option)
                    break

        output_options = json_data.get("outputs", {})
        for output_idx, output_option in output_options.items():
            output_idx = int(output_idx)
            if output_idx >= len(self._outputs_with_gui):
                logging.warning(f"Output index {output_idx} out of range")
                continue
            output_with_gui = self._outputs_with_gui[output_idx]
            callback_load = output_with_gui.data_with_gui.callbacks.load_gui_options_from_json
            if callback_load is not None:
                callback_load(output_option)

        internal_gui_options = json_data.get("internal_gui_options", {})
        if self.load_internal_gui_options_from_json is not None:
            self.load_internal_gui_options_from_json(internal_gui_options)

    @staticmethod
    def _Doc_Section() -> None:  # Dummy function to create a section in the IDE # noqa
        # --------------------------------------------------------------------------------------------
        #       Function documentation & source code
        #       (This is a draft)
        # --------------------------------------------------------------------------------------------
        pass

    def get_function_userdoc(self) -> str | None:
        """Return the user documentation of the function"""
        from fiatlight.fiat_utils import docstring_utils

        if not self.doc_display:
            return ""
        if self.doc_user:
            r = self.doc_user
            r = docstring_utils.unindent_docstring(r)
            return r
        return self._get_function_docstring()

    def _get_function_docstring(self) -> str | None:
        """Return the docstring of the function"""
        from fiatlight.fiat_utils import docstring_utils

        if self._f_impl is None:
            return None
        if hasattr(self._f_impl, "__doc__"):
            docstring = self._f_impl.__doc__
            if docstring is None:
                return None
            docstring = docstring_utils.unindent_docstring(docstring)
            return docstring
        return None

    def get_function_source_code(self) -> str | None:
        """Return the source code of the function"""
        if not self.doc_show_source:
            return None
        if self._f_impl is None:
            return None
        import inspect

        try:
            r = inspect.getsource(self._f_impl)
            return r
        except (OSError, TypeError):
            return None


FunctionWithGuiFactoryFromName: TypeAlias = Callable[[str], FunctionWithGui]
