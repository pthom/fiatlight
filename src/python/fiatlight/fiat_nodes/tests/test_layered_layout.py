"""Layer assignment + crossing minimization for the Sugiyama-style auto-layout
(pure, no imgui)."""
from fiatlight.fiat_nodes.sugiyama_layout import (
    compute_layered_ranks,
    order_layers_to_reduce_crossings,
)


def test_linear_pipeline() -> None:
    # a -> b -> c
    layer = compute_layered_ranks(["a", "b", "c"], [("a", "b"), ("b", "c")])
    assert layer == {"a": 0, "b": 1, "c": 2}


def test_longest_path_wins() -> None:
    # a -> b -> d, a -> d  : d must sit past the longest path (layer 2), not 1.
    layer = compute_layered_ranks(["a", "b", "d"], [("a", "b"), ("b", "d"), ("a", "d")])
    assert layer == {"a": 0, "b": 1, "d": 2}


def test_diamond() -> None:
    # a -> b, a -> c, b -> d, c -> d
    layer = compute_layered_ranks(["a", "b", "c", "d"], [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")])
    assert layer == {"a": 0, "b": 1, "c": 1, "d": 2}


def test_isolated_and_multiple_sources() -> None:
    # two separate chains + an isolated node, all sources at layer 0.
    layer = compute_layered_ranks(["x", "a", "b", "p", "q"], [("a", "b"), ("p", "q")])
    assert layer == {"x": 0, "a": 0, "b": 1, "p": 0, "q": 1}


def test_unknown_edges_ignored() -> None:
    layer = compute_layered_ranks(["a", "b"], [("a", "b"), ("a", "ghost"), ("ghost", "b")])
    assert layer == {"a": 0, "b": 1}


def test_cycle_does_not_loop() -> None:
    # a -> b -> a (cycle): no crash/hang; the back-edge keeps nodes at layer 0.
    layer = compute_layered_ranks(["a", "b"], [("a", "b"), ("b", "a")])
    assert layer == {"a": 0, "b": 0}


def _crossings(columns: dict[int, list[str]], edges: list[tuple[str, str]], layer: dict[str, int]) -> int:
    pos = {sid: i for col in columns.values() for i, sid in enumerate(col)}
    total = 0
    for L in range(max(layer.values(), default=0)):
        pairs = sorted((pos[s], pos[d]) for s, d in edges if layer.get(s) == L and layer.get(d) == L + 1)
        targets = [d for _, d in pairs]
        total += sum(1 for i in range(len(targets)) for j in range(i + 1, len(targets)) if targets[i] > targets[j])
    return total


def test_reduces_a_simple_crossing() -> None:
    # a -> d, b -> c  with stable order [a,b]/[c,d] crosses; reorder fixes it.
    order = ["a", "b", "c", "d"]
    edges = [("a", "d"), ("b", "c")]
    layer = {"a": 0, "b": 0, "c": 1, "d": 1}
    cols = order_layers_to_reduce_crossings(order, edges, layer)
    assert cols == {0: ["a", "b"], 1: ["d", "c"]}
    assert _crossings(cols, edges, layer) == 0


def test_keeps_a_non_crossing_order() -> None:
    order = ["a", "b", "c", "d"]
    edges = [("a", "c"), ("b", "d")]
    layer = {"a": 0, "b": 0, "c": 1, "d": 1}
    cols = order_layers_to_reduce_crossings(order, edges, layer)
    assert cols == {0: ["a", "b"], 1: ["c", "d"]}


def test_never_increases_crossings() -> None:
    # A 3-layer graph whose stable order has crossings; result must be <= stable.
    order = ["s", "a", "b", "c", "x", "y"]
    edges = [("s", "b"), ("s", "a"), ("a", "y"), ("b", "x"), ("c", "x")]
    layer = compute_layered_ranks(order, edges)
    stable = {L: [sid for sid in order if layer[sid] == L] for L in range(max(layer.values()) + 1)}
    cols = order_layers_to_reduce_crossings(order, edges, layer)
    assert _crossings(cols, edges, layer) <= _crossings(stable, edges, layer)
