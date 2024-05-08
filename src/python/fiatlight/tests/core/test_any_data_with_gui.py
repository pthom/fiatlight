from fiatlight.fiat_types import UnspecifiedValue
from fiatlight.fiat_core import ParamKind, ParamWithGui, AnyDataWithGui
from fiatlight.fiat_core.to_gui import _to_data_with_gui, _any_type_class_name_to_gui


def test_creation() -> None:
    a: AnyDataWithGui[int] = _any_type_class_name_to_gui("int", globals_dict=globals(), locals_dict=locals())
    assert a.callbacks.edit is not None
    assert a.callbacks.default_value_provider is not None
    assert a.callbacks.default_value_provider() == 0


def test_primitive_serialization() -> None:
    a = _to_data_with_gui(1, globals_dict=globals(), locals_dict=locals())
    assert a.value == 1
    assert a.save_to_json() == {"type": "Primitive", "value": 1}
    a.load_from_json({"type": "Primitive", "value": 2})
    assert a.value == 2


def test_named_data_with_gui_creation() -> None:
    x = _to_data_with_gui(1, globals_dict=globals(), locals_dict=locals())
    n = ParamWithGui("x", x, ParamKind.PositionalOrKeyword, UnspecifiedValue)
    assert n.name == "x"
    assert n.data_with_gui.value == 1


def test_named_data_with_gui_serialization() -> None:
    d = _to_data_with_gui(1, globals_dict=globals(), locals_dict=locals())
    n = ParamWithGui("x", d, ParamKind.PositionalOrKeyword, UnspecifiedValue)
    assert n.save_to_json() == {"name": "x", "data": {"type": "Primitive", "value": 1}}

    n.load_from_json({"name": "x", "data": {"type": "Primitive", "value": 2}})
    assert n.name == "x"
    assert n.data_with_gui.value == 2


def test_custom_data_with_gui_serialization() -> None:
    from fiatlight.fiat_core.any_data_with_gui import Foo, FooWithGui

    # Register the Foo type with its GUI implementation (do this once at the beginning of your program)
    from fiatlight.fiat_core.to_gui import register_type

    register_type(Foo, FooWithGui)

    # Use the Foo type with its GUI implementation
    from fiatlight.fiat_core.to_gui import _to_data_with_gui

    foo = Foo(1)
    foo_gui = _to_data_with_gui(foo, globals_dict=globals(), locals_dict=locals())
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

    a = _to_data_with_gui(MyEnum.A, globals_dict=globals(), locals_dict=locals())
    assert a.value == MyEnum.A
    as_json = a.save_to_json()
    assert as_json == {"class": "MyEnum", "type": "Enum", "value_name": "A"}
    a.load_from_json({"class": "MyEnum", "type": "Enum", "value_name": "B"})
    assert a.value == MyEnum.B  # type: ignore
