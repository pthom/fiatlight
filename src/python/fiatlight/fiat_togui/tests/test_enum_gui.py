import fiatlight as fl
from fiatlight.fiat_togui import to_gui
from fiatlight.fiat_types import FiatAttributes
from fiatlight.fiat_togui.enum_with_gui import EnumWithGui
from fiatlight.fiat_togui.tests.sample_enum import (
    SampleEnum,
    SampleEnumRegisteredDecorator,
    SampleEnumRegisteredManually,
)

NO_FIAT_ATTRIBUTES = FiatAttributes({})


def test_enum_registered() -> None:
    def foo(a: SampleEnumRegisteredManually) -> int:
        return a.value

    foo_gui = fl.FunctionWithGui(foo)
    assert isinstance(foo_gui._inputs_with_gui[0].data_with_gui, EnumWithGui)

    def foo2(a: SampleEnumRegisteredDecorator) -> int:
        return a.value

    foo2_gui = fl.FunctionWithGui(foo2)
    assert isinstance(foo2_gui._inputs_with_gui[0].data_with_gui, EnumWithGui)


def test_enum_non_registered() -> None:
    def foo(a: SampleEnum) -> int:
        return a.value

    foo_gui = fl.FunctionWithGui(foo)
    assert isinstance(foo_gui._inputs_with_gui[0].data_with_gui, EnumWithGui)


def test_enum_serialization() -> None:
    from enum import Enum

    class MyEnum(Enum):
        A = 1
        B = 2

    a = to_gui._to_data_with_gui_impl(MyEnum.A, NO_FIAT_ATTRIBUTES)
    assert a.value == MyEnum.A
    as_json = a.call_save_to_dict(a.value)
    assert as_json == {"class": "MyEnum", "type": "Enum", "value_name": "A"}
    a.value = a.call_load_from_dict({"class": "MyEnum", "type": "Enum", "value_name": "B"})
    assert a.value == MyEnum.B
