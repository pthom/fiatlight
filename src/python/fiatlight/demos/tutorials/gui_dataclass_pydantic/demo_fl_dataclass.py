"""  Example: using a dataclass with Fiatlight
==============================================

Note: Dataclasses cannot be serialized by default!
      As a consequence, a Fiatlight will warn that it can not save the user inputs upon exit.
      Look at the example demo_fl_pydantic.py to see how to use a Pydantic model instead,
      with which the user inputs can be saved.


In order to register a dataclass with Fiatlight, we can either:
---------------------------------------------------------------
  - Option 1: replace the @dataclass decorator with @fl.dataclass_with_gui_registration
  - Option 2: call fl.register_dataclass with the dataclass as argument


Add fiat_attributes when registering a dataclass:
-------------------------------------------------
fiat_attributes are custom attributes that enable to customize the GUI for a given member, or to add validators.

Example
    ```python
    @fl.dataclass_with_gui_registration(
        age__label="Age",
        ...
    ```

In this example, `age__label` will change the label of the age field in the GUI.
This name (`age__label`) is composed of the name of a member (`age`), followed by a **double** underscore,
followed by a fiat attribute name (`label`)

In order to know which fiat_attributes are available, you can query this via the command line.
In the example below we query the available attributes for a string.

```bash
> fiatlight gui str
...
... Outputs lots of other possible attributes
...
 Available fiat attributes for AnyDataWithGui Generic attributes:
  +-------------+--------+---------------------+------------------------------------------------+
  | label       | str    |                     | A label for the parameter. If empty, the       |
  |             |        |                     | function parameter name is used                |
  +-------------+--------+---------------------+------------------------------------------------+
...
```
"""

import fiatlight as fl


def validate_name(name: str) -> str:
    """A simple validator that raises a ValueError on bad inputs
    In this example, our name must start with a capital letter
    """
    if len(name) > 0 and not name[0].isupper():
        raise ValueError("Name must start with a capital letter")
    return name


def validate_preferred_number(number: int) -> int:
    """An example validator that modifies the user input.
    Here, this validator will force the number to be a multiple of 5
    """
    return int(number / 5) * 5


# Option 1: replace the @dataclass decorator with @fl.dataclass_with_gui_registration
# ------------------------------------------------------------------------------------
# @dataclass
@fl.dataclass_with_gui_registration(  # This also applies the @dataclass decorator
    name__label="Name",
    name__hint="Name (start with a capital letter)",
    age__label="Age",
    age__range=(0, 100),
    preferred_number__range=(0, 30),
    preferred_number__label="Pref number",
    # Validators
    name__validator=validate_name,
    preferred_number__validator=validate_preferred_number,
)
class PersonDataclass:
    name: str = ""
    age: int = 0
    preferred_number: int = 0

    def __str__(self) -> str:
        return f"{self.name} is {self.age} years old"


# Option 2: call fl.register_dataclass with the dataclass as argument
#           (this is often preferable, because it is less intrusive
#           as it does not modify the class definition)
# --------------------------------------------------------------------
# fl.register_dataclass(
#     PersonDataclass,
#     name__label="Name",
#     name__hint="Name (start with a capital letter)",
#     age__label="Age",
#     age__range=(0, 100),
#     preferred_number__range=(0, 30),
#     preferred_number__label = "Pref number",
#     # Validators
#     name__validator=validate_name,
#     preferred_number__validator=validate_preferred_number,
# )


# Display a function that uses the dataclass as an input and output:
# This way we can show the `present` and `edit` callbacks in action.
def f_dataclass(person: PersonDataclass) -> PersonDataclass:
    return person


fl.run(f_dataclass, app_name="Demo Dataclass")
