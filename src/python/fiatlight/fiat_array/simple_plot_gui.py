"""SimplePlotGui is a version of AnyDataWithGui that is specialized to plot 1D arrays.

Internally, it uses ImPlot (https://github.com/epezent/implot)
"""

from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui
from fiatlight.fiat_types.base_types import JsonDict
from fiatlight.fiat_array.array_types import FloatMatrix_Dim1, present_array
from dataclasses import dataclass
from enum import Enum, auto
from typing import Tuple, List
from imgui_bundle import implot, ImVec2, hello_imgui, imgui_ctx, imgui


class SimplePlotType(Enum):
    """Plot types supported to present 1D arrays with ImPlot.
    Note: ImPlot provides many other plot types
    """

    # line: A 2D line plot for displaying continuous data
    line = auto()  #
    # scatter: A scatter plot for displaying individual data points (for small arrays)
    scatter = auto()
    # stairs: A stairstep graph, useful for non-continuous data (for small arrays)
    stairs = auto()
    # bars: A bar chart for categorical data (for small arrays)
    bars = auto()

    @staticmethod
    def from_str(name: str) -> "SimplePlotType":
        if name not in SimplePlotType.__members__:
            raise ValueError(f"Invalid plot type: {name}")
        return SimplePlotType[name]


@dataclass
class SimplePlotParams:
    _plot_type_str: str = "line"  # The type of presentation to use (a string from SimplePlotType)
    # Size in em units (i.e. multiples of the font height)
    plot_size_em: Tuple[float, float] = (35, 20)
    # The threshold for the array size to be able to present scatter, bars, and stairs plots
    small_array_threshold: int = 100

    def plot_size_pixels(self) -> ImVec2:
        return hello_imgui.em_to_vec2(self.plot_size_em[0], self.plot_size_em[1])

    def as_dict(self) -> JsonDict:
        from dataclasses import asdict

        r = asdict(self)
        return r

    def presentation_type(self) -> SimplePlotType:
        return SimplePlotType.from_str(self._plot_type_str)

    def fill_from_dict(self, data: JsonDict) -> None:
        self.__dict__.update(data)


class SimplePlotPresenter:
    plot_params: SimplePlotParams
    array: FloatMatrix_Dim1 | None = None

    def __init__(self, array_params: SimplePlotParams | None = None) -> None:
        self.plot_params = SimplePlotParams() if array_params is None else array_params

    def set_array(self, array: FloatMatrix_Dim1) -> None:
        assert len(array.shape) == 1 or len(array.shape) == 2
        if len(array.shape) == 2:
            # We support only (x, y) arrays (in columns or rows)
            assert array.shape[1] == 2 or array.shape[0] == 2
        self.array = array

    def _available_plot_types(self) -> List["SimplePlotType"]:
        assert self.array is not None
        if len(self.array.shape) != 1:
            raise ValueError("Only 1D arrays are supported")

        r = [SimplePlotType.line]

        nb_items = self.array.shape[0]
        if nb_items < self.plot_params.small_array_threshold:
            r.append(SimplePlotType.scatter)
            r.append(SimplePlotType.stairs)
            r.append(SimplePlotType.bars)

        return r

    def _gui_select_plot_type(self) -> None:
        available_plot_types = self._available_plot_types()
        if len(available_plot_types) > 1:
            with imgui_ctx.begin_horizontal("Plot Type"):
                for plot_type in available_plot_types:
                    is_selected = self.plot_params.presentation_type() == plot_type
                    if imgui.radio_button(plot_type.name, is_selected):
                        self.plot_params._plot_type_str = plot_type.name
        else:
            self.plot_params._plot_type_str = available_plot_types[0].name

    def gui(self) -> None:
        if self.array is None:
            return
        self._gui_select_plot_type()

        if not implot.begin_plot(
            "##Plot" + str(self.plot_params.presentation_type()), self.plot_params.plot_size_pixels()
        ):
            return

        label = "plot"
        if self.plot_params.presentation_type() == SimplePlotType.line:
            implot.plot_line(label, self.array)
        elif self.plot_params.presentation_type() == SimplePlotType.scatter:
            implot.plot_scatter(label, self.array)
        elif self.plot_params.presentation_type() == SimplePlotType.stairs:
            implot.plot_stairs(label, self.array)
        elif self.plot_params.presentation_type() == SimplePlotType.bars:
            implot.plot_bars(label, self.array)

        implot.end_plot()


class SimplePlotGui(AnyDataWithGui[FloatMatrix_Dim1]):
    """A GUI for presenting 1D arrays with ImPlot."""

    plot_presenter: SimplePlotPresenter

    def __init__(self, array_params: SimplePlotParams | None = None) -> None:
        super().__init__()
        self.plot_presenter = SimplePlotPresenter(array_params)

        self.callbacks.present_custom = self.present_custom
        self.callbacks.present_custom_popup_possible = True

        self.callbacks.on_change = self.on_change
        self.callbacks.present_str = present_array

        self.callbacks.save_gui_options_to_json = self.save_gui_options_to_json
        self.callbacks.load_gui_options_from_json = self.load_gui_options_from_json

    def present_custom(self) -> None:
        self.plot_presenter.gui()

    def on_change(self) -> None:
        self.plot_presenter.set_array(self.get_actual_value())

    def save_gui_options_to_json(self) -> JsonDict:
        return self.plot_presenter.plot_params.as_dict()

    def load_gui_options_from_json(self, data: JsonDict) -> None:
        self.plot_presenter.plot_params.fill_from_dict(data)


def register_simple_plot_factory() -> None:
    """Will associate FloatMatrix_Dim1 with SimplePlotGui in the GUI factories."""
    from fiatlight.fiat_core import gui_factories

    gui_factories().register_factory("fiatlight.fiat_array.array_types.FloatMatrix_Dim1", SimplePlotGui)
