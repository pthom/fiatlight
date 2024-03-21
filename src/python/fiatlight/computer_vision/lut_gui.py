from typing import Tuple, Optional, TypeAlias
import math
from fiatlight import AnyDataWithGui
from fiatlight.computer_vision import ImageUInt8
from fiatlight.computer_vision.lut import LutParams, LutTable
from imgui_bundle import immapp, imgui, immvision


Point2d: TypeAlias = Tuple[float, float]


class LutParamsWithGui(AnyDataWithGui[LutParams]):
    _lut_graph: ImageUInt8
    _lut_graph_needs_refresh: bool = True
    _lut_graph_size_em: float = 3.5

    def __init__(self) -> None:
        super().__init__()
        self.callbacks.present_str = self.present_str
        self.callbacks.edit = self.edit
        self.callbacks.on_change = self.on_change
        self.callbacks.default_value_provider = lambda: LutParams()

    @staticmethod
    def present_str(lut_params: LutParams) -> str:
        if lut_params.is_default():
            return "Lut(default)"
        return "Lut(...)"

    def edit(self) -> bool:
        changed = self.gui_params()
        return changed

    def on_change(self) -> None:
        self._lut_graph_needs_refresh = True

    def lut_params(self) -> LutParams:
        assert isinstance(self.value, LutParams)
        return self.value

    def _lut_graph_size(self) -> int:
        return int(immapp.em_size(self._lut_graph_size_em))

    def _show_lut_graph(self) -> Point2d:
        refresh_image = self._lut_graph_needs_refresh
        if refresh_image:
            self._prepare_lut_graph()
        mouse_position = immvision.image_display("##lut", self._lut_graph, refresh_image=refresh_image)
        return mouse_position

    def lut_table(self) -> LutTable:
        return self.lut_params().to_table()

    def _prepare_lut_graph(self) -> None:
        from fiatlight.computer_vision.lut import lut_table_graph

        lut_table = self.lut_table()
        self._lut_graph = lut_table_graph(lut_table, self._lut_graph_size())
        self._lut_graph_needs_refresh = False

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

        def show_slider(label: str, v: float, min: float, max: float, logarithmic: bool) -> float:
            nonlocal idx_slider, changed
            imgui.set_next_item_width(70)
            idx_slider += 1
            flags = imgui.SliderFlags_.logarithmic.value if logarithmic else 0
            edited_this_slider, v = imgui.slider_float(f"{label}##slider{idx_slider}", v, min, max, flags=flags)
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
            self._lut_graph_needs_refresh = True
        imgui.end_group()
        return changed


#
#
# class LutChannelsWithGui(FunctionWithGui[Image, Image]):
#     color_type: ColorType = ColorType.BGR
#     channel_adjust_params: List[LutImage]
#
#     def __init__(self) -> None:
#         self.input_gui = ImageChannelsWithGui()
#         self.output_gui = ImageChannelsWithGui()
#         self.name = "LUT channels"
#
#         def f(x: Any) -> Any:
#             assert type(x) == np.ndarray
#
#             original_channels = x
#             self.add_params_on_demand(len(original_channels))
#
#             adjusted_channels = np.zeros_like(original_channels)
#             for i in range(len(original_channels)):
#                 adjusted_channels[i] = self.channel_adjust_params[i].apply(original_channels[i])
#
#             return adjusted_channels
#         self.f_impl = f
#
#     def output_gui_channels(self) -> ImageChannelsWithGui:
#         return cast(ImageChannelsWithGui, self.output_gui)
#
#     def add_params_on_demand(self, nb_channels: int) -> None:
#         if not hasattr(self, "channel_adjust_params"):
#             self.channel_adjust_params = []
#         while len(self.channel_adjust_params) < nb_channels:
#             self.channel_adjust_params.append(LutImage())
#
#     # def old_gui_params(self) -> bool:
#     #     changed = False
#     #     for i, channel_adjust_param in enumerate(self.channel_adjust_params):
#     #         channel_name = self.color_type.channels_names()[i]
#     #         imgui.push_id(str(i))
#     #         changed |= channel_adjust_param.old_gui_params(channel_name)
#     #         imgui.pop_id()
#     #     return changed
#
