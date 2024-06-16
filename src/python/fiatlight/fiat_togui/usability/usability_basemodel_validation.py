import fiatlight as fl
from pydantic import BaseModel, Field, field_validator


@fl.base_model_with_gui_registration()
class MyData(BaseModel):
    # This field should be between 0 and 99 inclusive
    x: int = Field(default=1, ge=0, lt=100)

    @field_validator("x")
    @classmethod
    def check_x(cls, v: int) -> int:
        if v % 2 == 0:
            raise ValueError("x must be odd")
        return v


def f(v: MyData) -> MyData:
    return v


fl.run(f)
