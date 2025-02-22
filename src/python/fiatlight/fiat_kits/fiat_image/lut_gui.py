from typing import Tuple, Optional, TypeAlias
import math
from fiatlight.fiat_core import AnyDataWithGui
from fiatlight.fiat_kits.fiat_image import ImageU8
from fiatlight.fiat_kits.fiat_image.lut_types import LutParams, LutTable
from fiatlight.fiat_utils.cache_per_imgui_view import CachePerImGuiView
from imgui_bundle import immapp, imgui, immvision


Point2d: TypeAlias = Tuple[float, float]


class LutParamsWithGui(AnyDataWithGui[LutParams]):
    """A GUI for LutParams, allowing to visually edit a curve representing Look-Up Table transformation."""

    _lut_graph: ImageU8
    _lut_graph_needs_refresh: CachePerImGuiView[bool] = CachePerImGuiView("lut_graph_needs_refresh", True)
    _lut_graph_size_em: float = 3.5

    def __init__(self) -> None:
        super().__init__(LutParams)
        self.callbacks.present_str = self.present_str
        self.callbacks.edit = self.edit
        self.callbacks.on_change = self.on_change
        self.callbacks.default_value_provider = lambda: LutParams()

    @staticmethod
    def present_str(lut_params: LutParams) -> str:
        if lut_params.is_default():
            return "Lut(default)"
        return "Lut(...)"

    def edit(self, _value: LutParams) -> tuple[bool, LutParams]:
        # _value is not used, as the value is accessed via self.lut_params() which accesses self.value
        # (note self.value is of type LutParams | Unspecified | Error)
        changed = self.gui_params()
        assert isinstance(self.value, LutParams)
        return changed, self.value

    def on_change(self, _lut_params: LutParams) -> None:
        self._lut_graph_needs_refresh.set_for_all_views(True)

    def lut_params(self) -> LutParams:
        assert isinstance(self.value, LutParams)
        return self.value

    def _lut_graph_size(self) -> int:
        return int(immapp.em_size(self._lut_graph_size_em))

    def _show_lut_graph(self) -> Point2d:
        lut_graph_needs_refresh = self._lut_graph_needs_refresh.get_for_current_view()
        if lut_graph_needs_refresh:
            self._prepare_lut_graph()
            self._lut_graph_needs_refresh.set_for_current_view(False)
        mouse_position = immvision.image_display("##lut", self._lut_graph, refresh_image=lut_graph_needs_refresh)
        return mouse_position

    def lut_table(self) -> LutTable:
        return self.lut_params().to_table()

    def _prepare_lut_graph(self) -> None:
        from fiatlight.fiat_kits.fiat_image.lut_functions import lut_table_graph

        lut_table = self.lut_table()
        self._lut_graph = lut_table_graph(lut_table, self._lut_graph_size())

    def handle_graph_mouse_edit(self, mouse_position: Point2d) -> bool:
        drag_threshold = 0
        mouse_button = 0
        changed = False

        def get_mouse_position_normalized() -> Optional[Point2d]:
            r: Optional[Point2d]
            graph_size = self._lut_graph_size()
            if mouse_position[0] >= 0:
                r = (mouse_position[0] / graph_size, 1 - mouse_position[1] / graph_size)
                return r
            else:
                return None

        mouse_position_normalized = get_mouse_position_normalized()

        if mouse_position_normalized is not None:
            imgui.text(f"{mouse_position_normalized[0]:.2f}, {mouse_position_normalized[1]:.2f}")

        if mouse_position_normalized is not None and imgui.is_mouse_dragging(0, drag_threshold):
            drag_delta = imgui.get_mouse_drag_delta(mouse_button)
            drag_horizontal = math.fabs(drag_delta.x) > math.fabs(drag_delta.y)
            drag_vertical = not drag_horizontal
            imgui.reset_mouse_drag_delta(mouse_button)

            delta_edge = 0.37
            if drag_horizontal and mouse_position_normalized[1] < delta_edge:
                self.lut_params().min_in = mouse_position_normalized[0]
                changed = True
            elif drag_horizontal and mouse_position_normalized[1] > 1.0 - delta_edge:
                self.lut_params().max_in = mouse_position_normalized[0]
                changed = True
            elif drag_vertical and mouse_position_normalized[0] < delta_edge:
                self.lut_params().min_out = mouse_position_normalized[1]
                changed = True
            elif drag_vertical and mouse_position_normalized[0] > 1.0 - delta_edge:
                self.lut_params().max_out = mouse_position_normalized[1]
                changed = True

        return changed

    def gui_params(self) -> bool:
        changed = False

        imgui.begin_group()
        mouse_position = self._show_lut_graph()
        if self.handle_graph_mouse_edit(mouse_position):
            changed = True

        if imgui.small_button("Reset"):
            self.lut_params().min_in, self.lut_params().max_in = (0.0, 1.0)
            self.lut_params().min_out, self.lut_params().max_out = (0.0, 1.0)
            self.lut_params().pow_exponent = 1.0
            changed = True
        imgui.end_group()

        imgui.same_line()

        imgui.begin_group()
        idx_slider = 0

        def show_slider(label: str, v: float, min_value: float, max_value: float, logarithmic: bool) -> float:
            nonlocal idx_slider, changed
            imgui.set_next_item_width(70)
            idx_slider += 1
            flags = imgui.SliderFlags_.logarithmic.value if logarithmic else 0
            edited_this_slider, v = imgui.slider_float(
                f"{label}##slider{idx_slider}", v, min_value, max_value, flags=flags
            )
            if edited_this_slider:
                changed = True
            return v

        def show_01_slider(label: str, v: float) -> float:
            return show_slider(label, v, 0, 1, False)

        def show_two_01_sliders(label: str, v_min: float, v_max: float) -> Tuple[float, float]:
            v_min = show_01_slider(f"##{label}v_min", v_min)
            imgui.same_line()
            v_max = show_01_slider(f"{label}##v_max", v_max)
            if math.fabs(v_max - v_min) < 1e-3:  # avoid div by 0
                v_min = v_max - 0.01
            return v_min, v_max

        self.lut_params().pow_exponent = show_slider("Gamma power", self.lut_params().pow_exponent, 0.0, 10.0, True)
        self.lut_params().min_in, self.lut_params().max_in = show_two_01_sliders(
            "In", self.lut_params().min_in, self.lut_params().max_in
        )
        self.lut_params().min_out, self.lut_params().max_out = show_two_01_sliders(
            "Out", self.lut_params().min_out, self.lut_params().max_out
        )

        if changed:
            self._lut_graph_needs_refresh.set_for_all_views(True)
        imgui.end_group()
        return changed
