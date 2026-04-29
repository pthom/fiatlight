"""FunctionPalette filtering: compatibility, search, and combined filters."""

from typing import NewType

import fiatlight as fl
from fiatlight.fiat_palette import FunctionPalette, PaletteFilter, PinKind
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


def _names_for(p: FunctionPalette, *, input_type: type | None = None, output_type: type | None = None) -> set[str]:
    """Helper: build a PaletteFilter with the given type filter(s) and return the names of matching functions."""
    flt = PaletteFilter()
    flt.input_type_filter = input_type
    flt.output_type_filter = output_type
    return {fi.name for fi in p.filter(flt)}


def test_input_type_filter_int() -> None:
    """`input_type_filter=int` selects functions with at least one INPUT accepting int."""
    p = _palette()
    names = _names_for(p, input_type=int)
    assert "consume_int" in names
    # consume_my_int does NOT accept int (int -> MyInt is rejected by strict typing)
    assert "consume_my_int" not in names
    assert "consume_str" not in names
    assert "produce_int" not in names  # no inputs


def test_input_type_filter_my_int() -> None:
    """`input_type_filter=MyInt` selects functions accepting MyInt (or its supertype int)."""
    p = _palette()
    names = _names_for(p, input_type=MyInt)
    assert "consume_int" in names  # MyInt -> int via supertype walk
    assert "consume_my_int" in names  # MyInt -> MyInt
    assert "consume_str" not in names


def test_output_type_filter_int() -> None:
    """`output_type_filter=int` selects producers whose output is int (or NewType-of-int)."""
    p = _palette()
    names = _names_for(p, output_type=int)
    assert "produce_int" in names
    assert "produce_str" not in names


def test_output_type_filter_my_int_strict() -> None:
    """`output_type_filter=MyInt` rejects plain `int` outputs (int -> MyInt is unsafe)."""
    p = _palette()
    names = _names_for(p, output_type=MyInt)
    assert "produce_int" not in names
    assert "produce_str" not in names


def test_palette_caches_input_output_types() -> None:
    """Sanity check: types are cached per FunctionInfo so the popup is cheap."""
    p = _palette()
    info_consume_int = next(fi for fi in p._functions if fi.name == "consume_int")
    assert info_consume_int.input_types == [("x", int)]
    assert info_consume_int.output_types == [int]


def test_filter_combines_type_filter_and_search() -> None:
    """Type filter + search-text filter compose."""
    p = _palette()

    only_compat = PaletteFilter(input_type_filter=int)
    names_compat = {fi.name for fi in p.filter(only_compat)}
    assert names_compat == {"consume_int"}

    compat_and_search = PaletteFilter(input_type_filter=int, search_text="int")
    names_both = {fi.name for fi in p.filter(compat_and_search)}
    assert names_both == {"consume_int"}

    compat_no_overlap = PaletteFilter(input_type_filter=int, search_text="str")
    assert p.filter(compat_no_overlap) == []


def test_filter_two_sided() -> None:
    """Both type filters combine via AND: function must match input AND output side."""
    p = _palette()

    # "Accepts int as input AND produces int" → consume_int (only one matching both).
    flt = PaletteFilter(
        input_type_filter=int,
        output_type_filter=int,
    )
    names = {fi.name for fi in p.filter(flt)}
    assert names == {"consume_int"}


def test_pin_kind_enum_string_values() -> None:
    """PinKind values match the legacy "input" / "output" strings (so any
    persisted state stays compatible)."""
    assert PinKind.INPUT.value == "input"
    assert PinKind.OUTPUT.value == "output"
