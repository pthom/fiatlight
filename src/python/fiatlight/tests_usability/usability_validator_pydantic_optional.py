"""In this example, an error should be displayed when the input is not an even number.
"""
import fiatlight as fl
from pydantic import BaseModel, field_validator


@fl.base_model_with_gui_registration()
class MyData(BaseModel):
    x: int = 0
    y: int = 0

    @field_validator("x")
    def check_even(cls, value: int) -> int:
        if value % 2 != 0:
            raise ValueError("x must be even")
        return value


def f(_x: MyData | None = MyData(x=2)) -> None:
    pass


fl.run(f)
