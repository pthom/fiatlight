from pydantic import BaseModel

import fiatlight
from fiatlight.fiat_togui.dataclass_gui import DataclassGui, DataclassLikeGui, BaseModelGui
from fiatlight import (
    FunctionWithGui,
    register_dataclass,
    register_base_model,
    dataclass_with_gui_registration,
    base_model_with_gui_registration,
    AnyDataWithGui,
)
from dataclasses import dataclass
from fiatlight.fiat_togui.to_gui import to_data_with_gui
from fiatlight.fiat_types import CustomAttributesDict
import copy


NO_CUSTOM_ATTRIBUTES: CustomAttributesDict = {}


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
    assert f_gui_param_gui._type == MyParam
    assert len(f_gui_param_gui._parameters_with_gui) == 3
    assert f_gui_param_gui._parameters_with_gui[0].name == "x"


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

    @base_model_with_gui_registration()
    class MyParam2(BaseModel):
        x: int = 3
        y: str = "Hello"
        z: float = 3.14

    def f2(param: MyParam2) -> MyParam2:
        return param

    f2_gui = FunctionWithGui(f2)
    f2_gui_param_gui = f2_gui.input("param")
    assert isinstance(f2_gui_param_gui, BaseModelGui)
    assert f2_gui_param_gui._type == MyParam2


def test_pydantic_with_enum() -> None:
    from enum import Enum

    @fiatlight.enum_with_gui_registration
    class MyEnum(Enum):
        A = 1
        B = 2

    @fiatlight.base_model_with_gui_registration()
    class MyParam(BaseModel):
        my_enum: MyEnum = MyEnum.A
        x: int = 3

    my_param = MyParam(my_enum=MyEnum.B, x=4)

    as_dict_base_model = my_param.model_dump(mode="json")
    assert as_dict_base_model == {"my_enum": 2, "x": 4}

    my_param_gui = to_data_with_gui(my_param, NO_CUSTOM_ATTRIBUTES)
    assert my_param_gui.value == my_param

    as_dict = my_param_gui.save_to_dict(my_param_gui.value)
    assert as_dict == {"type": "Pydantic", "value": {"my_enum": 2, "x": 4}}


def test_base_model_with_custom_attributes() -> None:
    @fiatlight.base_model_with_gui_registration(rotation_degree__range=(-180, 180))
    class ImageEffect(BaseModel):
        rotation_degree: int = 0

    # Test the custom attribute
    # 1. When creating the GUI manually
    my_param_gui = BaseModelGui(ImageEffect, {"rotation_degree__range": (-180, 180)})
    rot_gui = my_param_gui._parameters_with_gui[0].data_with_gui
    assert rot_gui.custom_attrs["range"] == (-180, 180)

    # 2. When using fiatlight machinery
    gui2 = fiatlight.fiat_togui.any_type_to_gui(ImageEffect, NO_CUSTOM_ATTRIBUTES)
    assert isinstance(gui2, BaseModelGui)
    rot_gui2 = gui2._parameters_with_gui[0].data_with_gui
    assert rot_gui2.custom_attrs["range"] == (-180, 180)

    # 3 When using fiatlight machinery with a function
    def f(effect: ImageEffect) -> ImageEffect:
        return effect

    f_gui = FunctionWithGui(f)
    f_gui_param_gui = f_gui.input("effect")
    rot_gui3 = f_gui_param_gui._parameters_with_gui[0].data_with_gui  # type: ignore
    assert rot_gui3.custom_attrs["range"] == (-180, 180)

    # 4.  When using fiatlight machinery with a function where the param is optional
    def f2(effect: ImageEffect | None = None) -> ImageEffect | None:
        return effect

    f2_gui = FunctionWithGui(f2)
    f2_gui_param_gui = f2_gui.input("effect")
    assert isinstance(f2_gui_param_gui, fiatlight.fiat_togui.composite_gui.OptionalWithGui)
    assert isinstance(f2_gui_param_gui.inner_gui, BaseModelGui)
    range_f2 = f2_gui_param_gui.inner_gui._parameters_with_gui[0].data_with_gui.custom_attrs["range"]
    assert range_f2 == (-180, 180)


def test_dataclass_with_custom_attributes() -> None:
    @fiatlight.dataclass_with_gui_registration(rotation_degree__range=(-180, 180))
    class ImageEffect:
        rotation_degree: int = 0

    # 4.  When using fiatlight machinery with a function where the param is optional
    def f2(effect: ImageEffect | None = None) -> ImageEffect | None:
        return effect

    f2_gui = FunctionWithGui(f2)
    f2_gui_param_gui = f2_gui.input("effect")
    assert isinstance(f2_gui_param_gui, fiatlight.fiat_togui.composite_gui.OptionalWithGui)
    assert isinstance(f2_gui_param_gui.inner_gui, DataclassGui)
    range_f2 = f2_gui_param_gui.inner_gui._parameters_with_gui[0].data_with_gui.custom_attrs["range"]
    assert range_f2 == (-180, 180)


def test_dataclass_in_custom_function() -> None:
    @fiatlight.base_model_with_gui_registration(x__range=(0, 10))
    class Foo(BaseModel):
        x: int = 3

    class MyFunction(FunctionWithGui):
        foo_gui: AnyDataWithGui[Foo]

        def __init__(self) -> None:
            super().__init__(self.my_function)
            foo = Foo()
            self.foo_gui = to_data_with_gui(foo, NO_CUSTOM_ATTRIBUTES)
            self.internal_state_gui = self._internal_state_gui

        def my_function(self) -> None:
            return

        def _internal_state_gui(self) -> bool:
            changed = self.foo_gui.call_edit()
            return changed

    my_function = MyFunction()
    fn_attrs = my_function.foo_gui.custom_attrs
    assert fn_attrs == {"x__range": (0, 10)}
    assert isinstance(my_function.foo_gui, BaseModelGui)
    x_attrs = my_function.foo_gui._parameters_with_gui[0].data_with_gui.custom_attrs
    assert x_attrs == {"range": (0, 10)}
