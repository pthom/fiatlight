"""Example: using a pydantic model with Fiatlight
=================================================

(Pydantic models can be serialized by Fiatlight)

In order to register a model with Fiatlight, we can either:
-----------------------------------------------------------
  - Option 1: add the @fl.base_model_with_gui_registration decorator to the model
  - Option 2: call fl.register_base_model with the model as argument


Add fiat_attributes when registering a model:
---------------------------------------------
fiat_attributes are custom attributes that enable to customize the GUI for a given member, or to add validators.

Example
    ```python
    @fl.base_model_with_gui_registration(
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
from pydantic import BaseModel, Field, field_validator


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


# Option 1: add the @fl.base_model_with_gui_registration decorator to the model
# -----------------------------------------------------------------------------
@fl.base_model_with_gui_registration(
    name__label="Name",
    name__hint="Name (start with a capital letter)",
    age__label="Age",
    # age__range=(0, 100),   # We do not need to specify the range here, as it is already specified in the model
    preferred_number__range=(0, 30),
    preferred_number__label="Pref number",
    # Validators
    # name__validator=validate_name,  # We may choose to use the pydantic field_validator decorator instead
    preferred_number__validator=validate_preferred_number,  # or we use a fiatlight validator (which will run in the GUI only)
)
class PersonPydantic(BaseModel):
    name: str = ""
    age: int = Field(default=0, ge=0, le=100)
    preferred_number: int = 0

    def __str__(self) -> str:
        return f"{self.name} is {self.age} years old"

    @field_validator("name")
    def validate_name_field(cls, value: str) -> str:
        return validate_name(value)


# # Option 2: call fl.register_base_model with the model as argument
#           (this is often preferable, because it is less intrusive
#           as it does not modify the class definition)
# ----------------------------------------------------------------
# fl.register_base_model(
#     PersonPydantic,
#     name__label="Name",
#     name__hint="Name (start with a capital letter)",
#     age__label="Age",
#     # age__range=(0, 100),   # We do not need to specify the range here, as it is already specified in the model
#     preferred_number__range=(0, 30),
#     preferred_number__label = "Pref number",
#     # Validators
#     # name__validator=validate_name,  # We may choose to use the pydantic field_validator decorator instead
#     preferred_number__validator=validate_preferred_number,  # or we use a fiatlight validator (which will run in the GUI only)
# )
#


# Display a function that uses the model as an input and output:
# This way we can show the `present` and `edit` callbacks in action.
def f_pydantic(person: PersonPydantic) -> PersonPydantic:
    return person


fl.run(f_pydantic, app_name="Demo Pydantic")
