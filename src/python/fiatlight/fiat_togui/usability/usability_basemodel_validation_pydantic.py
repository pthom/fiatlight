"""
In this example we have a base model with two validated values via pydantic.

When both are incorrect, we cannot show both errors at the same time in the GUI,
due to complex interactions between pydantic and Fiatlight.
They will be displayed one after the other, until everything is correct.

+--------------------------------+
| f                              |
| +----------------------------+ |
| | Param                      | |
| | +------------------------+ | |
| | | param                 v | |
| | +------------------------+ | |
| |                            | |
| |  ⚠ Invalid!                | |
| |  x                         | |
| |  +------------------+      | |
| |  | 1                | [-][+]|
| |  +------------------+      | |
| |  ⚠ Input should be even    | |  <== This is the first error
| |                            | |
| |  name                      | |
| |  +----------------------+  | |
| |  | ADAM                 |  | |   <== This second error will be shown after the first is fixed
| |  +----------------------+  | |
| |                            | |
| |                            | |
| +----------------------------+ |
|                                |
| +----------------------------+ |
| | Output                     | |
| | +------------------------+ | |
| | | Output: Unspecified     | | |
| +----------------------------+ |
| +----------------------------+ |


"""

import fiatlight as fl
from pydantic import BaseModel, Field, field_validator


@fl.base_model_with_gui_registration()
class MyData(BaseModel):
    # This field should be between 0 and 99 inclusive
    x: int = Field(default=1, ge=0, lt=100)
    name: str = "adam"

    @field_validator("x")
    @classmethod
    def check_x(cls, v: int) -> int:
        if v % 2 == 0:
            raise ValueError("x must be odd")
        return v

    @field_validator("name")
    @classmethod
    def check_name(cls, v: str) -> str:
        if not v.islower():
            raise ValueError("name must be lowercase")
        return v


def f(v: MyData) -> MyData:
    return v


fl.run(f)
