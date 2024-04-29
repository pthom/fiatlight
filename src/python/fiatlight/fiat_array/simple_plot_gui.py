"""SimplePlotGui is a version of AnyDataWithGui that is specialized to plot 1D arrays.

Internally, it uses ImPlot (https://github.com/epezent/implot)
"""

from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui
from fiatlight.fiat_types.base_types import JsonDict
from fiatlight.fiat_array.array_types import FloatMatrix_Dim1, FloatMatrix_Dim2, present_array
from dataclasses import dataclass
from enum import Enum, auto
from typing import List
from imgui_bundle import implot, ImVec2, imgui_ctx, imgui, immapp


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
    plot_size_em: ImVec2 = ImVec2(35, 20)
    # The threshold for the array size to be able to present scatter, bars, and stairs plots
    small_array_threshold: int = 100
    # Auto-scale the plot axes
    auto_fit: bool = True

    def as_dict(self) -> JsonDict:
        r = {
            "_plot_type_str": self._plot_type_str,
            "plot_size_em": (self.plot_size_em.x, self.plot_size_em.y),
            "small_array_threshold": self.small_array_threshold,
            "auto_fit": self.auto_fit,
        }
        return r

    def fill_from_dict(self, data: JsonDict) -> None:
        self._plot_type_str = data["_plot_type_str"]
        self.plot_size_em = ImVec2(*data["plot_size_em"])
        self.small_array_threshold = data["small_array_threshold"]
        self.auto_fit = data["auto_fit"]

    def presentation_type(self) -> SimplePlotType:
        return SimplePlotType.from_str(self._plot_type_str)


class SimplePlotPresenter:
    plot_params: SimplePlotParams
    array: FloatMatrix_Dim1 | FloatMatrix_Dim2 | None = None

    def __init__(self, array_params: SimplePlotParams | None = None) -> None:
        self.plot_params = SimplePlotParams() if array_params is None else array_params

    def set_array(self, array: FloatMatrix_Dim1 | FloatMatrix_Dim2) -> None:
        if len(array.shape) == 1:
            self.array = array
            return
        elif len(array.shape) == 2:
            # We only support 2D arrays, with (x, y) as rows or columns
            if array.shape[0] == 2:
                self.array = array.T
                return
            elif array.shape[1] == 2:
                self.array = array
                return
        raise ValueError("Only 1D arrays or 2D arrays with 2 columns or 2 rows are supported")

    def _is_2d_array(self) -> bool:
        return len(self.array.shape) == 2

    def _array_x(self) -> FloatMatrix_Dim1:
        assert self.array is not None
        if self._is_2d_array():
            return self.array[:, 0]
        return self.array

    def _array_y(self) -> FloatMatrix_Dim1:
        assert self.array is not None
        if self._is_2d_array():
            return self.array[:, 1]
        return self.array

    def _available_plot_types(self) -> List["SimplePlotType"]:
        assert self.array is not None
        r = [SimplePlotType.line]
        nb_items = self.array.shape[0]
        if nb_items < self.plot_params.small_array_threshold:
            r.append(SimplePlotType.scatter)
            r.append(SimplePlotType.stairs)
            if not self._is_2d_array():
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
        _, self.plot_params.auto_fit = imgui.checkbox("Auto Fit", self.plot_params.auto_fit)

        def plot_function() -> None:
            axis_flags = implot.AxisFlags_.auto_fit.value if self.plot_params.auto_fit else 0
            implot.setup_axes("x", "y", axis_flags, axis_flags)
            label = "##plot"
            if not self._is_2d_array():
                if self.plot_params.presentation_type() == SimplePlotType.line:
                    implot.plot_line(label, self.array)  # type: ignore
                elif self.plot_params.presentation_type() == SimplePlotType.scatter:
                    implot.plot_scatter(label, self.array)  # type: ignore
                elif self.plot_params.presentation_type() == SimplePlotType.stairs:
                    implot.plot_stairs(label, self.array)  # type: ignore
                elif self.plot_params.presentation_type() == SimplePlotType.bars:
                    implot.plot_bars(label, self.array)  # type: ignore
            else:
                if self.plot_params.presentation_type() == SimplePlotType.line:
                    implot.plot_line(label, self._array_x(), self._array_y())  # type: ignore
                elif self.plot_params.presentation_type() == SimplePlotType.scatter:
                    implot.plot_scatter(label, self._array_x(), self._array_y())
                elif self.plot_params.presentation_type() == SimplePlotType.stairs:
                    implot.plot_stairs(label, self._array_x(), self._array_y())

        self.plot_params.plot_size_em = immapp.show_resizable_plot_in_node_editor_em(
            "Plot", self.plot_params.plot_size_em, plot_function
        )


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


def present_float1_arrays_as_plot() -> None:
    """Will cause FloatMatrix_Dim1 to be presented as a line plot of a 1D array in the GUI.
    This uses SimplePlotGui and ImPlot. If the array is small, scatter, stairs, and bars plots are also available
    """
    from fiatlight.fiat_core import gui_factories

    gui_factories().register_factory("fiatlight.fiat_array.array_types.FloatMatrix_Dim1", SimplePlotGui)


def present_float2_arrays_as_plot() -> None:
    """Will cause FloatMatrix_Dim2 to be presented as a line plot of a 2D array in the GUI.
    This uses SimplePlotGui and ImPlot. If the array is small, scatter and stairs plots are also available
    """
    from fiatlight.fiat_core import gui_factories

    gui_factories().register_factory("fiatlight.fiat_array.array_types.FloatMatrix_Dim2", SimplePlotGui)
