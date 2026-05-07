"""Tests for stable node identity: `FunctionNode.stable_id`,
`FunctionWithGui.function_ref`, and the lambda/partial refusal path."""

import functools

import pytest

from fiatlight.fiat_core.function_with_gui import FunctionWithGui
from fiatlight.fiat_core.functions_graph import FunctionsGraph
from fiatlight.fiat_core.togui_exception import FiatToGuiException


def _color_convert(x: int) -> int:
    return x


def test_two_instances_have_distinct_stable_ids_and_same_function_ref() -> None:
    g = FunctionsGraph()
    n1 = g.add_function(_color_convert)
    n2 = g.add_function(_color_convert)
    assert n1.stable_id != n2.stable_id
    assert n1.function_with_gui.function_ref == n2.function_with_gui.function_ref
    assert n1.function_with_gui.function_ref.endswith("._color_convert")


def test_stable_ids_are_never_reused_after_remove() -> None:
    g = FunctionsGraph()
    n1 = g.add_function(_color_convert)
    g._remove_function_node(n1)
    n2 = g.add_function(_color_convert)
    assert n1.stable_id != n2.stable_id


def test_function_ref_refuses_lambda() -> None:
    with pytest.raises(FiatToGuiException, match="lambdas are not supported"):
        FunctionWithGui(lambda x: x, fn_name="fake")


def test_function_ref_refuses_functools_partial() -> None:
    def base(x: int, y: int) -> int:
        return x + y

    p = functools.partial(base, 1)
    with pytest.raises(FiatToGuiException, match="functools.partial is not supported"):
        FunctionWithGui(p, fn_name="fake")


def test_add_link_raises_on_ambiguous_name() -> None:
    g = FunctionsGraph()
    g.add_function(_color_convert)
    g.add_function(_color_convert)
    # The suffix scheme keeps the names distinct today (so no ambiguity),
    # but if the suffix scheme is ever bypassed the resolver must surface
    # the ambiguity with a clear message rather than silently picking one.
    g.functions_nodes[1].function_with_gui.function_name = "_color_convert"
    with pytest.raises(ValueError, match="resolves to 2 nodes"):
        g._function_node_with_name("_color_convert")
