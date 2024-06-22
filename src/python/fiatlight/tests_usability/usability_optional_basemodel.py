from pydantic import BaseModel
import fiatlight as fl


@fl.base_model_with_gui_registration()
class MyData(BaseModel):
    x: int = 5


def foo(data: MyData | None = None) -> MyData | None:
    return data


fl.run(foo)
