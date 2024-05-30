from typing import List, Optional

from fiatlight.fiat_types import UnspecifiedValue
from fiatlight.fiat_core import ParamKind, ParamWithGui, AnyDataWithGui
from fiatlight.fiat_togui.to_gui import (
    to_data_with_gui,
    _any_type_class_name_to_gui,
    to_type_with_gui,
)
from fiatlight.fiat_types import CustomAttributesDict


NO_CUSTOM_ATTRIBUTES: CustomAttributesDict = {}


def test_creation() -> None:
    a: AnyDataWithGui[int] = _any_type_class_name_to_gui("int", NO_CUSTOM_ATTRIBUTES)
    assert a.callbacks.edit is not None
    assert a.callbacks.default_value_provider is not None
    assert a.callbacks.default_value_provider() == 0


def test_primitive_serialization() -> None:
    a = to_data_with_gui(1, NO_CUSTOM_ATTRIBUTES)
    assert a.value == 1
    assert a.save_to_dict(a.value) == {"type": "Primitive", "value": 1}
    a.value = a.load_from_dict({"type": "Primitive", "value": 2})
    assert a.value == 2


def test_named_data_with_gui_creation() -> None:
    x = to_data_with_gui(1, NO_CUSTOM_ATTRIBUTES)
    n = ParamWithGui("x", x, ParamKind.PositionalOrKeyword, UnspecifiedValue)
    assert n.name == "x"
    assert n.data_with_gui.value == 1


def test_named_data_with_gui_serialization() -> None:
    d = to_data_with_gui(1, NO_CUSTOM_ATTRIBUTES)
    n = ParamWithGui("x", d, ParamKind.PositionalOrKeyword, UnspecifiedValue)
    assert n.save_self_value_to_dict() == {"name": "x", "data": {"type": "Primitive", "value": 1}}

    n.load_self_value_from_dict({"name": "x", "data": {"type": "Primitive", "value": 2}})
    assert n.name == "x"
    assert n.data_with_gui.value == 2


def test_pydantic_serialization() -> None:
    from pydantic import BaseModel
    from fiatlight import register_base_model

    class A(BaseModel):
        x: int
        y: str

    register_base_model(A)

    a = A(x=1, y="hello")
    a_gui = to_data_with_gui(a, NO_CUSTOM_ATTRIBUTES)
    assert a_gui.value == a

    as_dict = a_gui.save_to_dict(a_gui.value)
    assert as_dict == {"type": "Pydantic", "value": {"x": 1, "y": "hello"}}

    a2_gui = to_type_with_gui(A, NO_CUSTOM_ATTRIBUTES)
    a2_gui.value = a2_gui.load_from_dict(as_dict)
    assert isinstance(a2_gui.value, A)
    assert a2_gui.value == a

    # With composed types
    class B(BaseModel):
        a: A
        z: float

    register_base_model(B)
    b = B(a=a, z=3.14)
    b_gui = to_data_with_gui(b, NO_CUSTOM_ATTRIBUTES)
    assert b_gui.value == b

    as_dict = b_gui.save_to_dict(b_gui.value)
    assert as_dict == {"type": "Pydantic", "value": {"a": {"x": 1, "y": "hello"}, "z": 3.14}}

    b2_gui = to_type_with_gui(B, NO_CUSTOM_ATTRIBUTES)
    assert b2_gui.value is UnspecifiedValue
    b2_gui.value = b2_gui.load_from_dict(as_dict)
    assert isinstance(b2_gui.value, B)
    assert b2_gui.value == b


def test_type_storage() -> None:
    assert to_type_with_gui(int, NO_CUSTOM_ATTRIBUTES)._type == int  # type: ignore
    assert to_type_with_gui(float, NO_CUSTOM_ATTRIBUTES)._type == float  # type: ignore
    assert to_type_with_gui(str, NO_CUSTOM_ATTRIBUTES)._type == str  # type: ignore
    assert to_type_with_gui(bool, NO_CUSTOM_ATTRIBUTES)._type == bool  # type: ignore

    ListInt = List[int]
    li = to_type_with_gui(ListInt, NO_CUSTOM_ATTRIBUTES)
    assert li._type == ListInt  # type: ignore

    OptionalInt = Optional[int]
    oi = to_type_with_gui(OptionalInt, NO_CUSTOM_ATTRIBUTES)
    assert oi._type == OptionalInt  # type: ignore

    OptionalInt2 = int | None
    oi2 = to_type_with_gui(OptionalInt2, NO_CUSTOM_ATTRIBUTES)
    assert oi2._type == OptionalInt2  # type: ignore

    from fiatlight.fiat_kits.fiat_image import ImageU8_3, Image

    gi = to_type_with_gui(ImageU8_3, NO_CUSTOM_ATTRIBUTES)
    assert gi._type == Image  # type: ignore
