from fiatlight.to_gui import any_function_to_function_with_gui


def test_serialization() -> None:
    def add(a: int, b: int) -> int:
        return a + b

    add_gui = any_function_to_function_with_gui(add)

    add_gui.inputs_with_gui[0].data_with_gui.value = 1

    s = add_gui.to_json()
    assert s == {
        "name": "add",
        "inputs": [{"name": "a", "data": 1}, {"name": "b", "data": None}],
        "outputs": [{"name": "output", "data": None}],
    }

    json_data = {
        "name": "add",
        "inputs": [{"name": "a", "data": None}, {"name": "b", "data": 2}],
        "outputs": [{"name": "output", "data": None}],
    }
    add_gui.fill_from_json(json_data)
    assert add_gui.inputs_with_gui[1].data_with_gui.value == 2
    assert add_gui.inputs_with_gui[0].data_with_gui.value is None
    assert add_gui.outputs_with_gui[0].data_with_gui.value is None
    assert add_gui.name == "add"
