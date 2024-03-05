from fiatlight.to_gui import (
    any_typeclass_to_data_handlers,
    any_value_to_data_with_gui,
    any_function_to_function_with_gui,
)
from fiatlight.fiatlight_types import UnspecifiedValue, ErrorValue

import pytest
from typing import Tuple


class Dummy:
    pass


def test_any_typeclass_to_data_with_gui() -> None:
    with pytest.raises(ValueError):
        any_typeclass_to_data_handlers("Dummy")


def test_any_value_to_data_with_gui() -> None:
    a = any_value_to_data_with_gui(1)
    assert a.value == 1


def test_any_function_to_function_with_gui_one_output() -> None:
    def add(a: int, b: int = 2) -> int:
        return a + b

    add_gui = any_function_to_function_with_gui(add)

    # Test after construction
    assert add_gui.name == "add"
    assert add_gui.f_impl == add
    assert len(add_gui.inputs_with_gui) == 2
    assert len(add_gui.outputs_with_gui) == 1
    assert add_gui.inputs_with_gui[0].name == "a"
    assert add_gui.inputs_with_gui[1].name == "b"
    assert add_gui.inputs_with_gui[0].data_with_gui.value is UnspecifiedValue
    assert add_gui.inputs_with_gui[1].data_with_gui.value == 2
    assert add_gui.outputs_with_gui[0].data_with_gui.value is UnspecifiedValue

    # Test after invoke
    add_gui.inputs_with_gui[0].data_with_gui.value = 1
    add_gui.invoke()
    assert add_gui.outputs_with_gui[0].data_with_gui.value == 3
    assert add_gui.last_exception_message is None

    # Test after invoke with different default value
    add_gui.inputs_with_gui[0].data_with_gui.value = 1
    add_gui.inputs_with_gui[1].data_with_gui.value = 3
    add_gui.invoke()
    assert add_gui.outputs_with_gui[0].data_with_gui.value == 4
    assert add_gui.last_exception_message is None

    # Test after invoke with exception
    add_gui.inputs_with_gui[0].data_with_gui.value = "a"
    add_gui.invoke()
    assert add_gui.outputs_with_gui[0].data_with_gui.value is ErrorValue
    assert add_gui.last_exception_message is not None


def test_any_function_to_function_with_gui_two_outputs() -> None:
    def add_mult(a: int, b: int = 2) -> tuple[int, int]:
        return a + b, a * b

    add_mult_gui = any_function_to_function_with_gui(add_mult)

    # Test after construction
    assert add_mult_gui.name == "add_mult"
    assert add_mult_gui.f_impl == add_mult
    assert len(add_mult_gui.inputs_with_gui) == 2
    assert len(add_mult_gui.outputs_with_gui) == 2
    assert add_mult_gui.inputs_with_gui[0].name == "a"
    assert add_mult_gui.inputs_with_gui[1].name == "b"
    assert add_mult_gui.inputs_with_gui[0].data_with_gui.value is UnspecifiedValue
    assert add_mult_gui.inputs_with_gui[1].data_with_gui.value == 2
    assert add_mult_gui.outputs_with_gui[0].data_with_gui.value is UnspecifiedValue
    assert add_mult_gui.outputs_with_gui[1].data_with_gui.value is UnspecifiedValue

    # Test after invoke
    add_mult_gui.inputs_with_gui[0].data_with_gui.value = 1
    add_mult_gui.invoke()
    assert add_mult_gui.outputs_with_gui[0].data_with_gui.value == 3
    assert add_mult_gui.outputs_with_gui[1].data_with_gui.value == 2
    assert add_mult_gui.last_exception_message is None

    # Test after invoke with different default value
    add_mult_gui.inputs_with_gui[0].data_with_gui.value = 1
    add_mult_gui.inputs_with_gui[1].data_with_gui.value = 3
    add_mult_gui.invoke()
    assert add_mult_gui.outputs_with_gui[0].data_with_gui.value == 4
    assert add_mult_gui.outputs_with_gui[1].data_with_gui.value == 3
    assert add_mult_gui.last_exception_message is None

    # Test after invoke with exception
    add_mult_gui.inputs_with_gui[0].data_with_gui.value = "a"
    add_mult_gui.invoke()
    assert add_mult_gui.outputs_with_gui[0].data_with_gui.value is ErrorValue
    assert add_mult_gui.outputs_with_gui[1].data_with_gui.value is ErrorValue
    assert add_mult_gui.last_exception_message is not None


def test_any_function_to_function_with_gui_two_outputs_old_style() -> None:
    def add_mult(a: int, b: int = 2) -> Tuple[int, int]:
        return a + b, a * b

    add_mult_gui = any_function_to_function_with_gui(add_mult)
    assert len(add_mult_gui.outputs_with_gui) == 2


# def test_any_list_to_data_with_gui() -> None:
#     from typing import List
#     import inspect
#     a: List[int] = [1, 2, 3]
#     t = type(a)
#
#     def foo(a: list[int]) -> int:
#         return len(a)
#
#     sig = inspect.signature(foo)
#
#     fg = any_function_to_function_with_gui(foo)
#
#     ag = any_value_to_data_with_gui([1, 2, 3])
#     print(ag)
