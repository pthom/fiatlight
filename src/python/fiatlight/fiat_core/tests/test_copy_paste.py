"""Tests for the copy / paste / duplicate core: `FunctionsGraph.serialize_nodes`
and the additive `FunctionsGraph.instantiate_nodes`."""

from fiatlight.fiat_core.function_with_gui import FunctionWithGui
from fiatlight.fiat_core.functions_graph import FunctionsGraph


def src() -> int:
    return 1


def dbl(x: int) -> int:
    return x * 2


def _factory(ref: str) -> FunctionWithGui:
    """Re-create a FunctionWithGui from its function_ref (what the palette does at runtime)."""
    for f in (src, dbl):
        fwg = FunctionWithGui(f)
        if fwg.function_ref == ref:
            return fwg
    raise ValueError(f"unknown ref {ref}")


def test_instantiate_creates_fresh_nodes_and_remaps_internal_link() -> None:
    g = FunctionsGraph()
    n_src = g.add_function(src)
    n_dbl = g.add_function(dbl)
    g._add_link_from_function_nodes(n_src, n_dbl, dst_input_name="x", src_output_idx=0)

    payload = g.serialize_nodes([n_src, n_dbl])
    created = g.instantiate_nodes(payload, _factory)

    # Two fresh nodes, with stable ids distinct from the originals.
    assert len(created) == 2
    by_old = dict(created)
    new_src, new_dbl = by_old[n_src.stable_id], by_old[n_dbl.stable_id]
    assert {new_src.stable_id, new_dbl.stable_id}.isdisjoint({n_src.stable_id, n_dbl.stable_id})
    assert len(g.functions_nodes) == 4

    # The internal link was recreated between the two NEW nodes (not pointing at the originals).
    dup_links = [
        lk for lk in g.functions_nodes_links if lk.src_function_node is new_src and lk.dst_function_node is new_dbl
    ]
    assert len(dup_links) == 1
    assert len(g.functions_nodes_links) == 2


def test_links_with_an_endpoint_outside_the_copied_set_are_dropped() -> None:
    g = FunctionsGraph()
    n_src = g.add_function(src)
    n_dbl = g.add_function(dbl)
    g._add_link_from_function_nodes(n_src, n_dbl, dst_input_name="x", src_output_idx=0)

    # Copy only dbl: the src -> dbl link is external to the set and must not be recreated.
    payload = g.serialize_nodes([n_dbl])
    created = g.instantiate_nodes(payload, _factory)

    assert len(created) == 1
    assert len(g.functions_nodes_links) == 1  # only the original link remains


def test_unknown_function_ref_is_skipped() -> None:
    g = FunctionsGraph()
    n = g.add_function(dbl)
    payload = g.serialize_nodes([n])
    payload["nodes"][n.stable_id]["function_ref"] = "nope.does_not_exist"

    created = g.instantiate_nodes(payload, _factory)
    assert created == []
    assert len(g.functions_nodes) == 1  # nothing added
