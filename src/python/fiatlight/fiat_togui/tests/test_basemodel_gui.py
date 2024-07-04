import pytest
from pydantic import BaseModel, Field, field_validator

import fiatlight as fl
import fiatlight.fiat_togui.primitives_gui
from fiatlight.fiat_togui.basemodel_gui import BaseModelGui
from fiatlight import (
    FunctionWithGui,
    register_base_model,
    base_model_with_gui_registration,
    Invalid,
)
from fiatlight.fiat_togui.to_gui import _to_data_with_gui_impl
from fiatlight.fiat_types import FiatAttributes
from fiatlight.fiat_core import AnyDataWithGui


NO_FIAT_ATTRIBUTES = FiatAttributes({})


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
    def f(param: MyParam) -> int:
        return param.x

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


def test_model_with_annotated_types() -> None:
    @fl.base_model_with_gui_registration()
    class MyParam(BaseModel):
        # x is in fact of type
        #     typing.Annotated[int, Gt(gt=0)]
        x: int = Field(gt=0, default=0)

    my_param_gui = fl.fiat_togui.any_type_to_gui(MyParam)
    assert isinstance(my_param_gui, BaseModelGui)
    x_gui = my_param_gui.param_of_name("x").data_with_gui
    assert isinstance(x_gui, fiatlight.fiat_togui.primitives_gui.IntWithGui)


def test_model_with_annotated_range() -> None:
    @fl.base_model_with_gui_registration()
    class MyParam(BaseModel):
        # x is in fact of type
        #     typing.Annotated[int, Gt(gt=0), Lt(lt=0)]
        # We should be able to extract the range of possible values for Fiatlight.
        x: int = Field(gt=0, lt=10, default=0)

    my_param_gui = fl.fiat_togui.any_type_to_gui(MyParam)
    assert isinstance(my_param_gui, BaseModelGui)
    x_gui = my_param_gui.param_of_name("x").data_with_gui
    assert isinstance(x_gui, fiatlight.fiat_togui.primitives_gui.IntWithGui)

    assert "range" in x_gui.fiat_attributes
    assert x_gui.fiat_attributes["range"] == (1, 9)  # fiatlight range is inclusive (1, 9) instead of (0, 10)


def test_base_model_with_validation_errors() -> None:
    @fl.base_model_with_gui_registration()
    class MyParam(BaseModel):
        x: int = Field(gt=0, default=1)

    my_param_gui = fl.fiat_togui.any_type_to_gui(MyParam)
    assert isinstance(my_param_gui, BaseModelGui)
    x_gui = my_param_gui.param_of_name("x").data_with_gui

    # Try factor when no value is given for x
    # Factoring is possible if x > 0 (x has a default value of 1)
    my_param_gui.value = my_param_gui.construct_default_value()
    assert my_param_gui.value.x == 1
    my_param_gui.factor_dataclass_instance_with_edited_values()

    # Factoring should be possible if x has a positive value
    x_gui.value = 3
    p = my_param_gui.factor_dataclass_instance_with_edited_values()
    assert isinstance(p, MyParam)
    assert p.x == 3

    # If x is negative, factoring should return an error
    # and x_gui should be noted as an Invalid with the correct error message
    x_gui.value = -3
    factored_instance = my_param_gui.factor_dataclass_instance_with_edited_values()
    assert isinstance(factored_instance, Invalid)
    assert isinstance(x_gui.value, Invalid)
    assert x_gui.value.invalid_value == -3
    assert x_gui.value.error_message == "Input should be greater than 0"

    # If x is not of the correct type, we should catch it also
    x_gui.value = [1, 2, 3]
    factored_instance = my_param_gui.factor_dataclass_instance_with_edited_values()
    assert isinstance(factored_instance, Invalid)
    assert isinstance(x_gui.value, Invalid)
    assert x_gui.value.invalid_value == [1, 2, 3]
    assert x_gui.value.error_message == "Input should be a valid integer"


def test_base_model_with_no_default_constructor_but_constructible_type() -> None:
    class MyParam(BaseModel):
        # x does not have a default value.
        # However, its type can be constructed by default. We will use that.
        x: int

    register_base_model(MyParam)
    my_param_gui = BaseModelGui(MyParam)
    assert my_param_gui._type == MyParam
    assert my_param_gui.can_construct_default_value()
    assert my_param_gui.callbacks.default_value_provider is not None
    default_value = my_param_gui.callbacks.default_value_provider()
    assert default_value.x == 0


def test_base_model_with_no_default_constructor_and_unconstructible_type() -> None:
    class Foo(BaseModel):
        x: int

    class MyParam(BaseModel):
        # x does not have a default value.
        # Moreover, its type cannot be constructed by default.
        x: Foo

    register_base_model(MyParam)
    my_param_gui = BaseModelGui(MyParam)
    assert my_param_gui._type == MyParam
    assert my_param_gui.callbacks.default_value_provider is not None
    with pytest.raises(ValueError):
        _default_value = my_param_gui.callbacks.default_value_provider()


