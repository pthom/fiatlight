import fiatlight as fl
from pydantic import BaseModel


def usability_easy() -> None:
    def f(x: int) -> int:
        return x

    fl.run(f)


def usability_with_default_value() -> None:
    def f(x: int = 3) -> int:
        return x

    fl.run(f)


def usability_with_basemodel() -> None:
    @fl.base_model_with_gui_registration()
    class MyParam(BaseModel):
        x: int = 3
        y: str = "Hello"
        z: float = 3.14

    def f(param: MyParam) -> MyParam:
        return param

    fl.run(f)


if __name__ == "__main__":
    # usability_easy()
    # usability_with_default_value()
    usability_with_basemodel()
