from fiatlight.fiat_kits.fiat_text import (
    text_nodes,
    str_upper,
    split_words,
    join_words,
    unique_words,
    word_count,
    filter_out_short_words,
)
from fiatlight.fiat_palette import FunctionPalette


def test_text_pack_is_categorized_and_builds() -> None:
    p = FunctionPalette()
    for f in text_nodes():
        p.add_function(f)
    assert len(p._functions) == len(text_nodes())
    assert {fi.category for fi in p._functions} == {"text"}


def test_text_functions_compute() -> None:
    assert str_upper("ab") == "AB"
    assert split_words("a b  c") == ["a", "b", "c"]
    assert join_words(["a", "b"], "-") == "a-b"
    assert unique_words(["a", "b", "a", "c"]) == ["a", "b", "c"]
    assert word_count("one two three") == 3
    assert filter_out_short_words(["a", "abcd", "xy"], min_length=3) == ["abcd"]
