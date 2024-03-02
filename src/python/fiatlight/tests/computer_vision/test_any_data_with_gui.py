from fiatlight.any_data_with_gui import ParamWithGui, ParamKind
from fiatlight.to_gui import any_value_to_data_with_gui, any_typeclass_to_data_handlers


def test_creation() -> None:
    a = any_typeclass_to_data_handlers(int)
    assert a.gui_edit_impl is not None
    assert a.default_value_provider is not None
    assert a.default_value_provider() == 0


def test_primitive_serialization() -> None:
    a = any_value_to_data_with_gui(1)
    assert a.value == 1
    assert a.to_json() == {"type": "Primitive", "value": 1}
    a.fill_from_json({"type": "Primitive", "value": 2})
    assert a.value == 2


def test_named_data_with_gui_creation() -> None:
    x = any_value_to_data_with_gui(1)
    n = ParamWithGui("x", x, ParamKind.PositionalOrKeyword)
    assert n.name == "x"
    assert n.data_with_gui.value == 1


def test_named_data_with_gui_serialization() -> None:
    d = any_value_to_data_with_gui(1)
    n = ParamWithGui("x", d, ParamKind.PositionalOrKeyword)
    assert n.to_json() == {"name": "x", "data": {"type": "Primitive", "value": 1}}

    n.fill_from_json({"name": "x", "data": {"type": "Primitive", "value": 2}})
    assert n.name == "x"
    assert n.data_with_gui.value == 2


def test_custom_data_with_gui_serialization() -> None:
    from fiatlight.any_data_with_gui import Foo, make_foo_gui_handlers, FooGuiParams

    # Register the Foo type with its GUI implementation (do this once at the beginning of your program)
    from fiatlight.all_to_gui import all_type_to_gui_info, TypeToGuiHandlers

    all_type_to_gui_info().append(TypeToGuiHandlers(Foo, make_foo_gui_handlers, FooGuiParams()))

    # Use the Foo type with its GUI implementation
    from fiatlight.to_gui import any_value_to_data_with_gui

    foo = Foo(1)
    foo_gui = any_value_to_data_with_gui(foo)
    assert foo_gui.value == foo
    assert foo_gui.to_json() == {"type": "Dict", "value": {"x": 1}}

    foo_gui.fill_from_json({"type": "Dict", "value": {"x": 2}})
    assert isinstance(foo_gui.value, Foo)
    assert foo_gui.value.x == 2

    named_data = ParamWithGui("foo", foo_gui, ParamKind.PositionalOrKeyword)
    assert named_data.to_json() == {"name": "foo", "data": {"type": "Dict", "value": {"x": 2}}}

    named_data.fill_from_json({"name": "foo", "data": {"type": "Dict", "value": {"x": 3}}})
    assert named_data.name == "foo"
    assert isinstance(named_data.data_with_gui.value, Foo)
    assert named_data.data_with_gui.value.x == 3
