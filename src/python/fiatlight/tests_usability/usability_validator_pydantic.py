"""In this example, an error should be displayed when the input is not an even number.
"""
import fiatlight as fl
from pydantic import BaseModel, field_validator


@fl.base_model_with_gui_registration()
class MyData(BaseModel):
    even_int: int

    @field_validator("even_int")
    def check_even(cls, value: int) -> int:
        if value % 2 != 0:
            raise ValueError("even_int must be even")
        return value


def f(_data: MyData) -> None:
    pass


fl.run(f)
