import fiatlight as fl
from pydantic import BaseModel, Field


@fl.base_model_with_gui_registration()
class InnerInner1(BaseModel):
    a: int = 0
    b: int = 0


@fl.base_model_with_gui_registration()
class Inner1(BaseModel):
    c: int = 0
    d: int = 0
    sub: InnerInner1 = Field(default_factory=InnerInner1)


@fl.base_model_with_gui_registration()
class Inner2(BaseModel):
    x: int = 0
    y: int = 0


@fl.base_model_with_gui_registration()
class Outer(BaseModel):
    p: int = 0
    inner1: Inner1 = Field(default_factory=Inner1)
    inner2: Inner2 | None = None


def f(param: Outer) -> Outer:
    return param


def main() -> None:
    fl.run(f, app_name="nested_base_model")


if __name__ == "__main__":
    main()
