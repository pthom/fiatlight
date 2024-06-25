"""
In this example we have a base model with two validated values via Fiatlight Attributes.

When both are incorrect, we should have a result like this: Both errors are shown.

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
| |  ⚠ Input should be even    | |
| |                            | |
| |  name                      | |
| |  +----------------------+  | |
| |  | Adam                 |  | |
| |  +----------------------+  | |
| |  ⚠ Input should be lower   | |
| |  case                      | |
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
from pydantic import BaseModel
from typing import Any


def validate_even(x: int) -> int:
    if x % 2 != 0:
        raise ValueError("Input should be even")
    return x


def validate_lower_case(s: str) -> str:
    if not s.islower():
        raise ValueError("Input should be lower case")
    return s


@fl.base_model_with_gui_registration(
    x__validator=validate_even,
    name__validator=validate_lower_case,
)
class MyParam(BaseModel):
    x: int = 0
    name: str = "adam"

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)


def f(param: MyParam) -> MyParam:
    return param


fl.run(f)
