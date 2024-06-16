import fiatlight
from fiatlight.fiat_core import AnyDataWithGui, FunctionWithGui
from fiatlight.fiat_togui.primitives_gui import IntWithGui
from fiatlight.fiat_togui.optional_with_gui import OptionalWithGui
from fiatlight.fiat_togui.gui_registry import register_type
from dataclasses import dataclass
from typing import List, Optional


def test_basic() -> None:
    def f(int_param: int) -> int:
        return int_param + 1

    f_gui = FunctionWithGui(f)

    int_param = f_gui.param("int_param")
    assert isinstance(int_param.data_with_gui, IntWithGui)
    output = f_gui.output(0)
    assert isinstance(output, IntWithGui)

    int_param.data_with_gui.value = 10
    f_gui.invoke()
    assert output.value == 11


################################################################################################################
#  More advanced tests, where we derive from FunctionWithGui
################################################################################################################


# 1. Simple derivation
# --------------------
# In this example, FooGui inherits from FunctionWithGui, its method f is the function to be called.
# We will test that the parameters and output are correctly created, with the correct GUI types.
def test_with_class_function() -> None:
    class FooGui(FunctionWithGui):
        nb: int = 10

        def __init__(self) -> None:
            super().__init__(self.f)

        def f(self, int_param: int) -> int:
            return int_param + self.nb

    foo_gui = FooGui()
    int_param = foo_gui.param("int_param")
    assert isinstance(int_param.data_with_gui, IntWithGui)
    output = foo_gui.output(0)
    assert isinstance(output, IntWithGui)


# 2. Derivation, using module global types
# ----------------------------------------
# In this example, FooGui inherits from FunctionWithGui, its method f is the function to be called.
# We will test that the parameters and output are correctly created, with the correct GUI types,
# even if the types are defined and registered in the module global scope.


# Create our module global type
@dataclass
class IntWrapper:
    value: int = 0


# Create a GUI type for our local type
class IntWrapperWithGui(AnyDataWithGui[IntWrapper]):
    def __init__(self) -> None:
        super().__init__(IntWrapper)


# Register the GUI type as a module global type
fiatlight.register_type(IntWrapper, IntWrapperWithGui)


def test_with_class_function_and_module_global_types() -> None:
    class FooGui(FunctionWithGui):
        nb: int = 10

        def __init__(self) -> None:
            super().__init__(self.f)

        def f(self, int_wrapper_param: IntWrapper) -> IntWrapper:
            return IntWrapper(int_wrapper_param.value + self.nb)

    foo_gui = FooGui()
    int_wrapper_param = foo_gui.param("int_wrapper_param")
    assert isinstance(int_wrapper_param.data_with_gui, IntWrapperWithGui)
    output = foo_gui.output(0)
    assert isinstance(output, IntWrapperWithGui)


# 2. Derivation, using local types
# --------------------------------
# In this example, FooGui inherits from FunctionWithGui, its method f is the function to be called.
# We will test that the parameters and output are correctly created, with the correct GUI types,
# even if the types are defined in the local scope.
def test_with_class_function_and_local_types() -> None:
    # Create our local type
    @dataclass
    class IntWrapperLocal:
        value: int = 0

    # Create a GUI type for our local type
    class IntWrapperLocalWithGui(AnyDataWithGui[IntWrapperLocal]):
        def __init__(self) -> None:
            super().__init__(IntWrapperLocal)

    # Register the GUI type as a module global type
    register_type(IntWrapperLocal, IntWrapperLocalWithGui)

    class FooGui(FunctionWithGui):
        nb: int = 10

        def __init__(self) -> None:
            super().__init__(self.f)

        def f(self, int_wrapper_param: IntWrapperLocal) -> IntWrapperLocal:
            return IntWrapperLocal(int_wrapper_param.value + self.nb)

    foo_gui = FooGui()
    int_wrapper_param = foo_gui.param("int_wrapper_param")
    assert isinstance(int_wrapper_param.data_with_gui, IntWrapperLocalWithGui)
    output = foo_gui.output(0)
    assert isinstance(output, IntWrapperLocalWithGui)


################################################################################################################
#  Tests with composite types
################################################################################################################
@dataclass
class A:
    value: int = 0


class AWithGui(AnyDataWithGui[A]):
    def __init__(self) -> None:
        super().__init__(A)


register_type(A, AWithGui)


def test_optional_composite_type() -> None:
    def f(input_optional: Optional[A]) -> A | None:
        return None

    f_gui = FunctionWithGui(f)

    input_optional = f_gui.param("input_optional")
    assert isinstance(input_optional.data_with_gui, OptionalWithGui)
    assert isinstance(input_optional.data_with_gui.inner_gui, AWithGui)

    o = f_gui.output(0)
    assert isinstance(o, OptionalWithGui)
    assert isinstance(o.inner_gui, AWithGui)


################################################################################################################
#  Other tests
################################################################################################################
def test_with_list() -> None:
    def sum_list(x: List[int]) -> int:
        return sum(x)

    sum_list_gui = fiatlight.FunctionWithGui(sum_list)
    sum_list_gui._inputs_with_gui[0].data_with_gui.value = [1, 2, 3]
    sum_list_gui.invoke()
    assert sum_list_gui._outputs_with_gui[0].data_with_gui.value == 6