def test_base_model_factor_with_invalid_value() -> None:
    class MyParam(BaseModel):
        x: int = 0
        y: int = 0

        @field_validator("x")
        def check_even(cls, value: int) -> int:
            if value % 2 != 0:
                raise ValueError("x must be even")
            return value

    register_base_model(MyParam)
    my_param_gui = BaseModelGui(MyParam)
    my_param_gui.value = my_param_gui.construct_default_value()
    assert my_param_gui.value.x == 0

    # We simulate an edition with an invalid value
    my_param_gui._parameters_with_gui[0].data_with_gui.value = 1

    # But if we try to factor, we should get an Invalid
    invalid_value = my_param_gui.factor_dataclass_instance_with_edited_values()
    assert isinstance(invalid_value, Invalid)
    # However, we should have access to the invalid value
    # (even if this is not a validated instance of MyParam)
    assert isinstance(invalid_value.invalid_value, MyParam)
    assert isinstance(invalid_value.invalid_value.x, Invalid)
    assert invalid_value.invalid_value.x.invalid_value == 1

    # We also edit y
    my_param_gui._parameters_with_gui[1].data_with_gui.value = 2
    invalid_value = my_param_gui.factor_dataclass_instance_with_edited_values()
    assert isinstance(invalid_value, Invalid)
    assert isinstance(invalid_value.invalid_value, MyParam)
    assert isinstance(invalid_value.invalid_value.x, Invalid)
    assert invalid_value.invalid_value.x.invalid_value == 1
    assert invalid_value.invalid_value.y == 2


def test_base_model_with_invalid_default() -> None:
    class MyParam(BaseModel):
        x: int

        @field_validator("x")
        def check_odd(cls, value: int) -> int:
            if value % 2 == 0:
                raise ValueError("x must be odd")
            return value

    register_base_model(MyParam)
    my_param_gui = BaseModelGui(MyParam)
    assert my_param_gui._type == MyParam
    assert my_param_gui.callbacks.default_value_provider is not None
    with pytest.raises((ValueError, TypeError)):
        _default_value = my_param_gui.callbacks.default_value_provider()


def test_base_model_validation_optional() -> None:
    @fl.base_model_with_gui_registration()
    class MyData(BaseModel):
        x: int = 0

        @field_validator("x")
        def check_even(cls, value: int) -> int:
            if value % 2 != 0:
                raise ValueError("x must be even")
            return value

    from fiatlight.fiat_togui.optional_with_gui import OptionalWithGui

    inner_gui = fl.fiat_togui.any_type_to_gui(MyData)
    my_data_opt_gui = OptionalWithGui(inner_gui)

    assert isinstance(my_data_opt_gui.value, fl.fiat_types.Unspecified)
    my_data_opt_gui.value = my_data_opt_gui.construct_default_value()
    assert my_data_opt_gui.value is None

    my_data_opt_gui.value = MyData(x=2)

    my_data_opt_gui_value = my_data_opt_gui.value
    assert isinstance(my_data_opt_gui_value, MyData)
    assert my_data_opt_gui_value.x == 2


def test_decorators() -> None:
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


def test_base_model_with_fiat_attributes() -> None:
    @fl.base_model_with_gui_registration(rotation_degree__range=(-180, 180))
    class MyImageEffect(BaseModel):
        rotation_degree: int = 0

    # Test the custom attribute
    # 1. When creating the GUI manually
    my_param_gui = BaseModelGui(MyImageEffect, FiatAttributes({"rotation_degree__range": (-180, 180)}))
    rot_gui = my_param_gui._parameters_with_gui[0].data_with_gui
    assert rot_gui.fiat_attributes["range"] == (-180, 180)

    # 2. When using fiatlight machinery
    gui2 = fl.fiat_togui._any_type_to_gui_impl(MyImageEffect, NO_FIAT_ATTRIBUTES)
    assert isinstance(gui2, BaseModelGui)
    rot_gui2 = gui2._parameters_with_gui[0].data_with_gui
    assert rot_gui2.fiat_attributes["range"] == (-180, 180)

    # 3 When using fiatlight machinery with a function
    def f(effect: MyImageEffect) -> MyImageEffect:
        return effect

    f_gui = FunctionWithGui(f)
    f_gui_param_gui = f_gui.input("effect")
    rot_gui3 = f_gui_param_gui._parameters_with_gui[0].data_with_gui  # type: ignore
    assert rot_gui3.fiat_attributes["range"] == (-180, 180)

    # 4.  When using fiatlight machinery with a function where the param is optional
    def f2(effect: MyImageEffect | None = None) -> MyImageEffect | None:
        return effect

    f2_gui = FunctionWithGui(f2)
    f2_gui_param_gui = f2_gui.input("effect")
    assert isinstance(f2_gui_param_gui, fl.fiat_togui.optional_with_gui.OptionalWithGui)
    assert isinstance(f2_gui_param_gui.inner_gui, BaseModelGui)
    range_f2 = f2_gui_param_gui.inner_gui._parameters_with_gui[0].data_with_gui.fiat_attributes["range"]
    assert range_f2 == (-180, 180)


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


def test_basemodel_in_custom_function() -> None:
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

        def my_function(self) -> int:
            return 42

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
