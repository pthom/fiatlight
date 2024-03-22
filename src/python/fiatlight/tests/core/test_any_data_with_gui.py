from fiatlight.core import AnyDataWithGui, UnspecifiedValue
from fiatlight.core import ParamKind, ParamWithGui
from fiatlight.core.to_gui import any_value_to_data_with_gui, any_typeclass_to_gui


def test_creation() -> None:
    a: AnyDataWithGui[int] = any_typeclass_to_gui("int")
    assert a.callbacks.edit is not None
    assert a.callbacks.default_value_provider is not None
    assert a.callbacks.default_value_provider() == 0


def test_primitive_serialization() -> None:
    a = any_value_to_data_with_gui(1)
    assert a.value == 1
    assert a.save_to_json() == {"type": "Primitive", "value": 1}
    a.load_from_json({"type": "Primitive", "value": 2})
    assert a.value == 2


def test_named_data_with_gui_creation() -> None:
    x = any_value_to_data_with_gui(1)
    n = ParamWithGui("x", x, ParamKind.PositionalOrKeyword, UnspecifiedValue)
    assert n.name == "x"
    assert n.data_with_gui.value == 1


def test_named_data_with_gui_serialization() -> None:
    d = any_value_to_data_with_gui(1)
    n = ParamWithGui("x", d, ParamKind.PositionalOrKeyword, UnspecifiedValue)
    assert n.save_to_json() == {"name": "x", "data": {"type": "Primitive", "value": 1}}

    n.load_from_json({"name": "x", "data": {"type": "Primitive", "value": 2}})
    assert n.name == "x"
    assert n.data_with_gui.value == 2


def test_custom_data_with_gui_serialization() -> None:
    from fiatlight.core.any_data_with_gui import Foo, FooWithGui

    # Register the Foo type with its GUI implementation (do this once at the beginning of your program)
    from fiatlight.core import ALL_GUI_FACTORIES

    ALL_GUI_FACTORIES["Foo"] = FooWithGui

    # Use the Foo type with its GUI implementation
    from fiatlight.core.to_gui import any_value_to_data_with_gui

    foo = Foo(1)
    foo_gui = any_value_to_data_with_gui(foo)
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
