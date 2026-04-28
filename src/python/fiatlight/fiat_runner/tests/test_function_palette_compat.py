"""FunctionPalette.get_compatible_function_infos: filter palette by pin type."""

from typing import NewType

import fiatlight as fl
from fiatlight.fiat_runner.function_palette import FunctionPalette
from fiatlight.fiat_types import Function


MyInt = NewType("MyInt", int)
MyInt.__doc__ = "MyInt is a synonym for int (NewType)"


@fl.with_fiat_attributes(fiat_tags=["t"])
def produce_int() -> int:
    return 0


@fl.with_fiat_attributes(fiat_tags=["t"])
def produce_str() -> str:
    return ""


@fl.with_fiat_attributes(fiat_tags=["t"])
def consume_int(x: int) -> int:
    return x


@fl.with_fiat_attributes(fiat_tags=["t"])
def consume_my_int(x: MyInt) -> MyInt:
    return x


@fl.with_fiat_attributes(fiat_tags=["t"])
def consume_str(s: str) -> str:
    return s


def _palette() -> FunctionPalette:
    p = FunctionPalette()
    fns: list[Function] = [produce_int, produce_str, consume_int, consume_my_int, consume_str]
    for fn in fns:
        p.add_function(fn)
    return p


def test_compatible_consumers_for_int_output() -> None:
    """Dragging an int output → consumers that accept int (incl. via NewType reverse-walking)."""
    p = _palette()
    infos = p.get_compatible_function_infos(int, "output")
    names = {fi.name for fi in infos}
    # consume_int accepts int directly. consume_my_int does NOT (int -> MyInt rejected).
    # consume_str does not match.
    assert "consume_int" in names
    assert "consume_my_int" not in names
    assert "consume_str" not in names


def test_compatible_consumers_for_my_int_output() -> None:
    """Dragging a MyInt output → consumers that accept MyInt or int."""
    p = _palette()
    infos = p.get_compatible_function_infos(MyInt, "output")
    names = {fi.name for fi in infos}
    assert "consume_int" in names  # MyInt → int via supertype
    assert "consume_my_int" in names  # MyInt → MyInt
    assert "consume_str" not in names


def test_compatible_producers_for_int_input() -> None:
    """Dragging an int input → producers whose output is int (or a NewType of int)."""
    p = _palette()
    infos = p.get_compatible_function_infos(int, "input")
    names = {fi.name for fi in infos}
    assert "produce_int" in names
    assert "produce_str" not in names


def test_compatible_producers_for_my_int_input() -> None:
    """Dragging a MyInt input → only producers whose output is MyInt (int → MyInt rejected)."""
    p = _palette()
    infos = p.get_compatible_function_infos(MyInt, "input")
    names = {fi.name for fi in infos}
    assert "produce_int" not in names  # int output cannot feed a MyInt input
    assert "produce_str" not in names


def test_palette_caches_input_output_types() -> None:
    """Sanity check: types are cached per FunctionInfo so the popup is cheap."""
    p = _palette()
    info_consume_int = next(fi for fi in p._functions if fi.name == "consume_int")
    assert info_consume_int.input_types == [("x", int)]
    assert info_consume_int.output_types == [int]
