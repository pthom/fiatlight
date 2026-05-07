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


def test_load_workspace_queues_positions_by_stable_id() -> None:
    g = FunctionsGraph()
    g.add_function(_identity)
    sid = g.functions_nodes[0].stable_id

    gui = FunctionsGraphGui(g)
    workspace = {
        "version": 1,
        "nodes": {
            sid: {
                "function_ref": _identity.__module__ + "._identity",
                "function_name": "_identity",
                "input_values": {},
                "input_gui_options": {},
                "output_gui_options": {},
                "position": [12.5, 34.0],
                "expand_flags": {},
            }
        },
        "links": [],
    }
    gui.load_workspace_from_json(workspace, _factory_from_ref, rebuild_topology=False)
    assert gui._pending_loaded_positions_by_stable_id is not None
    pos = gui._pending_loaded_positions_by_stable_id[sid]
    assert (pos.x, pos.y) == (12.5, 34.0)


def test_load_workspace_skips_malformed_position_entries() -> None:
    g = FunctionsGraph()
    g.add_function(_identity)
    sid = g.functions_nodes[0].stable_id

    gui = FunctionsGraphGui(g)
    workspace = {
        "version": 1,
        "nodes": {
            sid: {
                "function_ref": _identity.__module__ + "._identity",
                "function_name": "_identity",
                "input_values": {},
                "input_gui_options": {},
                "output_gui_options": {},
                "position": "nope",  # malformed: should be [x, y]
                "expand_flags": {},
            }
        },
        "links": [],
    }
    gui.load_workspace_from_json(workspace, _factory_from_ref, rebuild_topology=False)
    # Malformed position is just ignored; no pending dict entry created.
    assert gui._pending_loaded_positions_by_stable_id is None


def test_load_workspace_tolerates_extra_node_ids() -> None:
    """Saved positions reference a stable_id with no matching node in the
    current graph (e.g. user removed it from code). Loader should ignore
    the orphan, not raise."""
    g = FunctionsGraph()
    g.add_function(_identity)
    sid_present = g.functions_nodes[0].stable_id

    gui = FunctionsGraphGui(g)
    workspace = {
        "version": 1,
        "nodes": {
            sid_present: {
                "function_ref": _identity.__module__ + "._identity",
                "function_name": "_identity",
                "input_values": {},
                "input_gui_options": {},
                "output_gui_options": {},
                "position": [1.0, 1.0],
                "expand_flags": {},
            },
            "n_gone": {
                "function_ref": _identity.__module__ + "._identity",
                "function_name": "_identity",
                "input_values": {},
                "input_gui_options": {},
                "output_gui_options": {},
                "position": [9.0, 9.0],
                "expand_flags": {},
            },
        },
        "links": [],
    }
    gui.load_workspace_from_json(workspace, _factory_from_ref, rebuild_topology=False)
    assert gui._pending_loaded_positions_by_stable_id is not None
    # Only the present node has a pending position; the orphan is dropped
    # (we iterate function_nodes_gui to build the pending dict).
    assert sid_present in gui._pending_loaded_positions_by_stable_id
    assert "n_gone" not in gui._pending_loaded_positions_by_stable_id


def test_pending_loaded_positions_are_imvec2() -> None:
    g = FunctionsGraph()
    g.add_function(_identity)
    sid = g.functions_nodes[0].stable_id

    gui = FunctionsGraphGui(g)
    workspace = {
        "version": 1,
        "nodes": {
            sid: {
                "function_ref": _identity.__module__ + "._identity",
                "function_name": "_identity",
                "input_values": {},
                "input_gui_options": {},
                "output_gui_options": {},
                "position": [1, 2],
                "expand_flags": {},
            }
        },
        "links": [],
    }
    gui.load_workspace_from_json(workspace, _factory_from_ref, rebuild_topology=False)
    assert gui._pending_loaded_positions_by_stable_id is not None
    assert isinstance(gui._pending_loaded_positions_by_stable_id[sid], ImVec2)
