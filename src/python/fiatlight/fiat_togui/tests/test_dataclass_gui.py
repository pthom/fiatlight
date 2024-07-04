import pytest

import fiatlight as fl
from fiatlight.fiat_togui.dataclass_gui import DataclassGui
from fiatlight.fiat_togui.dataclass_like_gui import DataclassLikeGui
from fiatlight import (
    FunctionWithGui,
    register_dataclass,
    dataclass_with_gui_registration,
)
from dataclasses import dataclass
from fiatlight.fiat_types import FiatAttributes
import copy


NO_FIAT_ATTRIBUTES = FiatAttributes({})


def test_dataclass_like_gui() -> None:
    @dataclass
    class MyParam:
        x: int = 3
        y: str = "Hello"
        z: float = 3.14

    my_param_gui = DataclassLikeGui(MyParam)
    assert my_param_gui.callbacks.default_value_provider is not None
    my_param_default = my_param_gui.callbacks.default_value_provider()
    assert my_param_default.x == 3


def test_dataclass_gui() -> None:
    @dataclass
    class MyParam:
        x: int = 3
        y: str = "Hello"
        z: float = 3.14

    register_dataclass(MyParam)

    my_param_gui = DataclassGui(MyParam)

    # Test the default value provider
    assert my_param_gui.callbacks.default_value_provider is not None
    my_param_default = my_param_gui.callbacks.default_value_provider()
    assert my_param_default.x == 3
    assert my_param_default.y == "Hello"
    assert my_param_default.z == 3.14

    # Test the serialization methods
    assert my_param_gui.callbacks.save_gui_options_to_json is not None
    assert my_param_gui.callbacks.load_gui_options_from_json is not None
    # 1. Test the save_to_json method
    gui_options_dict = my_param_gui.callbacks.save_gui_options_to_json()
    # str is the only widget that saves gui options here
    assert "y" in gui_options_dict
    y_options = copy.deepcopy(gui_options_dict["y"])
    # 2. Test the load_gui_options_from_json method
    my_param_gui.load_gui_options_from_json(gui_options_dict)
    gui_options_dict2 = my_param_gui.save_gui_options_to_json()
    assert "y" in gui_options_dict2
    assert gui_options_dict2["y"] == y_options

    def f(param: MyParam) -> int:
        return param.x

    f_gui = FunctionWithGui(f)
    f_gui_param_gui = f_gui.input("param")
    assert isinstance(f_gui_param_gui, DataclassGui)
    assert f_gui_param_gui._type == MyParam


def test_decorators() -> None:
    @dataclass_with_gui_registration()
    class MyParam:
        x: int = 3
        y: str = "Hello"
        z: float = 3.14

    def f(param: MyParam) -> MyParam:
        return param

    f_gui = FunctionWithGui(f)
    f_gui_param_gui = f_gui.input("param")
    assert isinstance(f_gui_param_gui, DataclassGui)
    assert f_gui_param_gui._type == MyParam


def test_dataclass_with_fiat_attributes() -> None:
    @fl.dataclass_with_gui_registration(rotation_degree__range=(-180, 180))
    class ImageEffect:
        rotation_degree: int = 0

    # 4.  When using fiatlight machinery with a function where the param is optional
    def f2(effect: ImageEffect | None = None) -> ImageEffect | None:
        return effect

    f2_gui = FunctionWithGui(f2)
    f2_gui_param_gui = f2_gui.input("effect")
    assert isinstance(f2_gui_param_gui, fl.fiat_togui.optional_with_gui.OptionalWithGui)
    assert isinstance(f2_gui_param_gui.inner_gui, DataclassGui)
    range_f2 = f2_gui_param_gui.inner_gui._parameters_with_gui[0].data_with_gui.fiat_attributes["range"]
    assert range_f2 == (-180, 180)


def test_dataclass_default_provider() -> None:
    # A.
    # Test the default provider with no given default values.
    # In that case we should construct the members with the default constructor for the type.
    @fl.dataclass_with_gui_registration()
    class A:
        x: int

    a_gui = fl.any_type_to_gui(A)
    assert a_gui.callbacks.default_value_provider is not None
    a_default = a_gui.callbacks.default_value_provider()
    assert a_default.x == 0

    # B.
    # Test the default provider with no given default values,
    # and no default constructor for the type.
    # In that case we should raise an error.
    class NoDefaultCtor:
        def __init__(self, dummy: int):
            pass

    @fl.dataclass_with_gui_registration()
    class B:
        v: NoDefaultCtor

    b_gui = fl.any_type_to_gui(B)
    assert b_gui.callbacks.default_value_provider is not None
    with pytest.raises(ValueError):
        _b_default = b_gui.callbacks.default_value_provider()

    # C.
    # Test the default provider with given default values.
    @fl.dataclass_with_gui_registration()
    class C:
        x: int = 3

    c_gui = fl.any_type_to_gui(C)
    assert c_gui.callbacks.default_value_provider is not None
    c_default = c_gui.callbacks.default_value_provider()
    assert c_default.x == 3

    # D.
    # Test that the default provider does not have side effects.
    @fl.dataclass_with_gui_registration()
    class D:
        x: int = 3

    d_instance = D(5)  # type: ignore
    d_instance_gui = fl.to_data_with_gui(d_instance)
    assert d_instance_gui.value.x == 5  # type: ignore
    assert d_instance_gui.callbacks.default_value_provider is not None
    d_default = d_instance_gui.callbacks.default_value_provider()
    assert d_default.x == 3
    assert d_instance_gui.value.x == 5  # type: ignore
