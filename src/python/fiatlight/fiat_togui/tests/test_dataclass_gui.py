from pydantic import BaseModel

from fiatlight.fiat_togui.dataclass_gui import DataclassGui, DataclassLikeGui, BaseModelGui
from fiatlight import FunctionWithGui, register_dataclass, register_base_model
from dataclasses import dataclass
import copy


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
    assert f_gui_param_gui._inner_type == MyParam


def test_base_model_gui() -> None:
    class MyParam(BaseModel):
        x: int = 3
        y: str = "Hello"
        z: float = 3.14

    register_base_model(MyParam)
    my_param_gui = BaseModelGui(MyParam)
    assert my_param_gui._type == MyParam

    # Test the default value provider
    assert my_param_gui.callbacks.default_value_provider is not None
    my_param_default = my_param_gui.callbacks.default_value_provider()
    assert my_param_default.x == 3
    assert my_param_default.y == "Hello"
    assert my_param_default.z == 3.14

    # Test register_base_model
    def f(param: MyParam) -> None:
        pass

    f_gui = FunctionWithGui(f)
    f_gui_param_gui = f_gui.input("param")
    assert isinstance(f_gui_param_gui, BaseModelGui)
    assert f_gui_param_gui._inner_type == MyParam
    assert len(f_gui_param_gui._parameters_with_gui) == 3
    assert f_gui_param_gui._parameters_with_gui[0].name == "x"
