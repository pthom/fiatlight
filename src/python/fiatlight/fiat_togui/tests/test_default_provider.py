import fiatlight as fl
import pytest


def test_with_given_default_provider() -> None:
    class MyParam:
        x: int

        def __init__(self, x: int) -> None:
            self.x = x

        def __eq__(self, other: object) -> bool:
            if not isinstance(other, MyParam):
                return False
            return self.x == other.x

    def f(param: MyParam) -> MyParam:
        return param

    f_gui = fl.FunctionWithGui(f)
    param_gui = f_gui.param_gui("param")

    assert param_gui.callbacks.default_value_provider is None
    assert not param_gui.can_construct_default_value()

    with pytest.raises(TypeError):
        param_gui.construct_default_value()

    param_gui.callbacks.default_value_provider = lambda: MyParam(42)
    assert param_gui.construct_default_value() == MyParam(42)


def test_with_default_provider_in_type() -> None:
    class MyParam:
        x: int

        def __init__(self, x: int = 42) -> None:
            self.x = x

        def __eq__(self, other: object) -> bool:
            if not isinstance(other, MyParam):
                return False
            return self.x == other.x

        def __str__(self) -> str:
            return f"MyParam({self.x})"

    def f(param: MyParam) -> MyParam:
        return param

    f_gui = fl.FunctionWithGui(f)
    param_gui = f_gui.param_gui("param")

    assert param_gui.callbacks.default_value_provider is None
    assert param_gui.can_construct_default_value()
    default_value = param_gui.construct_default_value()
    assert default_value == MyParam(42)


def test_native_function() -> None:
    import math

    cos_gui = fl.FunctionWithGui(math.cos)
    can_construct = cos_gui._inputs_with_gui[0].data_with_gui.can_construct_default_value()
    assert not can_construct
