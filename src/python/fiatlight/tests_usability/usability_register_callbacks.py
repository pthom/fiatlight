import fiatlight as fl
from imgui_bundle import imgui
from pydantic import BaseModel


class MyPoint3D(BaseModel):
    x: float
    y: float
    z: float


def _present_point(point: MyPoint3D) -> None:
    imgui.text(f"Point: ({point.x}, {point.y}, {point.z})")


def _edit_point(point: MyPoint3D) -> tuple[bool, MyPoint3D]:
    changed = False
    new_point = MyPoint3D(**point.model_dump())

    imgui.text("Edit Point:")
    imgui.set_next_item_width(100)
    c, new_x = imgui.input_float("X", new_point.x)
    if c:
        new_point.x = new_x
        changed = True
    imgui.set_next_item_width(100)
    c, new_y = imgui.input_float("Y", new_point.y)
    if c:
        new_point.y = new_y
        changed = True
    imgui.set_next_item_width(100)
    c, new_z = imgui.input_float("Z", new_point.z)
    if c:
        new_point.z = new_z
        changed = True

    if changed:
        return True, new_point
    else:
        return False, point


fl.register_callbacks(
    MyPoint3D,
    present=_present_point,
    edit=_edit_point,
    default=lambda: MyPoint3D(x=0.0, y=0.0, z=0.0),
)


def f(p: MyPoint3D) -> float:
    return p.x


fl.run(f)
