"""Reroute (relay) node: adopt-on-connect polymorphic typing + P1 invariant.

P1 = a connection that would make a reroute adopt a type which breaks an existing
downstream link is rejected (rather than silently dropping that link)."""
import typing

from fiatlight.fiat_core.function_node import FunctionNode
from fiatlight.fiat_core.functions_graph import FunctionsGraph
from fiatlight.fiat_core.reroute_function import RerouteFunctionWithGui, REROUTE_INPUT_NAME
from fiatlight.fiat_types.typename_utils import TypeLike


def _produce_int() -> int:
    return 1


def _produce_str() -> str:
    return "x"


def _consume_int(x: int) -> int:
    return x


def _in_type(reroute: FunctionNode) -> TypeLike:
    return reroute.function_with_gui.input(REROUTE_INPUT_NAME)._type


def _out_type(reroute: FunctionNode) -> TypeLike:
    return reroute.function_with_gui.output(0)._type


def test_reroute_starts_any_and_accepts_any_output() -> None:
    g = FunctionsGraph()
    g.add_function(_produce_int)
    g.add_function(RerouteFunctionWithGui())
    src, reroute = g.functions_nodes
    assert _in_type(reroute) is typing.Any and _out_type(reroute) is typing.Any
    ok, reason = g._can_add_link(src, reroute, dst_input_name=REROUTE_INPUT_NAME, src_output_idx=0)
    assert ok, reason


def test_reroute_adopts_input_type() -> None:
    g = FunctionsGraph()
    g.add_function(_produce_int)
    g.add_function(RerouteFunctionWithGui())
    src, reroute = g.functions_nodes
    g._add_link_from_function_nodes(src, reroute, dst_input_name=REROUTE_INPUT_NAME, src_output_idx=0)
    assert _in_type(reroute) is int and _out_type(reroute) is int


def test_reroute_reverts_to_any_on_disconnect() -> None:
    g = FunctionsGraph()
    g.add_function(_produce_int)
    g.add_function(RerouteFunctionWithGui())
    src, reroute = g.functions_nodes
    link = g._add_link_from_function_nodes(src, reroute, dst_input_name=REROUTE_INPUT_NAME, src_output_idx=0)
    assert _out_type(reroute) is int
    g._remove_link(link)
    assert _in_type(reroute) is typing.Any and _out_type(reroute) is typing.Any


def test_adopted_reroute_feeds_compatible_downstream() -> None:
    # produce_int -> reroute -> consume_int : everything compatible
    g = FunctionsGraph()
    g.add_function(_produce_int)
    g.add_function(RerouteFunctionWithGui())
    g.add_function(_consume_int)
    src, reroute, consumer = g.functions_nodes
    g._add_link_from_function_nodes(src, reroute, dst_input_name=REROUTE_INPUT_NAME, src_output_idx=0)
    ok, reason = g._can_add_link(reroute, consumer, dst_input_name="x", src_output_idx=0)
    assert ok, reason


def test_p1_rejects_upstream_that_would_break_downstream() -> None:
    # reroute -> consume_int (ok while reroute is Any). Then produce_str -> reroute
    # must be refused: it would make the reroute str, breaking str -> int downstream.
    g = FunctionsGraph()
    g.add_function(_produce_str)
    g.add_function(RerouteFunctionWithGui())
    g.add_function(_consume_int)
    src_str, reroute, consumer = g.functions_nodes
    g._add_link_from_function_nodes(reroute, consumer, dst_input_name="x", src_output_idx=0)
    ok, reason = g._can_add_link(src_str, reroute, dst_input_name=REROUTE_INPUT_NAME, src_output_idx=0)
    assert not ok
    assert "str" in reason and "int" in reason


def test_reroute_chain_propagates_type() -> None:
    # produce_int -> r1 -> r2 : r2 adopts int through the chain
    g = FunctionsGraph()
    g.add_function(_produce_int)
    g.add_function(RerouteFunctionWithGui())
    g.add_function(RerouteFunctionWithGui())
    src, r1, r2 = g.functions_nodes
    g._add_link_from_function_nodes(src, r1, dst_input_name=REROUTE_INPUT_NAME, src_output_idx=0)
    g._add_link_from_function_nodes(r1, r2, dst_input_name=REROUTE_INPUT_NAME, src_output_idx=0)
    assert _out_type(r2) is int


def test_p1_rejects_through_chain() -> None:
    # str -> r1 -> r2 -> consume_int : wiring str into the chain head is refused.
    g = FunctionsGraph()
    g.add_function(_produce_str)
    g.add_function(RerouteFunctionWithGui())
    g.add_function(RerouteFunctionWithGui())
    g.add_function(_consume_int)
    src_str, r1, r2, consumer = g.functions_nodes
    g._add_link_from_function_nodes(r2, consumer, dst_input_name="x", src_output_idx=0)
    g._add_link_from_function_nodes(r1, r2, dst_input_name=REROUTE_INPUT_NAME, src_output_idx=0)
    ok, _ = g._can_add_link(src_str, r1, dst_input_name=REROUTE_INPUT_NAME, src_output_idx=0)
    assert not ok


def _reroute_factory_from_ref(ref: str):  # type: ignore[no-untyped-def]
    """Test-local registry mapping saved refs back to fresh nodes for the loader."""
    from fiatlight.fiat_core.function_with_gui import FunctionWithGui

    plain = {f.__module__ + "." + f.__qualname__: f for f in (_produce_int, _consume_int)}
    if ref == RerouteFunctionWithGui().function_ref:
        return RerouteFunctionWithGui()
    if ref in plain:
        return FunctionWithGui(plain[ref])
    raise ValueError(f"Unknown ref {ref!r}")


def test_reroute_type_is_rederived_after_load() -> None:
    # produce_int -> reroute -> consume_int, saved then reloaded into a fresh graph:
    # the reroute's adopted type is not persisted, it is recomputed from the wiring.
    g = FunctionsGraph()
    g.add_function(_produce_int)
    g.add_function(RerouteFunctionWithGui())
    g.add_function(_consume_int)
    src, reroute, consumer = g.functions_nodes
    g._add_link_from_function_nodes(src, reroute, dst_input_name=REROUTE_INPUT_NAME, src_output_idx=0)
    g._add_link_from_function_nodes(reroute, consumer, dst_input_name="x", src_output_idx=0)
    saved = g.save_workspace_core_to_json()

    g2 = FunctionsGraph()
    g2.load_workspace_core_from_json(saved, _reroute_factory_from_ref, rebuild_topology=True)
    reroute2 = next(n for n in g2._reroute_nodes())
    assert _out_type(reroute2) is int


def test_no_reroute_graphs_unaffected() -> None:
    # Sanity: the reroute machinery is a no-op when there are no reroutes.
    g = FunctionsGraph()
    g.add_function(_produce_int)
    g.add_function(_consume_int)
    src, dst = g.functions_nodes
    ok, reason = g._can_add_link(src, dst, dst_input_name="x", src_output_idx=0)
    assert ok, reason
    assert g._reroute_nodes() == []
