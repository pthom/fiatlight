"""Text node pack for fiatlight.

A small batteries-included set of string / word-list functions, each tagged by
intent and put in the `text` category (applied once by the kit defaults).
`text_nodes()` returns them in a stable order.
"""
from typing import Callable, List, Any

from fiatlight.fiat_utils.fiat_attributes_decorator import add_fiat_attributes
from .nodes import (
    text_source,
    text_from_file,
    str_lower,
    str_upper,
    capitalize,
    title,
    remove_non_letters,
    strip_whitespace,
    collapse_whitespace,
    replace_text,
    reverse_text,
    repeat_text,
    split_words,
    split_lines,
    join_words,
    remove_empty_words,
    sort_words,
    unique_words,
    filter_out_short_words,
    char_count,
    word_count,
    count_words,
)

__all__ = [
    "text_nodes",
    "text_source",
    "text_from_file",
    "str_lower",
    "str_upper",
    "capitalize",
    "title",
    "remove_non_letters",
    "strip_whitespace",
    "collapse_whitespace",
    "replace_text",
    "reverse_text",
    "repeat_text",
    "split_words",
    "split_lines",
    "join_words",
    "remove_empty_words",
    "sort_words",
    "unique_words",
    "filter_out_short_words",
    "char_count",
    "word_count",
    "count_words",
]


def text_nodes() -> List[Callable[..., Any]]:
    """Return every text node, grouped by intent (stable order)."""
    return [
        # source / io
        text_source,
        text_from_file,
        # case
        str_lower,
        str_upper,
        capitalize,
        title,
        # clean
        remove_non_letters,
        strip_whitespace,
        collapse_whitespace,
        # transform
        replace_text,
        reverse_text,
        repeat_text,
        # split / join
        split_words,
        split_lines,
        join_words,
        # list operations
        remove_empty_words,
        sort_words,
        unique_words,
        filter_out_short_words,
        # analyze
        char_count,
        word_count,
        count_words,
    ]


def _apply_kit_defaults() -> None:
    """Put every node in this pack in the `text` category, once, instead of
    repeating `fiat_category="text"` on each function."""
    for fn in text_nodes():
        add_fiat_attributes(fn, fiat_category="text")


_apply_kit_defaults()
