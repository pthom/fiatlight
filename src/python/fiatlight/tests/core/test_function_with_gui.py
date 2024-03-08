from fiatlight import UnspecifiedValue, Unspecified
from fiatlight.core import any_function_to_function_with_gui, AnyDataWithGui
from typing import List


def test_create_function_with_gui() -> None:
    from fiatlight.core.to_gui import any_function_to_function_with_gui
    from fiatlight.core.to_gui import ALL_GUI_FACTORIES

    class Foo:
        a: int

        def __init__(self, a: int = 0):
            self.a = a

    class FooWithGui(AnyDataWithGui[Foo]):
        def __init__(self) -> None:
            super().__init__()
            self.handlers.edit = lambda x: (False, x)
            self.handlers.present = lambda x: None
            # self.handlers.to_dict_impl = lambda x: {"a": x.a}
            # self.handlers.from_dict_impl = lambda d: Foo(a=d["a"])

    ALL_GUI_FACTORIES["Foo"] = FooWithGui

    def add(foo: Foo) -> int:
        return foo.a

    add_gui = any_function_to_function_with_gui(add)
    add_gui.inputs_with_gui[0].data_with_gui.value = Foo(2)
    add_gui.invoke()
    assert add_gui.outputs_with_gui[0].data_with_gui.value == 2


def test_serialization() -> None:
    def add(a: int, b: int) -> int:
        return a + b

    add_gui = any_function_to_function_with_gui(add)
    add_gui.invoke()
    assert isinstance(add_gui.outputs_with_gui[0].data_with_gui.value, Unspecified)

    add_gui.inputs_with_gui[0].data_with_gui.value = 1

    json_data = add_gui.to_json()
    assert json_data == {
        "inputs": [
            {"data": {"type": "Primitive", "value": 1}, "name": "a"},
            {"data": {"type": "Unspecified"}, "name": "b"},
        ],
    }

    json_data = {
        "inputs": [
            {"data": {"type": "Unspecified"}, "name": "b"},
            {"data": {"type": "Primitive", "value": 2}, "name": "a"},
        ],
        "name": "add",
    }
    add_gui.fill_from_json(json_data)
    assert isinstance(add_gui.inputs_with_gui[0].data_with_gui.value, Unspecified)
    assert add_gui.inputs_with_gui[1].data_with_gui.value == 2
    assert add_gui.outputs_with_gui[0].data_with_gui.value is UnspecifiedValue
    assert add_gui.name == "add"


def test_with_list() -> None:
    def sum_list(x: List[int]) -> int:
        return sum(x)

    sum_list_gui = any_function_to_function_with_gui(sum_list)
    sum_list_gui.inputs_with_gui[0].data_with_gui.value = [1, 2, 3]
    sum_list_gui.invoke()
    assert sum_list_gui.outputs_with_gui[0].data_with_gui.value == 6
