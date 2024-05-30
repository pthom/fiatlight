import pytest

from fiatlight.fiat_togui import to_gui
from fiatlight.fiat_types import UnspecifiedValue, ErrorValue
from fiatlight import FunctionWithGui
from fiatlight.fiat_types import CustomAttributesDict

from typing import Tuple, Optional, NewType
import typing


class Dummy:
    pass


NO_CUSTOM_ATTRIBUTES: CustomAttributesDict = {}


def test_fully_qualified_name_to_gui() -> None:
    assert to_gui.fully_qualified_typename(int) == "int"
    assert to_gui.fully_qualified_typename(str) == "str"
    assert to_gui.fully_qualified_typename(list) == "list"
    from fiatlight.fiat_togui.tests.sample_enum import SampleEnumNotRegistered

    assert (
        to_gui.fully_qualified_typename(SampleEnumNotRegistered)
        == "fiatlight.fiat_togui.tests.sample_enum.SampleEnumNotRegistered"
    )

    with pytest.raises(AssertionError):
        to_gui.fully_qualified_typename(int | None)  # type: ignore


def test_register_new_type() -> None:
    from fiatlight.fiat_togui.primitives_gui import IntWithGui

    EvenInt = NewType("EvenInt", int)

    with pytest.raises(ValueError):
        # fiatlight requires that the type is documented
        to_gui.register_typing_new_type(EvenInt, IntWithGui)

    EvenInt.__doc__ = "Even integer (synonym for int) (NewType)"
    to_gui.register_typing_new_type(EvenInt, IntWithGui)


def test_type_member_simple() -> None:
    assert to_gui.any_type_to_gui(int, NO_CUSTOM_ATTRIBUTES)._type == int
    assert to_gui.any_type_to_gui(float, NO_CUSTOM_ATTRIBUTES)._type == float
    assert to_gui.any_type_to_gui(str, NO_CUSTOM_ATTRIBUTES)._type == str
    assert to_gui.any_type_to_gui(bool, NO_CUSTOM_ATTRIBUTES)._type == bool


def test_type_member_composed() -> None:
    with pytest.raises(ValueError):
        # We should not call any_composed_type_to_gui with a simple type
        to_gui.any_composed_type_to_gui(int, NO_CUSTOM_ATTRIBUTES)

    from fiatlight.fiat_togui.composite_gui import OptionalWithGui, ListWithGui

    OptionalInt = Optional[int]
    oi = to_gui.any_composed_type_to_gui(OptionalInt, NO_CUSTOM_ATTRIBUTES)
    assert oi._type == typing.Optional[int]
    assert isinstance(oi, OptionalWithGui)
    assert oi.inner_gui._type == int

    OptionalInt2 = int | None
    oi2 = to_gui.any_composed_type_to_gui(OptionalInt2, NO_CUSTOM_ATTRIBUTES)
    assert oi2._type == typing.Optional[int]
    assert isinstance(oi2, OptionalWithGui)
    assert oi2.inner_gui._type == int

    ListInt = typing.List[int]
    li = to_gui.any_composed_type_to_gui(ListInt, NO_CUSTOM_ATTRIBUTES)
    assert li._type == typing.List[int]
    assert isinstance(li, ListWithGui)
    assert li.inner_gui._type == int

    ListInt2 = list[int]
    li2 = to_gui.any_composed_type_to_gui(ListInt2, NO_CUSTOM_ATTRIBUTES)
    assert li2._type == typing.List[int]
    assert isinstance(li2, ListWithGui)
    assert li2.inner_gui._type == int

    ListOptionalInt = list[int | None]
    loi = to_gui.any_composed_type_to_gui(ListOptionalInt, NO_CUSTOM_ATTRIBUTES)
    assert loi._type == typing.List[typing.Optional[int]]
    assert isinstance(loi, ListWithGui)
    assert loi.inner_gui._type == typing.Optional[int]


def test_image_new_type_to_gui() -> None:
    # Complex case:
    # Images are handled by a Gui that can handle multiple types defined by NewType
    from fiatlight.fiat_kits.fiat_image import ImageU8_3, ImageWithGui

    gi = to_gui.any_typing_new_type_to_gui(ImageU8_3, NO_CUSTOM_ATTRIBUTES)

    # gi._type is equal to
    #    typing.Union[
    #    fiatlight.fiat_kits.fiat_image.image_types.ImageU8_1,
    #    fiatlight.fiat_kits.fiat_image.image_types.ImageU8_2,
    #    fiatlight.fiat_kits.fiat_image.image_types.ImageU8_3,
    #    fiatlight.fiat_kits.fiat_image.image_types.ImageU8_4,
    #    ...]

    assert isinstance(gi, ImageWithGui)


def test_any_typeclass_to_data_with_gui() -> None:
    d = to_gui._any_typename_to_gui("Dummy", NO_CUSTOM_ATTRIBUTES)
    assert d.callbacks.edit is None
    assert d.callbacks.default_value_provider is None
    assert d.callbacks.default_value_provider is None


def test_any_value_to_data_with_gui() -> None:
    a = to_gui.to_data_with_gui(1, NO_CUSTOM_ATTRIBUTES)
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
