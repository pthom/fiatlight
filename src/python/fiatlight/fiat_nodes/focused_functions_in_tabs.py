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
        hello_imgui.add_dockable_window(self._make_dockable_window(fn))

    def _remove_focused_function(self, fn: FunctionNodeGui) -> None:
        hello_imgui.remove_dockable_window(self._dockable_window_label(fn))

    def _has_focused_function(self, fn: FunctionNodeGui) -> bool:
        dockable_windows = hello_imgui.get_runner_params().docking_params.dockable_windows
        dockable_windows_labels = [dw.label for dw in dockable_windows]
        new_window_label = self._dockable_window_label(fn)
        return new_window_label in dockable_windows_labels

    def _draw_focus_on_function_btn(self, fn: FunctionNodeGui) -> None:
        is_new_focus = not self._has_focused_function(fn)
        with fontawesome_6_ctx():
            clicked = imgui.button(icons_fontawesome_6.ICON_FA_WINDOW_RESTORE, ImVec2(0, 0))
            if is_new_focus:
                fiat_osd.set_widget_tooltip("Focus on function in new tab")
            else:
                fiat_osd.set_widget_tooltip("Un-focus function")

            if clicked:
                if is_new_focus:
                    self._add_focused_function(fn)
                else:
                    self._remove_focused_function(fn)

    def _function_unique_name(self, fn: FunctionNodeGui) -> str:
        from fiatlight.fiat_nodes.functions_graph_gui import KK_STATIC_FunctionsGraphGui

        assert KK_STATIC_FunctionsGraphGui is not None
        unique_name = KK_STATIC_FunctionsGraphGui.function_node_unique_name(fn)
        return unique_name

    def _dockable_window_label(self, fn: FunctionNodeGui) -> str:
        return self._function_unique_name(fn) + "##FocusedFunctionsInTabs_" + str(id(fn))

    def _make_dockable_window(self, fn: FunctionNodeGui) -> hello_imgui.DockableWindow:
        unique_name = self._function_unique_name(fn)

        def _wrap_gui_store_change() -> None:
            if self.last_frame_idx != imgui.get_frame_count():
                self.did_any_function_return_true_this_frame = False
                self.last_frame_idx = imgui.get_frame_count()
            changed = fn.draw_node(unique_name)
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
