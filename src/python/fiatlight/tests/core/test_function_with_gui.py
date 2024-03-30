from fiatlight.fiat_core import to_function_with_gui, AnyDataWithGui
from typing import List


def test_create_function_with_gui() -> None:
    from fiatlight.fiat_core.to_gui import to_function_with_gui
    from fiatlight.fiat_core.to_gui import gui_factories

    class Foo:
        a: int

        def __init__(self, a: int = 0):
            self.a = a

    class FooWithGui(AnyDataWithGui[Foo]):
        def __init__(self) -> None:
            super().__init__()
            self.callbacks.edit = lambda: False

    gui_factories().register_factory("Foo", FooWithGui)

    def add(foo: Foo) -> int:
        return foo.a

    add_gui = to_function_with_gui(add)
    add_gui._inputs_with_gui[0].data_with_gui.value = Foo(2)
    add_gui.invoke()
    assert add_gui._outputs_with_gui[0].data_with_gui.value == 2


def test_with_list() -> None:
    def sum_list(x: List[int]) -> int:
        return sum(x)

    sum_list_gui = to_function_with_gui(sum_list)
    sum_list_gui._inputs_with_gui[0].data_with_gui.value = [1, 2, 3]
    sum_list_gui.invoke()
    assert sum_list_gui._outputs_with_gui[0].data_with_gui.value == 6
