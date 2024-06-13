from pydantic import BaseModel, Field

import fiatlight as fl
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
from fiatlight.fiat_togui.to_gui import _to_data_with_gui_impl
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


def test_base_model_with_field_default() -> None:
    class MyParam(BaseModel):
        x: list[int] = Field(default=[3])

    register_base_model(MyParam)
    my_param_gui = BaseModelGui(MyParam)
    assert my_param_gui._type == MyParam
    assert my_param_gui.callbacks.default_value_provider is not None
    default_value = my_param_gui.callbacks.default_value_provider()
    assert default_value.x == [3]


def test_base_model_with_field_default_factory() -> None:
    class Foo(BaseModel):
        a: int = 0

    class MyParam(BaseModel):
        foo: Foo = Field(default_factory=Foo)
        x: int = Field(default=3)

    register_base_model(Foo)
    register_base_model(MyParam)

    my_param_gui = BaseModelGui(MyParam)
    assert my_param_gui._type == MyParam
    assert isinstance(my_param_gui.value, fl.fiat_types.Unspecified)
    assert my_param_gui.callbacks.default_value_provider is not None
    default_value = my_param_gui.callbacks.default_value_provider()
    assert isinstance(default_value.foo, Foo)
    assert default_value.x == 3


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

    @fl.enum_with_gui_registration
    class MyEnum(Enum):
        A = 1
        B = 2

    @fl.base_model_with_gui_registration()
    class MyParam(BaseModel):
        my_enum: MyEnum = MyEnum.A
        x: int = 3

    my_param = MyParam(my_enum=MyEnum.B, x=4)

    as_dict_base_model = my_param.model_dump(mode="json")
    assert as_dict_base_model == {"my_enum": 2, "x": 4}

    my_param_gui = _to_data_with_gui_impl(my_param, NO_FIAT_ATTRIBUTES)
    assert my_param_gui.value == my_param

    as_dict = my_param_gui.call_save_to_dict(my_param_gui.value)
    assert as_dict == {"type": "Pydantic", "value": {"my_enum": 2, "x": 4}}


def test_base_model_with_custom_attributes() -> None:
    @fl.base_model_with_gui_registration(rotation_degree__range=(-180, 180))
    class ImageEffect(BaseModel):
        rotation_degree: int = 0

    # Test the custom attribute
    # 1. When creating the GUI manually
    my_param_gui = BaseModelGui(ImageEffect, FiatAttributes({"rotation_degree__range": (-180, 180)}))
    rot_gui = my_param_gui._parameters_with_gui[0].data_with_gui
    assert rot_gui.fiat_attributes["range"] == (-180, 180)

    # 2. When using fiatlight machinery
    gui2 = fl.fiat_togui._any_type_to_gui_impl(ImageEffect, NO_FIAT_ATTRIBUTES)
    assert isinstance(gui2, BaseModelGui)
    rot_gui2 = gui2._parameters_with_gui[0].data_with_gui
    assert rot_gui2.fiat_attributes["range"] == (-180, 180)

    # 3 When using fiatlight machinery with a function
    def f(effect: ImageEffect) -> ImageEffect:
        return effect

    f_gui = FunctionWithGui(f)
    f_gui_param_gui = f_gui.input("effect")
    rot_gui3 = f_gui_param_gui._parameters_with_gui[0].data_with_gui  # type: ignore
    assert rot_gui3.fiat_attributes["range"] == (-180, 180)

    # 4.  When using fiatlight machinery with a function where the param is optional
    def f2(effect: ImageEffect | None = None) -> ImageEffect | None:
        return effect

    f2_gui = FunctionWithGui(f2)
    f2_gui_param_gui = f2_gui.input("effect")
    assert isinstance(f2_gui_param_gui, fl.fiat_togui.composite_gui.OptionalWithGui)
    assert isinstance(f2_gui_param_gui.inner_gui, BaseModelGui)
    range_f2 = f2_gui_param_gui.inner_gui._parameters_with_gui[0].data_with_gui.fiat_attributes["range"]
    assert range_f2 == (-180, 180)


def test_dataclass_with_custom_attributes() -> None:
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


def test_dataclass_in_custom_function() -> None:
    @fl.base_model_with_gui_registration(x__range=(0, 10))
    class Foo(BaseModel):
        x: int = 3

    class MyFunction(FunctionWithGui):
        foo_gui: AnyDataWithGui[Foo]

        def __init__(self) -> None:
            super().__init__(self.my_function)
            foo = Foo()
            self.foo_gui = _to_data_with_gui_impl(foo, NO_FIAT_ATTRIBUTES)
            self.internal_state_gui = self._internal_state_gui

        def my_function(self) -> None:
            return

        def _internal_state_gui(self) -> bool:
            changed = self.foo_gui.gui_edit()
            return changed

    foo_gui = fl.fiat_togui._any_type_to_gui_impl(Foo, NO_FIAT_ATTRIBUTES)
    assert isinstance(foo_gui, BaseModelGui)
    assert foo_gui.fiat_attributes == {"x__range": (0, 10)}
    base_model_x_attrs = foo_gui._parameters_with_gui[0].data_with_gui.fiat_attributes
    assert base_model_x_attrs == {"range": (0, 10)}

    my_function = MyFunction()

    inner_foo_gui_attrs = my_function.foo_gui.fiat_attributes
    assert inner_foo_gui_attrs == {"x__range": (0, 10)}

    assert isinstance(my_function.foo_gui, BaseModelGui)
    inner_base_model_x_attrs = my_function.foo_gui._parameters_with_gui[0].data_with_gui.fiat_attributes
    assert inner_base_model_x_attrs == {"range": (0, 10)}


def test_basemodel_with_optional_member() -> None:
    @fl.base_model_with_gui_registration(
        x__range=(0, 10),
        x__label="X Value",
        x__tooltip="This is the x value",
    )
    class MyParam(BaseModel):
        x: int | None = 3

    def f(param: MyParam) -> MyParam:
        return param

    f_gui = FunctionWithGui(f)
    f_gui_param_gui = f_gui.input("param")
    assert isinstance(f_gui_param_gui, BaseModelGui)
    assert f_gui_param_gui._type == MyParam
    f_gui_param_gui_inner = f_gui_param_gui._parameters_with_gui[0].data_with_gui
    assert f_gui_param_gui_inner.label == "X Value"
    assert f_gui_param_gui_inner.tooltip == "This is the x value"
