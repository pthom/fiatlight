from imgui_bundle import hello_imgui, imgui
from pydantic import BaseModel, field_validator
import fiatlight as fl


@fl.base_model_with_gui_registration()
class Address(BaseModel):
    city: str = "Your city?"
    street: str = ""
    zip_code: str = ""

    @field_validator("city")
    def city_should_not_be_empty(cls, value: str) -> str:
        if len(value) == 0:
            raise ValueError("city should not be empty")
        return value


@fl.base_model_with_gui_registration()
class User(BaseModel):
    name: str = "John Doe"
    age: int = 19
    address: Address = Address()

    @field_validator("age")
    def cannot_be_minor(cls, value: int) -> int:
        if value < 18:
            raise ValueError("age should be at least 18")
        return value


USER = User()
MY_VALUE = 42
MY_VALUE2 = 12


def gui():
    global USER

    # Edit a pydantic model
    force_refresh = False
    if imgui.button("Set age to 42"):
        USER.age = 42
        force_refresh = True
    user_changed, USER = fl.immediate_edit("User##1", USER, force_refresh=force_refresh)
    if user_changed:
        print("User changed")

    # Edit a simple value using fiatlight (here we edit an int)
    global MY_VALUE, MY_VALUE2
    changed, MY_VALUE = fl.immediate_edit(
        "Value",
        MY_VALUE,
        edit_type="slider",
        slider_logarithmic=True,
        range=(1, 1000_000_000),
    )

    changed, MY_VALUE = fl.immediate_edit(
        "Value2",  # Error: same label used twice (Fiatlight should raise an understandable error)
        MY_VALUE2,
        edit_type="knob",
        range=(10, 20),
    )


hello_imgui.run(gui)
