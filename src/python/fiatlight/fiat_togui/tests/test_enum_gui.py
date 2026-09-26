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


def test_enum_param_fiat_attributes() -> None:
    """An enum parameter receives its fiat attributes (label, tooltip...), as the other parameters do"""

    def foo(a: SampleEnum = SampleEnum.A, b: SampleEnum | None = None) -> int:
        return 0

    fl.add_fiat_attributes(foo, a__label="The a", a__tooltip="a tooltip", b__tooltip="b tooltip")
    foo_gui = fl.FunctionWithGui(foo)
    a_gui = foo_gui.input("a")
    assert isinstance(a_gui, EnumWithGui)
    assert a_gui.label == "The a"
    assert a_gui.tooltip == "a tooltip"
    assert foo_gui.input("b").tooltip == "b tooltip"  # Optional[Enum]: the attributes reach the inner enum GUI too
