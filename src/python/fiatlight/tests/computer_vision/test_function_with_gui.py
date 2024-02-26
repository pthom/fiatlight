from fiatlight import UnspecifiedValue, Unspecified
from fiatlight.to_gui import any_function_to_function_with_gui


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
        "name": "add",
        "outputs": [{"data": {"type": "Unspecified"}, "name": "output"}],
    }

    json_data = {
        "inputs": [
            {"data": {"type": "Unspecified"}, "name": "b"},
            {"data": {"type": "Primitive", "value": 2}, "name": "a"},
        ],
        "name": "add",
        "outputs": [{"data": {"type": "Unspecified"}, "name": "output"}],
    }
    add_gui.fill_from_json(json_data)
    assert add_gui.inputs_with_gui[0].data_with_gui.value is UnspecifiedValue
    assert add_gui.inputs_with_gui[1].data_with_gui.value == 2
    assert add_gui.outputs_with_gui[0].data_with_gui.value is UnspecifiedValue
    assert add_gui.name == "add"
