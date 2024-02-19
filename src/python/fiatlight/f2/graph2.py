from imgui_bundle import imgui, imgui_node_editor as ed, icons_fontawesome, immapp, ImVec2, imgui_ctx
from fiatlight.f2.any_f import ObservableFunction, PresentOutputGui, ParameterWithGui
from fiatlight.internal import fl_widgets
from fiatlight.config import config
from typing import Optional, Any, TypeVar, Generic, Callable


Input = TypeVar("Input")
Output = TypeVar("Output")
T = TypeVar("T")


class FunctionNode2(Generic[Input, Output]):
    _function: ObservableFunction[Input, Output]
    output_gui: PresentOutputGui[Output]

    _next_function_node: Optional["FunctionNode2[Output, Any]"]

    node_id: ed.NodeId
    pin_input: ed.PinId
    pin_output: ed.PinId
    link_id: ed.LinkId

    node_size: ImVec2  # will be set after the node is drawn once

    def __init__(self, function: Callable[[Input], Output], output_gui: PresentOutputGui[Output]) -> None:
        self._function = ObservableFunction(function)
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
                output = self._function.get_output()
                if output is None:
                    imgui.text("None")
                else:
                    self.output_gui(output)

        def draw_output_pin() -> None:
            if hasattr(self, "node_size"):
                imgui.same_line(self.node_size.x - immapp.em_size(2))
                ed.begin_pin(self.pin_output, ed.PinKind.output)
                imgui.text(icons_fontawesome.ICON_FA_ARROW_CIRCLE_RIGHT)
                ed.end_pin()

        def edit_params() -> bool:
            from imgui_bundle import imgui_ctx

            changed = False
            for i, param in enumerate(self._function.parameters_with_gui()):
                with imgui_ctx.push_id(f"param_{i}"):
                    if param.edit_gui is not None:
                        imgui.text(param.name + ":")
                        changed = param.edit_gui() or changed
            return changed

        ed.begin_node(self.node_id)
        draw_title()
        draw_input_pin()
        draw_exception_message()
        if edit_params():
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
    from imgui_bundle import immapp

    from fiatlight.f2.boxed import BoxedInt

    def f(param1: int, x: int) -> int:
        return param1 + x

    def edit_int(x: BoxedInt) -> bool:
        if x.value is None:
            x.value = 0
        changed, x.value = imgui.slider_int("Value", x.value, -10, 10)
        return changed

    def present_int(x: int) -> None:
        imgui.text(str(x))

    import functools
    from fiatlight.f2.any_f import FunctionWithSettableParams

    class FWrapped(FunctionWithSettableParams):  # type: ignore
        param1: BoxedInt

        def __init__(self) -> None:
            super().__init__()
            self.param1 = BoxedInt(0)
            self.parameters_with_gui = [
                ParameterWithGui[BoxedInt](
                    "param1",
                    edit_gui=functools.partial(edit_int, self.param1),
                    present_gui=functools.partial(present_int, self.param1),
                )
            ]

        def f(self, x: int) -> int:
            return f(self.param1.value, x)

        def name(self) -> str:
            return "FWrapped"

    f_wrapped = FWrapped()

    function_node = FunctionNode2(
        f_wrapped,
        output_gui=present_int,
    )

    def gui() -> None:
        ed.begin("Function Graph")
        function_node.draw_node()
        ed.end()

    immapp.run(gui, with_node_editor=True)


if __name__ == "__main__":
    sandbox()
