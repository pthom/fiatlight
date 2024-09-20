from fiatlight.fiat_nodes.function_node_gui import FunctionNodeGui
from imgui_bundle import hello_imgui, imgui, ImVec2
from fiatlight.fiat_widgets import fontawesome_6_ctx, icons_fontawesome_6, fiat_osd


class FocusedFunctionsInTabs:
    did_any_function_return_true_this_frame: bool = False
    last_frame_idx: int = -1

    def __init__(self) -> None:
        pass

    def draw_focus_on_function_btn(self, fn: FunctionNodeGui) -> None:
        self._draw_focus_on_function_btn(fn)

    def did_any_change_happen(self) -> bool:
        return self.did_any_function_return_true_this_frame

    def _add_focused_function(self, fn: FunctionNodeGui) -> None:
        if self._has_opened_dockable_window(fn):
            return
        maybe_previous_dockable_window = self._get_dockable_window(fn)
        if maybe_previous_dockable_window is not None:
            maybe_previous_dockable_window.is_visible = True
        else:
            hello_imgui.add_dockable_window(self._make_dockable_window(fn))

    def _highlight_dockable_window(self, fn: FunctionNodeGui) -> None:
        dockable_window = self._get_dockable_window(fn)
        assert dockable_window is not None
        hello_imgui.get_runner_params().docking_params.focus_dockable_window(dockable_window.label)

    # def _remove_focused_function(self, fn: FunctionNodeGui) -> None:
    #     maybe_previous_dockable_window = self._get_dockable_window(fn)
    #     assert maybe_previous_dockable_window is not None
    #     maybe_previous_dockable_window.is_visible = False

    def _get_dockable_window(self, fn: FunctionNodeGui) -> hello_imgui.DockableWindow | None:
        dockable_windows = hello_imgui.get_runner_params().docking_params.dockable_windows
        result = None
        for dockable_window in dockable_windows:
            if dockable_window.label == self._dockable_window_label(fn):
                result = dockable_window
                break
        return result

    def _has_opened_dockable_window(self, fn: FunctionNodeGui) -> bool:
        dockable_window = self._get_dockable_window(fn)
        return dockable_window is not None and dockable_window.is_visible

    def _draw_focus_on_function_btn(self, fn: FunctionNodeGui) -> None:
        has_opened_dockable_window = not self._has_opened_dockable_window(fn)
        with fontawesome_6_ctx():
            clicked = imgui.button(icons_fontawesome_6.ICON_FA_UP_RIGHT_FROM_SQUARE, ImVec2(0, 0))
            fiat_osd.set_widget_tooltip("Focus on function in new tab")

            if clicked:
                if has_opened_dockable_window:
                    self._add_focused_function(fn)
                else:
                    self._highlight_dockable_window(fn)

    def _dockable_window_label(self, fn: FunctionNodeGui) -> str:
        function_name = fn.get_function_node().function_with_gui.function_name
        return function_name + "##FocusedFunctionsInTabs_" + str(id(fn))

    def _make_dockable_window(self, fn: FunctionNodeGui) -> hello_imgui.DockableWindow:
        def _wrap_gui_store_change() -> None:
            if self.last_frame_idx != imgui.get_frame_count():
                self.did_any_function_return_true_this_frame = False
                self.last_frame_idx = imgui.get_frame_count()
            changed = fn.draw_node()
            if changed:
                self.did_any_function_return_true_this_frame = True

        dockable_window = hello_imgui.DockableWindow()
        dockable_window.dock_space_name = "MainDockSpace"
        dockable_window.gui_function = _wrap_gui_store_change
        dockable_window.label = self._dockable_window_label(fn)
        dockable_window.is_visible = True
        dockable_window.include_in_view_menu = True
        return dockable_window


FOCUSED_FUNCTIONS_IN_TABS = FocusedFunctionsInTabs()
