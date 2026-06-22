"""The palette popup keeps the user's filter across reopenings; only the
per-open type filters (set by drag-from-pin) are reset."""
from imgui_bundle import ImVec2

from fiatlight.fiat_core import FunctionsGraph
from fiatlight.fiat_nodes.functions_graph_gui import FunctionsGraphGui
from fiatlight.fiat_palette.palette import PinKind
from fiatlight.fiat_nodes.functions_graph_gui import _DraggedFnParamPin
from fiatlight.fiat_types.fiat_number_types import Float_0_1


def _graph_gui() -> FunctionsGraphGui:
    return FunctionsGraphGui(FunctionsGraph.create_empty())


def test_user_filter_cleaned_on_reopen() -> None:
    g = _graph_gui()
    g._palette_filter.search_text = "blur"
    g._palette_filter.selected_tags.append("filter")
    g._palette_filter.selected_category = "image"

    g._open_popup_at(ImVec2(0, 0))
    filt = g._open_popup.filter  # type: ignore[union-attr]

    # Same persistent object, filter reset on reopen.
    assert filt is g._palette_filter
    assert filt.search_text == ""
    assert filt.selected_tags == []
    assert filt.selected_category is None


def test_type_filters_reset_each_open() -> None:
    g = _graph_gui()
    # Drag-from-an-output opens with an input_type_filter set.
    pin = _DraggedFnParamPin(pin_id=None, pin_kind=PinKind.OUTPUT, pin_type=Float_0_1)  # type: ignore[arg-type]
    g._open_popup_at(ImVec2(0, 0), dragged_pin=pin)
    assert g._palette_filter.input_type_filter is Float_0_1

    # A plain reopen (no drag) clears the per-open type filters.
    g._open_popup_at(ImVec2(0, 0))
    assert g._palette_filter.input_type_filter is None
    assert g._palette_filter.output_type_filter is None
