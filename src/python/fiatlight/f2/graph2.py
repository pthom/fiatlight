from imgui_bundle import imgui, imgui_node_editor as ed, icons_fontawesome, immapp, ImVec2, imgui_ctx
from fiatlight.f2.any_f import ObservableFunction, EditDataGuiFunction, PresentDataGuiFunction
from fiatlight.internal import fl_widgets
from fiatlight.config import config
from typing import Optional, Any, TypeVar, Generic


Input = TypeVar("Input")
Output = TypeVar("Output")


class FunctionNode2(Generic[Input, Output]):
    _function: ObservableFunction[Input, Output]
    _next_function_node: Optional["FunctionNode2[Output, Any]"]

    params_gui: EditDataGuiFunction[Input]
    output_gui: PresentDataGuiFunction[Output]

    node_id: ed.NodeId
    pin_input: ed.PinId
    pin_output: ed.PinId
    link_id: ed.LinkId

    def __init__(
        self,
        function: ObservableFunction[Input, Output],
        params_gui: EditDataGuiFunction[Input],
        output_gui: PresentDataGuiFunction[Output],
    ) -> None:
        self._function = function
        self._next_function_node = None

        self.params_gui = params_gui
        self.output_gui = output_gui

        self.node_id = ed.NodeId.create()
        self.pin_input = ed.PinId.create()
        self.pin_output = ed.PinId.create()
        self.link_id = ed.LinkId.create()

    def _draw_exception_message(self) -> None:
        # return
        last_exception_message = self._function.last_exception_message
        if last_exception_message is None:
            return
        fl_widgets.text("Exception:\n" + last_exception_message, max_line_width=30, color=config.colors.error)

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

        imgui.text(self._function.name())
        self._draw_exception_message()

        params_changed, new_params = self.params_gui(self._function.get_params().get_value())
        if params_changed:
            self._function.set_params_value(new_params)

        draw_input_pin = True  # idx != 0
        if draw_input_pin:
            ed.begin_pin(self.pin_input, ed.PinKind.input)
            imgui.text(icons_fontawesome.ICON_FA_CIRCLE)
            ed.end_pin()

        def draw_output() -> None:
            with imgui_ctx.push_id("output"):
                if self._function.get_output().is_unset():
                    imgui.text("Unset!")
                if self._function.get_output().is_none():
                    imgui.text("None")
                else:
                    imgui.begin_group()
                    self.output_gui(self._function.get_output().get_value())
                    imgui.end_group()
                imgui.same_line()
                ed.begin_pin(self.pin_output, ed.PinKind.output)
                imgui.text(icons_fontawesome.ICON_FA_CIRCLE)
                ed.end_pin()

        draw_output()

        ed.end_node()

    def draw_link(self) -> None:
        if self._next_function_node is None:
            return
        ed.link(self.link_id, self.pin_output, self._next_function_node.pin_input)

    # def set_input(self, input_data: Any) -> None:
    #     self.input_data_with_gui.set(input_data)
    #     self._invoke_function()


def sandbox() -> None:
    from typing import Tuple
    from imgui_bundle import immapp

    def f(a: int) -> int:
        return a + 3

    observable_f = ObservableFunction(f)

    def edit_data_gui(x: int | None) -> Tuple[bool, int]:
        if x is None:
            x = 0
        changed, new_value = imgui.slider_int("Value", x, -10, 10)
        return changed, new_value

    def present_data_gui(x: int) -> None:
        imgui.text(str(x))

    function_node = FunctionNode2(observable_f, edit_data_gui, present_data_gui)

    def gui() -> None:
        ed.begin("Function Graph")
        function_node.draw_node()
        ed.end()

    # addons = immapp.AddOnsParams()
    # addons.with_node_editor = True
    immapp.run(gui, with_node_editor=True)


if __name__ == "__main__":
    sandbox()
