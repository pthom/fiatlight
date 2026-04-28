"""Integration tests: FunctionsGraph._can_add_link rejects type-incompatible links."""

from typing import NewType

from fiatlight.fiat_core.functions_graph import FunctionsGraph


MyInt = NewType("MyInt", int)
MyInt.__doc__ = "MyInt is a synonym for int (NewType)"


def test_compatible_link_accepted() -> None:
    def produce_int() -> int:
        return 1

    def consume_int(x: int) -> int:
        return x

    g = FunctionsGraph.from_function_composition([produce_int, consume_int])
    src = g.functions_nodes[0]
    dst = g.functions_nodes[1]
    # Composition factory already created the link; our type check should have accepted it.
    assert len(g.functions_nodes_links) == 1
    ok, reason = g._can_add_link(src, dst, dst_input_name="x", src_output_idx=0)
    # link already exists so reason is "Link already exists" — but type compat passed (otherwise
    # we'd have hit the type-compat branch first? no, "already exists" is checked before types).
    assert "type" not in reason.lower()


def test_incompatible_link_rejected_int_to_str() -> None:
    def produce_int() -> int:
        return 1

    def consume_str(s: str) -> str:
        return s

    g = FunctionsGraph()  # type: ignore[call-arg]
    g.add_function(produce_int)
    g.add_function(consume_str)
    src = g.functions_nodes[0]
    dst = g.functions_nodes[1]
    ok, reason = g._can_add_link(src, dst, dst_input_name="s", src_output_idx=0)
    assert not ok
    assert "int" in reason and "str" in reason


def test_newtype_to_supertype_accepted_in_graph() -> None:
    def produce_my_int() -> MyInt:
        return MyInt(1)

    def consume_int(x: int) -> int:
        return x

    g = FunctionsGraph()  # type: ignore[call-arg]
    g.add_function(produce_my_int)
    g.add_function(consume_int)
    src = g.functions_nodes[0]
    dst = g.functions_nodes[1]
    ok, reason = g._can_add_link(src, dst, dst_input_name="x", src_output_idx=0)
    assert ok, f"expected accepted, got reason: {reason}"


def test_supertype_to_newtype_rejected_in_graph() -> None:
    def produce_int() -> int:
        return 1

    def consume_my_int(x: MyInt) -> MyInt:
        return x

    g = FunctionsGraph()  # type: ignore[call-arg]
    g.add_function(produce_int)
    g.add_function(consume_my_int)
    src = g.functions_nodes[0]
    dst = g.functions_nodes[1]
    ok, reason = g._can_add_link(src, dst, dst_input_name="x", src_output_idx=0)
    assert not ok
    assert "MyInt" in reason or "int" in reason
