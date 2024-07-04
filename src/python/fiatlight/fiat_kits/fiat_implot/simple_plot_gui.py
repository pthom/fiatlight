"""SimplePlotGui is a version of AnyDataWithGui that is specialized to plot 1D/2D arrays.

Internally, it uses ImPlot (https://github.com/epezent/implot)
"""

from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui
from fiatlight.fiat_core import PossibleFiatAttributes
from fiatlight.fiat_types.base_types import JsonDict, FiatAttributes
from fiatlight.fiat_kits.fiat_implot.array_types import (
    FloatMatrix_Dim1,
    FloatMatrix_Dim2,
    present_array,
    FloatMatrix,
)
from enum import Enum
from typing import List
from imgui_bundle import implot, ImVec2, imgui_ctx, imgui, immapp, ImVec2_Pydantic
from pydantic import BaseModel


FloatMatrix_Dim1_Or_2 = FloatMatrix_Dim1 | FloatMatrix_Dim2


class SimplePlotType(Enum):
    """Plot types supported to present 1D arrays with ImPlot.
    Note: ImPlot provides many other plot types
    """

    # line: A 2D line plot for displaying continuous data
    line = "line"
    # scatter: A scatter plot for displaying individual data points (for small arrays)
    scatter = "scatter"
    # stairs: A stairstep graph, useful for non-continuous data (for small arrays)
    stairs = "stairs"
    # bars: A bar chart for categorical data (for small arrays)
    bars = "bars"

    @staticmethod
    def from_str(name: str) -> "SimplePlotType":
        if name not in SimplePlotType.__members__:
            raise ValueError(f"Invalid plot type: {name}")
        return SimplePlotType[name]


class SimplePlotParams(BaseModel):
    plot_type: SimplePlotType = SimplePlotType.line  # The type of presentation to use
    # Size in em units (i.e. multiples of the font height)
    plot_size_em: ImVec2_Pydantic = ImVec2(35, 20)
    # The threshold for the array size to be able to present scatter, bars, and stairs plots
    small_array_threshold: int = 100
    # Auto-scale the plot axes
    auto_fit: bool = True


class SimplePlotPossibleFiatAttributes(PossibleFiatAttributes):
    def __init__(self) -> None:
        super().__init__("SimplePlotGui")

        self.add_explained_attribute(
            name="plot_type",
            explanation="The type of presentation to use. Choose from line, scatter, stairs, or bars.",
            type_=str,
            default_value="line",
        )
        self.add_explained_attribute(
            name="plot_size_em",
            explanation="Size in em units (i.e. multiples of the font height)",
            type_=tuple,
            default_value=(35.0, 20.0),
            tuple_types=(float, float),
        )
        self.add_explained_attribute(
            name="auto_fit",
            explanation="Auto-scale the plot axes",
            type_=bool,
            default_value=True,
        )
        self.add_explained_attribute(
            name="small_array_threshold",
            explanation="The threshold for the array size to be able to present scatter, bars, and stairs plots",
            type_=int,
            default_value=100,
        )


_SIMPLE_PLOT_POSSIBLE_FIAT_ATTRIBUTES = SimplePlotPossibleFiatAttributes()


