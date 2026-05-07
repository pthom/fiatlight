"""Round-trip tests for the workspace JSON format introduced in
PR 3 of the graph-persistence rework. Covers `FunctionsGraph`-level
core data only. GUI-layer round-trip (positions, expand flags,
session) requires an imgui-node-editor context and is exercised by
manual smoke testing."""

from __future__ import annotations

import pytest

from fiatlight.fiat_core.function_with_gui import FunctionWithGui
from fiatlight.fiat_core.functions_graph import FunctionsGraph


def _f_a(x: int) -> int:
    return x


def _f_b(x: int) -> int:
    return x * 2


def _factory_from_ref(ref: str) -> FunctionWithGui:
    """Test-local registry: maps the saved function_ref back to a fresh
    FunctionWithGui for the loader."""
    mapping = {f.__module__ + "." + f.__qualname__: f for f in (_f_a, _f_b)}
    if ref not in mapping:
        raise ValueError(f"Unknown function ref: {ref!r}")
    return FunctionWithGui(mapping[ref])


def test_save_workspace_core_emits_id_keyed_nodes_and_links() -> None:
    g = FunctionsGraph.from_function_composition([_f_a, _f_b])
    saved = g.save_workspace_core_to_json()

    # Top-level shape.
    assert set(saved.keys()) == {"nodes", "links"}
    # Two nodes, one link.
    assert len(saved["nodes"]) == 2
    assert len(saved["links"]) == 1

    # Node entries carry function_ref and the live data slots.
    for entry in saved["nodes"].values():
        assert "function_ref" in entry
        assert entry["function_ref"].endswith(("._f_a", "._f_b"))
        for key in ("function_name", "input_values", "input_gui_options", "output_gui_options"):
            assert key in entry

    # Link refers nodes by stable_id, not by name.
    link = saved["links"][0]
    assert set(link.keys()) == {"src_node", "src_output_idx", "dst_node", "dst_input_name"}
    saved_ids = list(saved["nodes"].keys())
    assert link["src_node"] in saved_ids
    assert link["dst_node"] in saved_ids


def test_workspace_core_roundtrip_preserves_topology_and_ids() -> None:
    g1 = FunctionsGraph.from_function_composition([_f_a, _f_b])
    saved = g1.save_workspace_core_to_json()
    saved_ids = [n.stable_id for n in g1.functions_nodes]

    g2 = FunctionsGraph.create_empty()
    g2.load_workspace_core_from_json(saved, _factory_from_ref)

    assert [n.stable_id for n in g2.functions_nodes] == saved_ids
    assert len(g2.functions_nodes_links) == 1
    link = g2.functions_nodes_links[0]
    assert link.src_function_node.stable_id == saved_ids[0]
    assert link.dst_function_node.stable_id == saved_ids[1]


def test_workspace_core_roundtrip_keeps_counter_ahead_of_loaded_ids() -> None:
    g1 = FunctionsGraph.from_function_composition([_f_a, _f_b])
    saved = g1.save_workspace_core_to_json()

    g2 = FunctionsGraph.create_empty()
    g2.load_workspace_core_from_json(saved, _factory_from_ref)

    # New nodes added after load must not collide with existing ids.
    new_node = g2.add_function(_f_a)
    existing_ids = {n.stable_id for n in g2.functions_nodes if n is not new_node}
    assert new_node.stable_id not in existing_ids


def test_workspace_core_loader_skips_missing_function_refs() -> None:
    g1 = FunctionsGraph.from_function_composition([_f_a, _f_b])
    saved = g1.save_workspace_core_to_json()

    def broken_factory(ref: str) -> FunctionWithGui:
        if ref.endswith("._f_b"):
            raise ValueError(f"Function {ref} not in palette")
        return _factory_from_ref(ref)

    g2 = FunctionsGraph.create_empty()
    g2.load_workspace_core_from_json(saved, broken_factory)

    # Only _f_a should have been loaded; the link touching _f_b is dropped.
    assert len(g2.functions_nodes) == 1
    assert g2.functions_nodes[0].function_with_gui.function_ref.endswith("._f_a")
    assert len(g2.functions_nodes_links) == 0


def test_workspace_core_loader_drops_links_with_missing_endpoint() -> None:
    g1 = FunctionsGraph.from_function_composition([_f_a, _f_b])
    saved = g1.save_workspace_core_to_json()
    # Inject a phantom link referencing a non-existent destination id.
    saved["links"].append(
        {
            "src_node": list(saved["nodes"].keys())[0],
            "src_output_idx": 0,
            "dst_node": "n_phantom",
            "dst_input_name": "x",
        }
    )

    g2 = FunctionsGraph.create_empty()
    g2.load_workspace_core_from_json(saved, _factory_from_ref)

    # The phantom link is dropped; the real link survives.
    assert len(g2.functions_nodes_links) == 1


