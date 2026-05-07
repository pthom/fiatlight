"""Tests for node position persistence (PR 2 of graph-persistence rework).

Save-side requires a real imgui-node-editor context (`ed.get_node_position`
only works inside `ed.begin/end`), so it's covered by manual GUI smoke
tests, not here. The load-side and the JSON shape can be exercised
headlessly."""

from imgui_bundle import ImVec2

from fiatlight.fiat_core.functions_graph import FunctionsGraph
from fiatlight.fiat_nodes.functions_graph_gui import FunctionsGraphGui


def _identity(x: int) -> int:
    return x


def test_load_node_positions_queues_positions_by_function_name() -> None:
    g = FunctionsGraph()
    g.add_function(_identity)
    gui = FunctionsGraphGui(g)
    gui.load_node_positions_from_json({"_identity": [12.5, 34.0]})
    assert gui._pending_loaded_positions is not None
    pos = gui._pending_loaded_positions["_identity"]
    assert (pos.x, pos.y) == (12.5, 34.0)


def test_load_node_positions_skips_malformed_entries() -> None:
    g = FunctionsGraph()
    gui = FunctionsGraphGui(g)
    gui.load_node_positions_from_json({"good": [1.0, 2.0], "bogus": "nope", "short": [1]})
    assert gui._pending_loaded_positions is not None
    assert "good" in gui._pending_loaded_positions
    assert "bogus" not in gui._pending_loaded_positions
    assert "short" not in gui._pending_loaded_positions


def test_load_node_positions_tolerates_unknown_function_names() -> None:
    g = FunctionsGraph()
    g.add_function(_identity)
    gui = FunctionsGraphGui(g)
    # Saved positions reference a function that doesn't exist in the current
    # graph (e.g. user removed it from code). Load should still queue them;
    # _apply_pending_loaded_positions silently ignores unmatched names.
    gui.load_node_positions_from_json({"_identity": [1.0, 1.0], "_gone": [9.0, 9.0]})
    assert gui._pending_loaded_positions is not None
    assert set(gui._pending_loaded_positions.keys()) == {"_identity", "_gone"}


def test_pending_loaded_positions_is_imvec2() -> None:
    g = FunctionsGraph()
    gui = FunctionsGraphGui(g)
    gui.load_node_positions_from_json({"a": [1, 2]})
    assert gui._pending_loaded_positions is not None
    assert isinstance(gui._pending_loaded_positions["a"], ImVec2)
