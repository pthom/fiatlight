from fiatlight.fiat_togui.to_gui import _any_type_class_name_to_gui, _to_data_with_gui, _capture_current_scope
from fiatlight.fiat_types import UnspecifiedValue, ErrorValue
from fiatlight import FunctionWithGui

from typing import Tuple, Optional


class Dummy:
    pass


def test_any_typeclass_to_data_with_gui() -> None:
    d = _any_type_class_name_to_gui("Dummy", _capture_current_scope())
    assert d.callbacks.edit is None
    assert d.callbacks.default_value_provider is None
    assert d.callbacks.default_value_provider is None


def test_any_value_to_data_with_gui() -> None:
    a = _to_data_with_gui(1, _capture_current_scope())
    assert a.value == 1


def test_any_function_to_function_with_gui_one_output() -> None:
    def add(a: int, b: int = 2) -> int:
        return a + b

    add_gui = FunctionWithGui(add)

    # Test after construction
    assert add_gui.name == "add"
    assert add_gui._f_impl == add
    assert len(add_gui._inputs_with_gui) == 2
    assert len(add_gui._outputs_with_gui) == 1
    assert add_gui._inputs_with_gui[0].name == "a"
    assert add_gui._inputs_with_gui[1].name == "b"
    assert add_gui._inputs_with_gui[0].data_with_gui.value is UnspecifiedValue
    assert add_gui._inputs_with_gui[1].default_value == 2
    assert add_gui._outputs_with_gui[0].data_with_gui.value is UnspecifiedValue

    # Test after invoke
    add_gui._inputs_with_gui[0].data_with_gui.value = 1
    add_gui.invoke()
    assert add_gui._outputs_with_gui[0].data_with_gui.value == 3
    assert add_gui._last_exception_message is None

    # Test after invoke with different default value
    add_gui._inputs_with_gui[0].data_with_gui.value = 1
    add_gui._inputs_with_gui[1].data_with_gui.value = 3
    add_gui._dirty = True
    add_gui.invoke()
    assert add_gui._outputs_with_gui[0].data_with_gui.value == 4
    assert add_gui._last_exception_message is None

    # Test after invoke with exception
    add_gui._inputs_with_gui[0].data_with_gui.value = "a"
    add_gui._dirty = True
    add_gui.invoke()
    assert add_gui._outputs_with_gui[0].data_with_gui.value is ErrorValue
    assert add_gui._last_exception_message is not None


def test_any_function_to_function_with_gui_two_outputs() -> None:
    def add_mult(a: int, b: int = 2) -> tuple[int, int]:
        return a + b, a * b

    add_mult_gui = FunctionWithGui(add_mult)

    # Test after construction
    assert add_mult_gui.name == "add_mult"
    assert add_mult_gui._f_impl == add_mult
    assert len(add_mult_gui._inputs_with_gui) == 2
    assert len(add_mult_gui._outputs_with_gui) == 2
    assert add_mult_gui._inputs_with_gui[0].name == "a"
    assert add_mult_gui._inputs_with_gui[1].name == "b"
    assert add_mult_gui._inputs_with_gui[0].data_with_gui.value is UnspecifiedValue
    assert add_mult_gui._inputs_with_gui[1].default_value == 2
    assert add_mult_gui._outputs_with_gui[0].data_with_gui.value is UnspecifiedValue
    assert add_mult_gui._outputs_with_gui[1].data_with_gui.value is UnspecifiedValue

    # Test after invoke
    add_mult_gui._inputs_with_gui[0].data_with_gui.value = 1
    add_mult_gui.invoke()
    assert add_mult_gui._outputs_with_gui[0].data_with_gui.value == 3
    assert add_mult_gui._outputs_with_gui[1].data_with_gui.value == 2
    assert add_mult_gui._last_exception_message is None

    # Test after invoke with different default value
    add_mult_gui._inputs_with_gui[0].data_with_gui.value = 1
    add_mult_gui._inputs_with_gui[1].data_with_gui.value = 3
    add_mult_gui._dirty = True
    add_mult_gui.invoke()
    assert add_mult_gui._outputs_with_gui[0].data_with_gui.value == 4
    assert add_mult_gui._outputs_with_gui[1].data_with_gui.value == 3
    assert add_mult_gui._last_exception_message is None

    # Test after invoke with exception
    add_mult_gui._inputs_with_gui[0].data_with_gui.value = "a"
    add_mult_gui._dirty = True
    add_mult_gui.invoke()
    assert add_mult_gui._outputs_with_gui[0].data_with_gui.value is ErrorValue
    assert add_mult_gui._outputs_with_gui[1].data_with_gui.value is ErrorValue
    assert add_mult_gui._last_exception_message is not None


def test_any_function_to_function_with_gui_two_outputs_old_style() -> None:
    def add_mult(a: int, b: int = 2) -> Tuple[int, int]:
        return a + b, a * b

    add_mult_gui = FunctionWithGui(add_mult)
    assert len(add_mult_gui._outputs_with_gui) == 2


def test_function_with_optional_param() -> None:
    from fiatlight.fiat_togui.composite_gui import OptionalWithGui

    def foo(a: int | None = None) -> int:
        if a is None:
            return 0
        else:
            return a + 2

    def foo2(a: Optional[int] = None) -> int:
        if a is None:
            return 0
        else:
            return a + 2

    foo_gui = FunctionWithGui(foo)
    assert isinstance(foo_gui._inputs_with_gui[0].data_with_gui, OptionalWithGui)

    foo2_gui = FunctionWithGui(foo2)
    assert isinstance(foo2_gui._inputs_with_gui[0].data_with_gui, OptionalWithGui)

    print("a")


def test_enum_gui() -> None:
    from fiatlight.fiat_togui.composite_gui import EnumWithGui
    from enum import Enum

    class MyEnum(Enum):
        A = 1
        B = 2

    scope_storage = _capture_current_scope()
    my_enum_gui = _any_type_class_name_to_gui("<enum 'MyEnum'>", scope_storage)
    assert isinstance(my_enum_gui, EnumWithGui)

    def foo(a: MyEnum) -> int:
        return a.value

    foo_gui = FunctionWithGui(foo)
    assert isinstance(foo_gui._inputs_with_gui[0].data_with_gui, EnumWithGui)
