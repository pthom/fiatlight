from typing import Any, Optional, Callable, Sequence
from imgui_bundle import imgui, immapp, imgui_node_editor as node_ed
from fiatlux_py import AnyDataWithGui, FunctionWithGui, FunctionsCompositionGraph


def versatile_gui_data(value: Any) -> None:
    if value is None:
        imgui.text("None")
    elif isinstance(value, int):
        imgui.text(f"Int Value={value}")
    elif isinstance(value, float):
        imgui.text(f"Float Value={value}")
    elif isinstance(value, str):
        max_len = 50
        if len(value) > max_len:
            imgui.text(f"Str len={len(value)}")
            imgui.text('"' + value[:max_len])
            if imgui.button("..."):
                imgui.open_popup("popup_value_text")

            node_ed.suspend_node_editor_canvas_immapp()
            if imgui.begin_popup("popup_value_text"):
                imgui.input_text_multiline("##value_text", value)
                imgui.end_popup()
            node_ed.resume_node_editor_canvas_immapp()
        else:
            imgui.text('"' + value + '"')
    elif isinstance(value, list):
        imgui.text(f"List len={len(value)}")
        for i, v in enumerate(value):
            if i >= 5:
                if imgui.button("..."):
                    imgui.open_popup("popup_value_list")

                node_ed.suspend_node_editor_canvas_immapp()
                if imgui.begin_popup("popup_value_list"):
                    for i, v in enumerate(value):
                        versatile_gui_data(v)
                    imgui.end_popup()
                node_ed.resume_node_editor_canvas_immapp()

                break
            else:
                versatile_gui_data(v)
    elif isinstance(value, tuple):
        # imgui.text(f"Tuple len={len(value)}")
        strs = [str(v) for v in value]
        tuple_str = "(" + ", ".join(strs) + ")"
        imgui.text(tuple_str)

    else:
        raise Exception(f"versatile_gui_data Unsupported type: {type(value)}")


def versatile_gui_set_input(value: Any) -> Optional[Any]:
    changed = False
    if value is None:
        imgui.text("gui_set_input: unknown type (None)")
    elif isinstance(value, int):
        imgui.set_next_item_width(100)
        changed, new_value = imgui.slider_int("", value, 0, 100)
    elif isinstance(value, float):
        imgui.set_next_item_width(100)
        changed, new_value = imgui.slider_float("", value, 0.0, 100.0)  # type: ignore
    elif isinstance(value, str):
        imgui.set_next_item_width(100)
        changed, new_value = imgui.input_text("", value)  # type: ignore
    else:
        raise Exception(f"VersatileDataWithGui Unsupported type: {type(value)}")

    if changed:
        return new_value
    else:
        return None


class VersatileDataWithGui(AnyDataWithGui):
    value: Any = None

    def gui_data(self, function_name: str) -> None:
        imgui.push_id(str(id(self)))
        versatile_gui_data(self.value)
        imgui.pop_id()

    def gui_set_input(self) -> Optional[Any]:
        return versatile_gui_set_input(self.value)

    def get(self) -> Optional[Any]:
        return self.value

    def set(self, v: Any) -> None:
        self.value = v


class VersatileFunctionWithGui(FunctionWithGui):
    inner_function: Callable[[Any], Any]
    inner_function_name: str

    def __init__(self, function: Callable[[Any], Any], function_name: Optional[str] = None):
        self.inner_function = function
        if function_name is not None:
            self.inner_function_name = function_name
        else:
            self.inner_function_name = function.__name__
        self.input_gui = VersatileDataWithGui()
        self.output_gui = VersatileDataWithGui()

    def f(self, x: Any) -> Any:
        return self.inner_function(x)

    def name(self) -> str:
        return self.inner_function_name

    def gui_params(self) -> bool:
        return False


class VersatileFunctionsCompositionGraph(FunctionsCompositionGraph):
    def __init__(self, functions: Sequence[Callable[[Any], Any]]) -> None:
        functions_with_gui = [VersatileFunctionWithGui(f) for f in functions]
        FunctionsCompositionGraph.__init__(self, functions_with_gui)
        # super.__init__(self, functions_with_gui)
