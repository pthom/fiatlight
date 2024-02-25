from fiatlight.any_data_with_gui import NamedDataWithGui
from fiatlight.to_gui import any_value_to_data_with_gui, any_typeclass_to_data_with_gui


def test_creation() -> None:
    a = any_typeclass_to_data_with_gui(int)
    assert a.value is None
    assert a.gui_edit_impl is not None
    assert a.gui_present_impl is not None
    assert a.default_value is not None
    a.value = a.default_value()
    assert a.value == 0


def test_any_serialization() -> None:
    a = any_value_to_data_with_gui(1)
    assert a.value == 1
    print(a.to_json())
    a.fill_from_json("2")
    assert a.value == 2


def test_named_data_with_gui_creation() -> None:
    x = any_value_to_data_with_gui(1)
    n = NamedDataWithGui("x", x)
    assert n.name == "x"
    assert n.data_with_gui.value == 1


def test_named_data_with_gui_serialization() -> None:
    from fiatlight.any_data_with_gui import Foo, make_foo_with_gui, FooGuiParams

    # Register the Foo type with its GUI implementation (do this once at the beginning of your program)
    from fiatlight.all_to_gui import all_type_to_gui_info, TypeToGuiInfo

    all_type_to_gui_info().append(TypeToGuiInfo(Foo, make_foo_with_gui, FooGuiParams()))

    # Use the Foo type with its GUI implementation
    from fiatlight.to_gui import any_value_to_data_with_gui

    foo = Foo(1)
    foo_gui = any_value_to_data_with_gui(foo)
    assert foo_gui.value == foo

    assert foo_gui.to_json() == '{"x": 1}'
    foo_gui.fill_from_json('{"x": 2}')
    assert foo_gui.value.x == 2
