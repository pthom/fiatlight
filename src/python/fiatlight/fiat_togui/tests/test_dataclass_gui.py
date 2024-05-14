from fiatlight.fiat_togui.dataclass_gui import DataclassGui
from fiatlight import register_dataclass, FunctionWithGui
import copy


def test_dataclass_gui() -> None:
    from dataclasses import dataclass

    @dataclass
    class MyParam:
        x: int = 3
        y: str = "Hello"
        z: float = 3.14

    my_param_gui = DataclassGui(MyParam)

    # Test the default value provider
    assert my_param_gui.callbacks.default_value_provider is not None
    my_param_default = my_param_gui.callbacks.default_value_provider()
    assert my_param_default.x == 3
    assert my_param_default.y == "Hello"
    assert my_param_default.z == 3.14

    # Test the serialization methods
    # 1. Test the save_to_json method
    gui_options_dict = my_param_gui.save_gui_options_to_json()
    assert "y" in gui_options_dict  # str is the only widget that saves options here
    y_options = copy.deepcopy(gui_options_dict["y"])
    # 2. Test the load_gui_options_from_json method
    my_param_gui.load_gui_options_from_json(gui_options_dict)
    gui_options_dict2 = my_param_gui.save_gui_options_to_json()
    assert "y" in gui_options_dict2
    assert gui_options_dict2["y"] == y_options

    # Test the present_str
    present_str_result = my_param_gui.present_str(my_param_default)
    assert present_str_result == "MyParam(x: 3, y: Hello, z: 3.14)"

    # Test the register_type function
    register_dataclass(MyParam)

    def f(param: MyParam) -> None:
        pass

    f_gui = FunctionWithGui(f)
    f_gui_param_gui = f_gui.input("param")
    assert isinstance(f_gui_param_gui, DataclassGui)
    assert f_gui_param_gui._dataclass_type == MyParam
