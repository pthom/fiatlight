import fiatlight as fl
from fiatlight.fiat_togui.dataclass_gui import DataclassGui, DataclassLikeGui
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

    # Test the present_str
    present_str_result = my_param_gui.present_str(my_param_default)
    assert present_str_result == "MyParam(x: 3, y: Hello, z: 3.14)"

    def f(param: MyParam) -> None:
        pass

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
    assert isinstance(f2_gui_param_gui, fl.fiat_togui.composite_gui.OptionalWithGui)
    assert isinstance(f2_gui_param_gui.inner_gui, DataclassGui)
    range_f2 = f2_gui_param_gui.inner_gui._parameters_with_gui[0].data_with_gui.fiat_attributes["range"]
    assert range_f2 == (-180, 180)
