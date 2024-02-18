from imgui_bundle import imgui, imgui_node_editor as ed, icons_fontawesome, immapp, ImVec2, imgui_ctx
from fiatlight.f2.any_f import ObservableFunction, EditDataGuiFunction, PresentDataGuiFunction
from fiatlight.internal import fl_widgets
from fiatlight.config import config
from typing import Optional, Any, TypeVar, Generic, TypeAlias, List, Callable


SettableParameters = TypeVar("SettableParameters")
Input = TypeVar("Input")
Output = TypeVar("Output")
T = TypeVar("T")


class ParameterWithGui(Generic[T]):
    value: T | None
    edit_gui: EditDataGuiFunction[T] | None
    present_gui: PresentDataGuiFunction[T] | None

    def __init__(
        self,
        value: T | None = None,
        edit_gui: EditDataGuiFunction[T] | None = None,
        present_gui: PresentDataGuiFunction[T] | None = None,
    ) -> None:
        self.value = value
        self.edit_gui = edit_gui
        self.present_gui = present_gui


FunctionParametersWithGui: TypeAlias = List[ParameterWithGui[Any]]


class FunctionWithWrappedParams(Generic[SettableParameters, Input, Output]):
    function_parameters_gui: FunctionParametersWithGui
    wrapped_function: Callable[[SettableParameters, Input], Output]

    def __init__(
        self,
        wrapped_function: Callable[[SettableParameters, Input], Output],
        function_parameters_gui: FunctionParametersWithGui | None,
    ) -> None:
        self.wrapped_function = wrapped_function
        self.function_parameters_gui = function_parameters_gui or []
        self.__name__ = wrapped_function.__name__

    def __call__(self, x: Input) -> Output:
        settable_parameters_list = [param.value for param in self.function_parameters_gui]
        return self.wrapped_function(*settable_parameters_list, x)  # type: ignore

    def draw_params(self) -> bool:
        params_changed = False
        for i, param in enumerate(self.function_parameters_gui):
            with imgui_ctx.push_id(f"param_{i}"):
                if param.edit_gui is not None:
                    changed_this, new_value = param.edit_gui(param.value)
                    if changed_this:
                        param.value = new_value
                        params_changed = True
        return params_changed

    def parameters(self) -> List[Any]:
        r = [param.value for param in self.function_parameters_gui]
        return r


class FunctionNode2(Generic[SettableParameters, Input, Output]):
    output_gui: PresentDataGuiFunction[Output]
    _function_with_wrapped_params: FunctionWithWrappedParams[SettableParameters, Input, Output]
    _function: ObservableFunction[Input, Output]

    # _function: ObservableFunction[Input, Output]
    # function_parameters_gui: FunctionParametersWithGui

    _next_function_node: Optional["FunctionNode2[Output, Any, Any]"]

    node_id: ed.NodeId
    pin_input: ed.PinId
    pin_output: ed.PinId
    link_id: ed.LinkId

    node_size: ImVec2  # will be set after the node is drawn once

    def __init__(
        self,
        function: Callable[[SettableParameters, Input], Output],
        output_gui: PresentDataGuiFunction[Output],
        function_parameters_gui: FunctionParametersWithGui | None = None,
    ) -> None:
        # self._function = ObservableFunction(function)
        # self.function_parameters_gui = function_parameters_gui or []
        self._function_with_wrapped_params = FunctionWithWrappedParams(function, function_parameters_gui or [])
        self._function = ObservableFunction(self._function_with_wrapped_params)
        self._function.set_input(1)

        self.output_gui = output_gui
        self._next_function_node = None

        self.node_id = ed.NodeId.create()
        self.pin_input = ed.PinId.create()
        self.pin_output = ed.PinId.create()
        self.link_id = ed.LinkId.create()

    def _old_reposition_node(self, idx: int) -> None:
        position = ed.get_node_position(self.node_id)
        if position.x == 0 and position.y == 0:
            nb_nodes_per_row = 5
            width_between_nodes = immapp.em_size(20)
            height_between_nodes = immapp.em_size(20)
            position = ImVec2(
                (idx % nb_nodes_per_row) * width_between_nodes, (idx // nb_nodes_per_row) * height_between_nodes
            )
            ed.set_node_position(self.node_id, position)

    def draw_node(self) -> None:
        ed.begin_node(self.node_id)

        def draw_title() -> None:
            imgui.text(self._function.name())

        def draw_exception_message() -> None:
            last_exception_message = self._function.last_exception_message
            if last_exception_message is None:
                return
            fl_widgets.text("Exception:\n" + last_exception_message, max_line_width=30, color=config.colors.error)

        def draw_input_pin() -> None:
            ed.begin_pin(self.pin_input, ed.PinKind.input)
            imgui.text(icons_fontawesome.ICON_FA_ARROW_CIRCLE_LEFT)
            ed.end_pin()

        def draw_function_output() -> None:
            with imgui_ctx.push_id("output"):
                if self._function.get_output() is None:
                    imgui.text("None")
                else:
                    self.output_gui(self._function.get_output())

        def draw_output_pin() -> None:
            if hasattr(self, "node_size"):
                imgui.same_line(self.node_size.x - immapp.em_size(2))
                ed.begin_pin(self.pin_output, ed.PinKind.output)
                imgui.text(icons_fontawesome.ICON_FA_ARROW_CIRCLE_RIGHT)
                ed.end_pin()

        draw_title()
        draw_input_pin()
        draw_exception_message()
        params_changed = self._function_with_wrapped_params.draw_params()
        if params_changed:
            self._call_function()
        draw_function_output()
        draw_output_pin()

        ed.end_node()
        self.node_size = imgui.get_item_rect_size()

    def _call_function(self) -> None:
        function_input = self._function.get_input()
        self._function.set_input(function_input)

    def draw_link(self) -> None:
        if self._next_function_node is None:
            return
        ed.link(self.link_id, self.pin_output, self._next_function_node.pin_input)


def sandbox() -> None:
    from typing import Tuple
    from imgui_bundle import immapp

    def f(param1: int, param2: int, x: int) -> int:
        return param1 + param2 + x

    def g(x: int) -> int:
        return x + 3

    def edit_int(x: int | None) -> Tuple[bool, int]:
        if x is None:
            x = 0
            changed = True
            return changed, x
        changed, new_value = imgui.slider_int("Value", x, -10, 10)
        return changed, new_value

    def present_int(x: int | None) -> None:
        imgui.text(str(x))
        imgui.new_line()

    # function_node = FunctionNode2(
    #     f,
    #     output_gui=present_int,
    #     function_parameters_gui=[
    #         ParameterWithGui(0, edit_int, present_int),
    #         ParameterWithGui(0, edit_int, present_int),
    #     ],
    # )

    function_node = FunctionNode2(
        g,
        output_gui=present_int,
        function_parameters_gui=[],
    )

    def gui() -> None:
        ed.begin("Function Graph")
        function_node.draw_node()
        ed.end()

    immapp.run(gui, with_node_editor=True)


if __name__ == "__main__":
    sandbox()
