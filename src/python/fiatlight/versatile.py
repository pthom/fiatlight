from typing import Any, Optional, Sequence
from imgui_bundle import imgui, imgui_ctx
from fiatlight.any_data_with_gui import AnyDataWithGui
from fiatlight.function_with_gui import FunctionWithGui
from fiatlight.functions_graph import FunctionsGraph
from fiatlight.fiatlight_types import PureFunction, PureFunctionOrFunctionWithGui
from fiatlight.internal import osd_widgets
from typing import Callable


def _add_details_button(obj: Any, detail_gui: Callable[[], None]) -> None:
    with imgui_ctx.push_obj_id(obj):
        if imgui.button("show details"):
            osd_widgets.set_detail_gui(detail_gui)
        if imgui.is_item_hovered():
            osd_widgets.set_tooltip(
                "Click to show details, then open the Info tab at the bottom to see the full string"
            )


def versatile_gui_data(value: Any) -> None:
    if value is None:
        imgui.text("None")
    elif isinstance(value, int):
        imgui.text(f"Int Value={value}")
    elif isinstance(value, float):
        imgui.text(f"Float Value={value:.4f}")
        if imgui.is_item_hovered():
            osd_widgets.set_tooltip(f"{value}")
    elif isinstance(value, str):
        max_len = 30
        if len(value) > max_len:
            imgui.text(f"Str len={len(value)}")
            imgui.text('"' + value[:max_len])

            def detail_gui() -> None:
                imgui.input_text_multiline("##value_text", value)

            _add_details_button(value, detail_gui)
            if imgui.is_item_hovered():
                osd_widgets.set_tooltip(
                    "Click to show details, then open the Info tab at the bottom to see the full string"
                )
        else:
            imgui.text('"' + value + '"')
    elif isinstance(value, list):
        imgui.text(f"List len={len(value)}")
        for i, v in enumerate(value):
            if i >= 5:

                def detail_gui() -> None:
                    for i, v in enumerate(value):
                        versatile_gui_data(v)

                _add_details_button(value, detail_gui)
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
    new_value: Any = None
    if value is None:
        imgui.text("gui_set_input: unknown type (None)")
    elif isinstance(value, int):
        imgui.set_next_item_width(100)
        changed, new_value = imgui.slider_int("", value, 0, 100)
    elif isinstance(value, float):
        imgui.set_next_item_width(100)
        changed, new_value = imgui.slider_float("", value, 0.0, 100.0)
    elif isinstance(value, str):
        imgui.set_next_item_width(100)
        changed, new_value = imgui.input_text("", value)
    else:
        raise Exception(f"VersatileDataWithGui Unsupported type: {type(value)}")

    if changed:
        return new_value
    else:
        return None


class VersatileDataWithGui(AnyDataWithGui):
    def gui_data(self, function_name: str) -> None:
        imgui.push_id(str(id(self)))
        versatile_gui_data(self.value)
        imgui.pop_id()

    def gui_set_input(self) -> Optional[Any]:
        return versatile_gui_set_input(self.value)


class VersatileFunctionWithGui(FunctionWithGui):
    inner_function: PureFunction
    inner_function_name: str

    def __init__(self, function: PureFunction, function_name: Optional[str] = None):
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


def to_function_with_gui(f: PureFunctionOrFunctionWithGui) -> FunctionWithGui:
    if isinstance(f, FunctionWithGui):
        return f
    else:
        return VersatileFunctionWithGui(f)


class VersatileFunctionsGraph(FunctionsGraph):
    def __init__(self, functions: Sequence[PureFunction]) -> None:
        functions_with_gui = [to_function_with_gui(f) for f in functions]
        FunctionsGraph.__init__(self, functions_with_gui)
        # super.__init__(self, functions_with_gui)
