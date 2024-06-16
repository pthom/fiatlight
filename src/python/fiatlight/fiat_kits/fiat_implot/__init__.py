from fiatlight.fiat_kits.fiat_implot.array_types import (
    FloatMatrix_Dim1,
    FloatMatrix_Dim2,
    FloatMatrix_Dim3,
    FloatMatrix_Dim4,
    IntMatrix_Dim1,
    IntMatrix_Dim2,
    IntMatrix_Dim3,
    IntMatrix_Dim4,
)
from fiatlight.fiat_kits.fiat_implot.simple_plot_gui import (
    present_float1_arrays_as_plot,
    present_float2_arrays_as_plot,
    SimplePlotGui,
)

present_float1_arrays_as_plot()
present_float2_arrays_as_plot()

__all__ = [
    # from array_types
    "FloatMatrix_Dim1",
    "FloatMatrix_Dim2",
    "FloatMatrix_Dim3",
    "FloatMatrix_Dim4",
    "IntMatrix_Dim1",
    "IntMatrix_Dim2",
    "IntMatrix_Dim3",
    "IntMatrix_Dim4",
    # from simple_plot_gui
    # "present_float1_arrays_as_plot",
    # "present_float2_arrays_as_plot",
    "SimplePlotGui",
]
