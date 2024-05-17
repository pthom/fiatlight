from typing import List, Optional

from fiatlight.fiat_types import UnspecifiedValue
from fiatlight.fiat_core import ParamKind, ParamWithGui, AnyDataWithGui
from fiatlight.fiat_togui.to_gui import (
    to_data_with_gui,
    _any_type_class_name_to_gui,
    capture_current_scope,
    any_type_to_gui,
)


def test_creation() -> None:
    a: AnyDataWithGui[int] = _any_type_class_name_to_gui("int", capture_current_scope())
    assert a.callbacks.edit is not None
    assert a.callbacks.default_value_provider is not None
    assert a.callbacks.default_value_provider() == 0


def test_primitive_serialization() -> None:
    a = to_data_with_gui(1, capture_current_scope())
    assert a.value == 1
    assert a.save_to_json() == {"type": "Primitive", "value": 1}
    a.load_from_json({"type": "Primitive", "value": 2})
    assert a.value == 2


def test_named_data_with_gui_creation() -> None:
    x = to_data_with_gui(1, capture_current_scope())
    n = ParamWithGui("x", x, ParamKind.PositionalOrKeyword, UnspecifiedValue)
    assert n.name == "x"
    assert n.data_with_gui.value == 1


def test_named_data_with_gui_serialization() -> None:
    d = to_data_with_gui(1, capture_current_scope())
    n = ParamWithGui("x", d, ParamKind.PositionalOrKeyword, UnspecifiedValue)
    assert n.save_to_json() == {"name": "x", "data": {"type": "Primitive", "value": 1}}

    n.load_from_json({"name": "x", "data": {"type": "Primitive", "value": 2}})
    assert n.name == "x"
    assert n.data_with_gui.value == 2


def test_custom_data_with_gui_serialization() -> None:
    from fiatlight.fiat_core.any_data_with_gui import Foo, FooWithGui

    # Register the Foo type with its GUI implementation (do this once at the beginning of your program)
    from fiatlight.fiat_togui.to_gui import register_type

    register_type(Foo, FooWithGui)

    # Use the Foo type with its GUI implementation
    from fiatlight.fiat_togui.to_gui import to_data_with_gui

    foo = Foo(1)
    foo_gui = to_data_with_gui(foo, capture_current_scope())
    assert foo_gui.value == foo
    assert foo_gui.save_to_json() == {"type": "Dict", "value": {"x": 1}}

    foo_gui.load_from_json({"type": "Dict", "value": {"x": 2}})
    assert isinstance(foo_gui.value, Foo)
    assert foo_gui.value.x == 2

    named_data = ParamWithGui("foo", foo_gui, ParamKind.PositionalOrKeyword, UnspecifiedValue)
    assert named_data.save_to_json() == {"name": "foo", "data": {"type": "Dict", "value": {"x": 2}}}

    named_data.load_from_json({"name": "foo", "data": {"type": "Dict", "value": {"x": 3}}})
    assert named_data.name == "foo"
    assert isinstance(named_data.data_with_gui.value, Foo)
    assert named_data.data_with_gui.value.x == 3


def test_enum_serialization() -> None:
    from enum import Enum

    class MyEnum(Enum):
        A = 1
        B = 2

    a = to_data_with_gui(MyEnum.A, capture_current_scope())
    assert a.value == MyEnum.A
    as_json = a.save_to_json()
    assert as_json == {"class": "MyEnum", "type": "Enum", "value_name": "A"}
    a.load_from_json({"class": "MyEnum", "type": "Enum", "value_name": "B"})
    assert a.value == MyEnum.B  # type: ignore


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

    as_dict = a_gui.save_to_json()
    assert as_dict == {"type": "Pydantic", "value": {"x": 1, "y": "hello"}}

    a2_gui = any_type_to_gui(A, current_scope)
    a2_gui.load_from_json(as_dict)
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

    as_dict = b_gui.save_to_json()
    assert as_dict == {"type": "Pydantic", "value": {"a": {"x": 1, "y": "hello"}, "z": 3.14}}

    b2_gui = any_type_to_gui(B, current_scope)
    assert b2_gui.value is UnspecifiedValue
    b2_gui.load_from_json(as_dict)
    assert isinstance(b2_gui.value, B)
    assert b2_gui.value == b


def test_type_storage() -> None:
    scope_storage = capture_current_scope()

    assert any_type_to_gui(int, scope_storage)._type == int  # type: ignore
    assert any_type_to_gui(float, scope_storage)._type == float  # type: ignore
    assert any_type_to_gui(str, scope_storage)._type == str  # type: ignore
    assert any_type_to_gui(bool, scope_storage)._type == bool  # type: ignore

    ListInt = List[int]
    li = any_type_to_gui(ListInt, scope_storage)
    assert li._type == ListInt  # type: ignore

    OptionalInt = Optional[int]
    oi = any_type_to_gui(OptionalInt, scope_storage)
    assert oi._type == OptionalInt  # type: ignore

    OptionalInt2 = int | None
    oi2 = any_type_to_gui(OptionalInt2, scope_storage)
    assert oi2._type == OptionalInt2  # type: ignore

    from fiatlight.fiat_kits.fiat_image import ImageU8_3, Image

    gi = any_type_to_gui(ImageU8_3, scope_storage)
    assert gi._type == Image  # type: ignore