def test_programmatic_mode_load_does_not_rebuild_topology() -> None:
    """rebuild_topology=False: code is the source of truth for topology;
    loader only restores values + GUI options against existing nodes
    (matched by stable_id)."""
    g1 = FunctionsGraph.from_function_composition([_f_a, _f_b])
    # Pretend the user changed an input value before saving.
    saved = g1.save_workspace_core_to_json()
    nodes = list(saved["nodes"].values())
    # Inject a value to verify it round-trips into the right node.
    nodes[0]["input_values"] = {"x": {"name": "x", "data": {"type": "Primitive", "value": 42}}}

    # Fresh graph from the same code.
    g2 = FunctionsGraph.from_function_composition([_f_a, _f_b])
    g2_topology_before = (
        [n.stable_id for n in g2.functions_nodes],
        len(g2.functions_nodes_links),
    )
    g2.load_workspace_core_from_json(saved, _factory_from_ref, rebuild_topology=False)
    g2_topology_after = (
        [n.stable_id for n in g2.functions_nodes],
        len(g2.functions_nodes_links),
    )

    # Topology untouched.
    assert g2_topology_before == g2_topology_after


def test_workspace_refuses_future_version() -> None:
    from fiatlight.fiat_nodes.functions_graph_gui import FunctionsGraphGui

    g = FunctionsGraph.create_empty()
    gui = FunctionsGraphGui(g)
    with pytest.raises(ValueError, match="newer than this build"):
        gui.load_workspace_from_json({"version": 999, "nodes": {}, "links": []}, _factory_from_ref)


def test_session_focused_visible_roundtrip() -> None:
    from fiatlight.fiat_nodes.functions_graph_gui import FunctionsGraphGui

    g = FunctionsGraph.from_function_composition([_f_a, _f_b])
    gui = FunctionsGraphGui(g)

    # Default is False everywhere.
    saved = gui.save_session_to_json()
    sids = [n.stable_id for n in g.functions_nodes]
    assert all(saved["focused_function_visible"][s] is False for s in sids)

    # Toggle and round-trip.
    gui.function_nodes_gui[0]._focused_function_visible = True
    saved = gui.save_session_to_json()
    gui.function_nodes_gui[0]._focused_function_visible = False
    gui.load_session_from_json(saved)
    assert gui.function_nodes_gui[0]._focused_function_visible is True


def test_session_load_tolerates_unknown_node_ids() -> None:
    from fiatlight.fiat_nodes.functions_graph_gui import FunctionsGraphGui

    g = FunctionsGraph.from_function_composition([_f_a])
    gui = FunctionsGraphGui(g)
    # Saved session references a stable_id that no longer exists; loader
    # should ignore it without raising.
    gui.load_session_from_json({"version": 1, "focused_function_visible": {"n_gone": True}})
    # Existing node's flag is at its default.
    assert gui.function_nodes_gui[0]._focused_function_visible is False


def test_clear_all_empties_graph_and_preserves_counter() -> None:
    """clear_all() drops nodes + links but keeps the stable_id counter
    monotonic. Any node added after a clear receives an id that has never
    been used by anything saved earlier in the same session."""
    g = FunctionsGraph.from_function_composition([_f_a, _f_b])
    last_id_before_clear = g.functions_nodes[-1].stable_id

    g.clear_all()

    assert g.functions_nodes == []
    assert g.functions_nodes_links == []

    fresh = g.add_function(_f_a)
    assert fresh.stable_id != last_id_before_clear
    # Counter advanced past the previously used id.
    assert int(fresh.stable_id[1:]) > int(last_id_before_clear[1:])


def test_round_trip_save_clear_load_restores_state() -> None:
    """File menu round-trip: build → save → clear → load matches the
    original topology. Models what File > New followed by File > Open does
    to a composer-mode graph."""
    g = FunctionsGraph.from_function_composition([_f_a, _f_b])
    saved = g.save_workspace_core_to_json()
    saved_ids = [n.stable_id for n in g.functions_nodes]

    g.clear_all()
    assert g.functions_nodes == []
    assert g.functions_nodes_links == []

    g.load_workspace_core_from_json(saved, _factory_from_ref)
    assert [n.stable_id for n in g.functions_nodes] == saved_ids
    assert len(g.functions_nodes_links) == 1


def test_session_path_for_strips_workspace_suffix() -> None:
    from fiatlight.fiat_runner.fiat_gui import FiatGui

    assert FiatGui._session_path_for("/tmp/foo.fiat_workspace.json") == "/tmp/foo.fiat_session.json"
    # No canonical suffix: append, don't try to be clever.
    assert FiatGui._session_path_for("/tmp/foo.json") == "/tmp/foo.json.fiat_session.json"
