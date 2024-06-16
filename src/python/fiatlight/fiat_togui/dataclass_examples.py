from fiatlight.fiat_togui.gui_registry import dataclass_with_gui_registration, base_model_with_gui_registration
from pydantic import BaseModel


@dataclass_with_gui_registration(x__range=(0, 10))
class ExampleDataclass:
    x: int = 0
    y: str = "Hello"


@base_model_with_gui_registration(x__range=(0, 10))
class ExampleBaseModel(BaseModel):
    x: int = 0
    y: str = "Hello"
