from typing import List, Optional

from fiatlight.fiat_types import UnspecifiedValue
from fiatlight.fiat_core import ParamKind, ParamWithGui, AnyDataWithGui
from fiatlight.fiat_togui.to_gui import (
    to_data_with_gui,
    _any_type_class_name_to_gui,
    capture_current_scope,
    to_type_with_gui,
)


def test_creation() -> None:
    a: AnyDataWithGui[int] = _any_type_class_name_to_gui("int", capture_current_scope())
    assert a.callbacks.edit is not None
    assert a.callbacks.default_value_provider is not None
    assert a.callbacks.default_value_provider() == 0


def test_primitive_serialization() -> None:
    a = to_data_with_gui(1, capture_current_scope())
    assert a.value == 1
    assert a.save_to_dict(a.value) == {"type": "Primitive", "value": 1}
    a.value = a.load_from_dict({"type": "Primitive", "value": 2})
    assert a.value == 2


def test_named_data_with_gui_creation() -> None:
    x = to_data_with_gui(1, capture_current_scope())
    n = ParamWithGui("x", x, ParamKind.PositionalOrKeyword, UnspecifiedValue)
    assert n.name == "x"
    assert n.data_with_gui.value == 1


def test_named_data_with_gui_serialization() -> None:
    d = to_data_with_gui(1, capture_current_scope())
    n = ParamWithGui("x", d, ParamKind.PositionalOrKeyword, UnspecifiedValue)
    assert n.save_self_value_to_dict() == {"name": "x", "data": {"type": "Primitive", "value": 1}}

    n.load_self_value_from_dict({"name": "x", "data": {"type": "Primitive", "value": 2}})
    assert n.name == "x"
    assert n.data_with_gui.value == 2


def test_enum_serialization() -> None:
    from enum import Enum

    class MyEnum(Enum):
        A = 1
        B = 2

    a = to_data_with_gui(MyEnum.A, capture_current_scope())
    assert a.value == MyEnum.A
    as_json = a.save_to_dict(a.value)
    assert as_json == {"class": "MyEnum", "type": "Enum", "value_name": "A"}
    a.value = a.load_from_dict({"class": "MyEnum", "type": "Enum", "value_name": "B"})
    assert a.value == MyEnum.B


def test_pydantic_serialization() -> None:
    from pydantic import BaseModel
    from fiatlight import register_base_model

    current_scope = capture_current_scope()

    class A(BaseModel):
        x: int
        y: str

    register_base_model(A)

    a = A(x=1, y="hello")
    a_gui = to_data_with_gui(a, current_scope)
    assert a_gui.value == a

    as_dict = a_gui.save_to_dict(a_gui.value)
    assert as_dict == {"type": "Pydantic", "value": {"x": 1, "y": "hello"}}

    a2_gui = to_type_with_gui(A, current_scope)
    a2_gui.value = a2_gui.load_from_dict(as_dict)
    assert isinstance(a2_gui.value, A)
    assert a2_gui.value == a

    # With composed types
    class B(BaseModel):
        a: A
        z: float

    register_base_model(B)
    b = B(a=a, z=3.14)
    b_gui = to_data_with_gui(b, current_scope)
    assert b_gui.value == b

    as_dict = b_gui.save_to_dict(b_gui.value)
    assert as_dict == {"type": "Pydantic", "value": {"a": {"x": 1, "y": "hello"}, "z": 3.14}}

    b2_gui = to_type_with_gui(B, current_scope)
    assert b2_gui.value is UnspecifiedValue
    b2_gui.value = b2_gui.load_from_dict(as_dict)
    assert isinstance(b2_gui.value, B)
    assert b2_gui.value == b


def test_type_storage() -> None:
    scope_storage = capture_current_scope()

    assert to_type_with_gui(int, scope_storage)._type == int  # type: ignore
    assert to_type_with_gui(float, scope_storage)._type == float  # type: ignore
    assert to_type_with_gui(str, scope_storage)._type == str  # type: ignore
    assert to_type_with_gui(bool, scope_storage)._type == bool  # type: ignore

    ListInt = List[int]
    li = to_type_with_gui(ListInt, scope_storage)
    assert li._type == ListInt  # type: ignore

    OptionalInt = Optional[int]
    oi = to_type_with_gui(OptionalInt, scope_storage)
    assert oi._type == OptionalInt  # type: ignore

    OptionalInt2 = int | None
    oi2 = to_type_with_gui(OptionalInt2, scope_storage)
    assert oi2._type == OptionalInt2  # type: ignore

    from fiatlight.fiat_kits.fiat_image import ImageU8_3, Image

    gi = to_type_with_gui(ImageU8_3, scope_storage)
    assert gi._type == Image  # type: ignore
