"""Demonstrates how Fiatlight can be used as a versatile immediate widget
for any kind of data (int, str, pydantic model, etc.), with a simple API,
and a high level of customization.

In this example, we interactively edit with fiatlight.immediate_edit:
- simple int values (either with a slider and a knob)
- a composed pydantic model (User) with a nested model (Address)

---

Note: we used the fiatlight command line tool to get info about the
possible customization options for the immediate_edit function for int values:

```bash
> fiatlight gui int

GUI type: int
==============
  A highly customizable int widget.

  Available fiat attributes for IntWithGui:
  --------------------------------------------------------------------------------
  +--------------------+-----------------+-----------+-------------------------------------------+
  | Name               | Type            | Default   | Explanation                               |
  +====================+=================+===========+===========================================+
  | range              | tuple[int, int] | (0, 10)   | Range of the integer                      |
  +--------------------+-----------------+-----------+-------------------------------------------+
  | edit_type          | str             | input     | Type of the edit widget. Possible values: |
  |                    |                 |           | slider, input, drag, knob,                |
  |                    |                 |           | slider_and_minus_plus                     |
  +--------------------+-----------------+-----------+-------------------------------------------+
  | format             | str             | %d        | Format string for the value               |
  +--------------------+-----------------+-----------+-------------------------------------------+
  | width_em           | float           | 9.0       | Width of the widget in em                 |
  +--------------------+-----------------+-----------+-------------------------------------------+
  | knob_size_em       | float           | 2.5       | Size of the knob in em                    |
  +--------------------+-----------------+-----------+-------------------------------------------+
  | knob_steps         | int             | 10        | Number of steps in the knob               |
  +--------------------+-----------------+-----------+-------------------------------------------+
  | knob_no_input      | bool            | True      | Disable text input on knobs and sliders   |
  +--------------------+-----------------+-----------+-------------------------------------------+
  | slider_no_input    | bool            | False     | Disable text input on sliders             |
  +--------------------+-----------------+-----------+-------------------------------------------+
  | slider_logarithmic | bool            | False     | Use a logarithmic scale for sliders       |
  +--------------------+-----------------+-----------+-------------------------------------------+

  Available fiat attributes for AnyDataWithGui Generic attributes:
  --------------------------------------------------------------------------------
  +---------------------+--------+---------------------+------------------------------------------------+
  | Name                | Type   | Default             | Explanation                                    |
  +=====================+========+=====================+================================================+
  |                     |        |                     | **Generic attributes**                         |
  +---------------------+--------+---------------------+------------------------------------------------+
  | validator           | object | None                | Function to validate a parameter value: should |
  |                     |        |                     | raise a ValueError if invalid, or return the   |
  |                     |        |                     | value (possibly modified)                      |
  +---------------------+--------+---------------------+------------------------------------------------+
  | label               | str    |                     | A label for the parameter. If empty, the       |
  |                     |        |                     | function parameter name is used                |
  +---------------------+--------+---------------------+------------------------------------------------+
  | tooltip             | str    |                     | An optional tooltip to be displayed            |
  +---------------------+--------+---------------------+------------------------------------------------+
  | label_color         | ImVec4 | ImVec4(0.000000,    | The color of the label (will use the default   |
  |                     |        | 0.000000, 0.000000, | text color if not provided)                    |
  |                     |        | 1.000000)           |                                                |
  +---------------------+--------+---------------------+------------------------------------------------+
  | edit_collapsible    | bool   | True                | If True, the edit GUI may be collapsible       |
  +---------------------+--------+---------------------+------------------------------------------------+
  | present_collapsible | bool   | True                | If True, the present GUI may be collapsible    |
  +---------------------+--------+---------------------+------------------------------------------------+

```

"""

from imgui_bundle import hello_imgui, imgui
from pydantic import BaseModel, field_validator
import fiatlight as fl


@fl.base_model_with_gui_registration(
    label="Address entry",
    tooltip="Please input at least the city",
    edit_collapsible=False,
)
class Address(BaseModel):
    city: str = "Your city?"
    street: str = ""
    zip_code: str = ""

    @field_validator("city")
    def city_should_not_be_empty(cls, value: str) -> str:
        if len(value) == 0:
            raise ValueError("city should not be empty")
        return value


@fl.base_model_with_gui_registration()
class User(BaseModel):
    name: str = "John Doe"
    age: int = 19
    address: Address = Address()

    @field_validator("age")
    def cannot_be_minor(cls, value: int) -> int:
        if value < 18:
            raise ValueError("age should be at least 18")
        return value


USER = User()
MY_VALUE = 42
MY_VALUE2 = 12


def gui() -> None:
    global USER

    # Edit a pydantic model
    force_refresh = False
    if imgui.button("Set age to 42"):
        USER.age = 42
        force_refresh = True
    user_changed, USER = fl.immediate_edit("User##1", USER, edit_collapsible=False, force_refresh=force_refresh)
    if user_changed:
        print("User changed")

    # Edit a simple value using fiatlight (here we edit an int)
    global MY_VALUE, MY_VALUE2
    changed, MY_VALUE = fl.immediate_edit(
        "Value",
        MY_VALUE,
        edit_type="slider",
        slider_logarithmic=True,
        range=(1, 1000_000_000),
    )

    changed, MY_VALUE = fl.immediate_edit(
        "Value2",  # Error: same label used twice (Fiatlight should raise an understandable error)
        MY_VALUE2,
        edit_type="knob",
        range=(10, 20),
    )


hello_imgui.run(gui)
