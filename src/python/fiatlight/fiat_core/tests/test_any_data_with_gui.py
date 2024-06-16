from fiatlight.fiat_types import UnspecifiedValue
from fiatlight.fiat_core import ParamKind, ParamWithGui, AnyDataWithGui
from fiatlight.fiat_togui.to_gui import (
    _to_data_with_gui_impl,
    _any_type_to_gui_impl,
)
from fiatlight.fiat_types import FiatAttributes


NO_FIAT_ATTRIBUTES = FiatAttributes({})


def test_creation() -> None:
    a: AnyDataWithGui[int] = _any_type_to_gui_impl(int, NO_FIAT_ATTRIBUTES)
    assert a.callbacks.edit is not None
    assert a.callbacks.default_value_provider is not None
    assert a.callbacks.default_value_provider() == 0


def test_primitive_serialization() -> None:
    a = _to_data_with_gui_impl(1, NO_FIAT_ATTRIBUTES)
    assert a.value == 1
    assert a.call_save_to_dict(a.value) == {"type": "Primitive", "value": 1}
    a.value = a.call_load_from_dict({"type": "Primitive", "value": 2})
    assert a.value == 2


def test_named_data_with_gui_creation() -> None:
    x = _to_data_with_gui_impl(1, NO_FIAT_ATTRIBUTES)
    n = ParamWithGui("x", x, ParamKind.PositionalOrKeyword, UnspecifiedValue)
    assert n.name == "x"
    assert n.data_with_gui.value == 1


def test_named_data_with_gui_serialization() -> None:
    d = _to_data_with_gui_impl(1, NO_FIAT_ATTRIBUTES)
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
    a_gui = _to_data_with_gui_impl(a, NO_FIAT_ATTRIBUTES)
    assert a_gui.value == a

    as_dict = a_gui.call_save_to_dict(a_gui.value)
    assert as_dict == {"type": "Pydantic", "value": {"x": 1, "y": "hello"}}

    a2_gui = _any_type_to_gui_impl(A, NO_FIAT_ATTRIBUTES)
    a2_gui.value = a2_gui.call_load_from_dict(as_dict)
    assert isinstance(a2_gui.value, A)
    assert a2_gui.value == a

    # With composed types
    class B(BaseModel):
        a: A
        z: float

    register_base_model(B)
    b = B(a=a, z=3.14)
    b_gui = _to_data_with_gui_impl(b, NO_FIAT_ATTRIBUTES)
    assert b_gui.value == b

    as_dict = b_gui.call_save_to_dict(b_gui.value)
    assert as_dict == {"type": "Pydantic", "value": {"a": {"x": 1, "y": "hello"}, "z": 3.14}}

    b2_gui = _any_type_to_gui_impl(B, NO_FIAT_ATTRIBUTES)
    assert b2_gui.value is UnspecifiedValue
    b2_gui.value = b2_gui.call_load_from_dict(as_dict)
    assert isinstance(b2_gui.value, B)
    assert b2_gui.value == b
