"""Layer assignment for the Sugiyama-style auto-layout (pure, no imgui)."""
from fiatlight.fiat_nodes.functions_graph_gui import compute_layered_ranks


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