class SimplePlotPresenter:
    plot_params: SimplePlotParams
    array: FloatMatrix_Dim1_Or_2 | None = None

    def __init__(self, array_params: SimplePlotParams | None = None) -> None:
        self.plot_params = SimplePlotParams() if array_params is None else array_params

    def set_array(self, array: FloatMatrix_Dim1_Or_2) -> None:
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
        assert self.array is not None
        return len(self.array.shape) == 2

    def _array_x(self) -> FloatMatrix_Dim1:
        assert self.array is not None
        if self._is_2d_array():
            return self.array[:, 0]  # type: ignore
        return self.array  # type: ignore

    def _array_y(self) -> FloatMatrix_Dim1:
        assert self.array is not None
        if self._is_2d_array():
            return self.array[:, 1]  # type: ignore
        return self.array  # type: ignore

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

    def on_fiat_attributes_changed(self, attributes: FiatAttributes) -> None:
        if "plot_type" in attributes:
            self.plot_params.plot_type = SimplePlotType.from_str(attributes["plot_type"])
        if "plot_size_em" in attributes:
            self.plot_params.plot_size_em = ImVec2(*attributes["plot_size_em"])
        if "auto_fit" in attributes:
            self.plot_params.auto_fit = attributes["auto_fit"]
        if "small_array_threshold" in attributes:
            self.plot_params.small_array_threshold = attributes["small_array_threshold"]

    def _gui_select_plot_type(self) -> None:
        available_plot_types = self._available_plot_types()
        if len(available_plot_types) > 1:
            with imgui_ctx.begin_horizontal("Plot Type"):
                for plot_type in available_plot_types:
                    is_selected = self.plot_params.plot_type == plot_type
                    if imgui.radio_button(plot_type.name, is_selected):
                        self.plot_params.plot_type = plot_type
        else:
            self.plot_params.plot_type = available_plot_types[0]

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
                if self.plot_params.plot_type == SimplePlotType.line:
                    implot.plot_line(label, self.array)  # type: ignore
                elif self.plot_params.plot_type == SimplePlotType.scatter:
                    implot.plot_scatter(label, self.array)  # type: ignore
                elif self.plot_params.plot_type == SimplePlotType.stairs:
                    implot.plot_stairs(label, self.array)  # type: ignore
                elif self.plot_params.plot_type == SimplePlotType.bars:
                    implot.plot_bars(label, self.array)  # type: ignore
            else:
                if self.plot_params.plot_type == SimplePlotType.line:
                    implot.plot_line(label, self._array_x(), self._array_y())
                elif self.plot_params.plot_type == SimplePlotType.scatter:
                    implot.plot_scatter(label, self._array_x(), self._array_y())
                elif self.plot_params.plot_type == SimplePlotType.stairs:
                    implot.plot_stairs(label, self._array_x(), self._array_y())

        self.plot_params.plot_size_em = immapp.show_resizable_plot_in_node_editor_em(
            "Plot", self.plot_params.plot_size_em, plot_function
        )


class SimplePlotGui(AnyDataWithGui[FloatMatrix_Dim1_Or_2]):
    """A GUI for presenting 1D or 2D arrays with ImPlot. Can present the array as a line, scatter (+ stairs, or bars plot, if the array is small enough)"""

    plot_presenter: SimplePlotPresenter

    def __init__(self, array_params: SimplePlotParams | None = None) -> None:
        super().__init__(FloatMatrix)  # type: ignore
        self.plot_presenter = SimplePlotPresenter(array_params)

        self.callbacks.present = self.present
        self.callbacks.present_collapsible = True

        self.callbacks.on_change = self.on_change
        self.callbacks.present_str = present_array

        self.callbacks.save_gui_options_to_json = self.save_gui_options_to_json
        self.callbacks.load_gui_options_from_json = self.load_gui_options_from_json

        # fiat attributes
        self.callbacks.on_fiat_attributes_changed = self.on_fiat_attributes_changes

    def on_fiat_attributes_changes(self, attributes: FiatAttributes) -> None:
        self.plot_presenter.on_fiat_attributes_changed(attributes)

    def present(self, _value: FloatMatrix_Dim1_Or_2) -> None:
        # _value is not used, as the array is set with on_change
        self.plot_presenter.gui()

    def on_change(self, value: FloatMatrix_Dim1_Or_2) -> None:
        self.plot_presenter.set_array(value)

    def save_gui_options_to_json(self) -> JsonDict:
        return self.plot_presenter.plot_params.model_dump(mode="json")

    def load_gui_options_from_json(self, data: JsonDict) -> None:
        self.plot_presenter.plot_params = SimplePlotParams.model_validate(data)

    @staticmethod
    def possible_fiat_attributes() -> PossibleFiatAttributes | None:
        # This is a method which we inherit from AnyDataWithGui.
        return _SIMPLE_PLOT_POSSIBLE_FIAT_ATTRIBUTES


def present_float1_arrays_as_plot() -> None:
    """Will cause FloatMatrix_Dim1 to be presented as a line plot of a 1D array in the GUI.
    This uses SimplePlotGui and ImPlot. If the array is small, scatter, stairs, and bars plots are also available
    """
    from fiatlight.fiat_togui.gui_registry import register_typing_new_type

    register_typing_new_type(FloatMatrix_Dim1, SimplePlotGui)


def present_float2_arrays_as_plot() -> None:
    """Will cause FloatMatrix_Dim2 to be presented as a line plot of a 2D array in the GUI.
    This uses SimplePlotGui and ImPlot. If the array is small, scatter and stairs plots are also available
    """
    from fiatlight.fiat_togui.gui_registry import register_typing_new_type

    register_typing_new_type(FloatMatrix_Dim2, SimplePlotGui)
