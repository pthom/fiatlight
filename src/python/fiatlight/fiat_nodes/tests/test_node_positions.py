"""Tests for node-position queueing in `load_workspace_from_json`.

Save-side requires a real imgui-node-editor context (`ed.get_node_position`
only works inside `ed.begin/end`), so it's covered by manual GUI smoke
tests, not here. The load-side and the JSON shape can be exercised
headlessly."""

from imgui_bundle import ImVec2

from fiatlight.fiat_core.function_with_gui import FunctionWithGui
from fiatlight.fiat_core.functions_graph import FunctionsGraph
from fiatlight.fiat_nodes.functions_graph_gui import FunctionsGraphGui


def _identity(x: int) -> int:
    return x


def _factory_from_ref(ref: str) -> FunctionWithGui:
    if ref.endswith("._identity"):
        return FunctionWithGui(_identity)
    raise ValueError(f"Unknown ref: {ref}")


def test_parse_positions_by_stable_id() -> None:
    g = FunctionsGraph()
    g.add_function(_identity)
    sid = g.functions_nodes[0].stable_id

    gui = FunctionsGraphGui(g)
    nodes_data = {sid: {"position": [12.5, 34.0]}}
    parsed = gui._parse_loaded_node_positions(nodes_data)
    pos = parsed[sid]
    assert (pos.x, pos.y) == (12.5, 34.0)


def test_parse_positions_skips_malformed_entries() -> None:
    g = FunctionsGraph()
    g.add_function(_identity)
    sid = g.functions_nodes[0].stable_id

    gui = FunctionsGraphGui(g)
    nodes_data = {sid: {"position": "nope"}}  # malformed: should be [x, y]
    # Malformed position is just ignored; no parsed entry created.
    assert gui._parse_loaded_node_positions(nodes_data) == {}


def test_parse_positions_tolerates_extra_node_ids() -> None:
    """Saved positions reference a stable_id with no matching node in the
    current graph (e.g. user removed it from code). Parser should ignore
    the orphan, not raise."""
    g = FunctionsGraph()
    g.add_function(_identity)
    sid_present = g.functions_nodes[0].stable_id

    gui = FunctionsGraphGui(g)
    nodes_data = {
        sid_present: {"position": [1.0, 1.0]},
        "n_gone": {"position": [9.0, 9.0]},
    }
    parsed = gui._parse_loaded_node_positions(nodes_data)
    # Only the present node is parsed; the orphan is dropped
    # (we iterate function_nodes_gui to build the dict).
    assert sid_present in parsed
    assert "n_gone" not in parsed


def test_parsed_positions_are_imvec2() -> None:
    g = FunctionsGraph()
    g.add_function(_identity)
    sid = g.functions_nodes[0].stable_id

    gui = FunctionsGraphGui(g)
    nodes_data = {sid: {"position": [1, 2]}}
    parsed = gui._parse_loaded_node_positions(nodes_data)
    assert isinstance(parsed[sid], ImVec2)


def _node_data(*, position: object) -> dict[str, object]:
    data: dict[str, object] = {
        "function_ref": _identity.__module__ + "._identity",
        "function_name": "_identity",
        "input_values": {},
        "input_gui_options": {},
        "output_gui_options": {},
        "expand_flags": {},
    }
    if position is not None:
        data["position"] = position
    return data


def _load_keys(position: object) -> list[str]:
    """Load a one-node workspace (optionally with a saved position) and return
    the scheduler's pending action keys."""
    g = FunctionsGraph()
    g.add_function(_identity)
    sid = g.functions_nodes[0].stable_id
    gui = FunctionsGraphGui(g)
    workspace = {"version": 1, "nodes": {sid: _node_data(position=position)}, "links": []}
    gui.load_workspace_from_json(workspace, _factory_from_ref, rebuild_topology=False)
    return gui._sched.pending_keys()


def test_load_workspace_schedules_position_apply() -> None:
    """Loading a workspace with positions queues a deferred apply (run later
    inside ed.begin/end); loading one without positions queues nothing."""
    assert "loaded_positions" in _load_keys([3.0, 4.0])
    assert "loaded_positions" not in _load_keys(None)
