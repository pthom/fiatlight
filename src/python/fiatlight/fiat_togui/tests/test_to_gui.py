import pytest

from fiatlight.fiat_togui import to_gui, gui_registry
from fiatlight.fiat_types import UnspecifiedValue, ErrorValue
from fiatlight import FunctionWithGui
from fiatlight.fiat_types import FiatAttributes

from typing import Tuple, Optional, NewType
import typing


class Dummy:
    pass


NO_FIAT_ATTRIBUTES = FiatAttributes({})


def test_type_member_simple() -> None:
    assert to_gui._any_type_to_gui_impl(int, NO_FIAT_ATTRIBUTES)._type == int
    assert to_gui._any_type_to_gui_impl(float, NO_FIAT_ATTRIBUTES)._type == float
    assert to_gui._any_type_to_gui_impl(str, NO_FIAT_ATTRIBUTES)._type == str
    assert to_gui._any_type_to_gui_impl(bool, NO_FIAT_ATTRIBUTES)._type == bool


def test_type_new_type() -> None:
    from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui_UnregisteredType

    MyInt = typing.NewType("MyInt", int)
    my_int_gui = to_gui._any_type_to_gui_impl(MyInt, NO_FIAT_ATTRIBUTES)
    assert isinstance(my_int_gui, AnyDataWithGui_UnregisteredType)
    assert my_int_gui.unregistered_typename == "fiatlight.fiat_togui.tests.test_to_gui.MyInt"
    assert my_int_gui._type is MyInt


def test_register_new_type() -> None:
    from fiatlight.fiat_togui.primitives_gui import IntWithGui

    EvenInt = NewType("EvenInt", int)

    with pytest.raises(ValueError):
        # fiatlight requires that the type is documented
        gui_registry.register_typing_new_type(EvenInt, IntWithGui)

    EvenInt.__doc__ = "Even integer (synonym for int) (NewType)"
    gui_registry.register_typing_new_type(EvenInt, IntWithGui)

    event_int_gui = to_gui._any_new_type_to_gui_impl(EvenInt, NO_FIAT_ATTRIBUTES)
    assert isinstance(event_int_gui, IntWithGui)


def test_type_optional() -> None:
    from typing import Union
    from fiatlight.fiat_togui.optional_with_gui import OptionalWithGui

    OptIntUnion = Union[int, None]
    opt_int_union_gui = to_gui._any_type_to_gui_impl(OptIntUnion, NO_FIAT_ATTRIBUTES)
    assert isinstance(opt_int_union_gui, OptionalWithGui)

    OptIntOptional = Optional[int]
    opt_int_optional_gui = to_gui._any_type_to_gui_impl(OptIntOptional, NO_FIAT_ATTRIBUTES)
    assert isinstance(opt_int_optional_gui, OptionalWithGui)

    OptIntNone = int | None
    opt_int_none_gui = to_gui._any_type_to_gui_impl(OptIntNone, NO_FIAT_ATTRIBUTES)
    assert isinstance(opt_int_none_gui, OptionalWithGui)


def test_tuple_type() -> None:
    from fiatlight.fiat_togui.tuple_with_gui import TupleWithGui
    from fiatlight.fiat_togui.primitives_gui import IntWithGui
    from fiatlight.fiat_togui.str_with_gui import StrWithGui

    IntAndStr = tuple[int, str]
    fiat_attributes = FiatAttributes({"0_range": (0, 5), "1_type": "email"})
    int_and_str_gui = to_gui._any_type_to_gui_impl(IntAndStr, fiat_attributes)
    assert isinstance(int_and_str_gui, TupleWithGui)
    assert len(int_and_str_gui._inner_guis) == 2
    assert isinstance(int_and_str_gui._inner_guis[0], IntWithGui)
    assert int_and_str_gui._inner_guis[0].fiat_attributes["range"] == (0, 5)
    assert isinstance(int_and_str_gui._inner_guis[1], StrWithGui)
    assert int_and_str_gui._inner_guis[1].fiat_attributes["type"] == "email"


def test_list_type() -> None:
    from fiatlight.fiat_togui.list_with_gui import ListWithGui
    from fiatlight.fiat_togui.primitives_gui import IntWithGui

    ListInt = list[int]
    list_int_gui = to_gui._any_type_to_gui_impl(ListInt, NO_FIAT_ATTRIBUTES)
    assert isinstance(list_int_gui, ListWithGui)
    assert isinstance(list_int_gui.inner_gui, IntWithGui)
    assert list_int_gui.inner_gui._type is int


def test_enum_type() -> None:
    from enum import Enum
    from fiatlight.fiat_togui.enum_with_gui import EnumWithGui

    class MyEnum(Enum):
        a = "a"
        b = "b"

    my_enum_gui = to_gui._any_type_to_gui_impl(MyEnum, NO_FIAT_ATTRIBUTES)
    assert isinstance(my_enum_gui, EnumWithGui)
    assert my_enum_gui.enum_type is MyEnum


def test_any_value_to_data_with_gui() -> None:
    a = to_gui._to_data_with_gui_impl(1, NO_FIAT_ATTRIBUTES)
    assert a.value == 1


def test_any_function_to_function_with_gui_one_output() -> None:
    def add(a: int, b: int = 2) -> int:
        return a + b

    add_gui = FunctionWithGui(add)

    # Test after construction
    assert add_gui.function_name == "add"
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
    assert add_mult_gui.function_name == "add_mult"
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
    from fiatlight.fiat_togui.optional_with_gui import OptionalWithGui

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


def test_annotated_type() -> None:
    from dataclasses import dataclass
    from typing import Annotated
    from fiatlight.fiat_togui.primitives_gui import IntWithGui

    @dataclass
    class ValueRange:
        lo: int
        hi: int

    @dataclass
    class MultipleOf:
        value: int

    Int_0_10 = Annotated[int, ValueRange(0, 10), MultipleOf(2)]

    int_0_10_gui = to_gui.any_type_to_gui(Int_0_10)
    assert isinstance(int_0_10_gui, IntWithGui)


def test_annotated_pydantic_type() -> None:
    import fiatlight as fl
    from fiatlight.fiat_togui.primitives_gui import IntWithGui
    from fiatlight.fiat_togui.basemodel_gui import BaseModelGui
    from pydantic import BaseModel, Field

    @fl.base_model_with_gui_registration()
    class MyParam(BaseModel):
        # x is in fact of type
        #     typing.Annotated[int, Gt(gt=0), Lt(lt=0)]
        # We should be able to extract the range of possible values for Fiatlight.
        x: int = Field(gt=0, lt=10, default=0)

    my_param_gui = fl.fiat_togui.any_type_to_gui(MyParam)
    assert isinstance(my_param_gui, BaseModelGui)
    x_gui = my_param_gui.param_of_name("x").data_with_gui
    assert isinstance(x_gui, IntWithGui)

    # assert hasattr(x_gui.fiat_attributes, "range")
    # assert x_gui.fiat_attributes["range"] == (0, 10)
