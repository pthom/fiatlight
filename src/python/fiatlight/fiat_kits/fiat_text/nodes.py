"""Text node functions (category `text`, applied by the kit defaults).

Plain functions over `str` / `list[str]`; the type->GUI registry renders the
widgets automatically (`str` inputs get a text field, `list[str]` outputs get a
scrollable list with a Details popup).
"""
from typing import List

from fiatlight.fiat_types import TextPath
from fiatlight.fiat_utils.fiat_attributes_decorator import with_fiat_attributes


# ----------------------------------------------------------------------------- source / io
@with_fiat_attributes(
    text__allow_multiline_edit=True,
    text__size_multiline_em=(40.0, 8.0),
    fiat_tags=["source"],
)
def text_source(text: str = "") -> str:
    """A source node: type or paste text to feed downstream nodes."""
    return text


@with_fiat_attributes(fiat_tags=["io"])
def text_from_file(text_file: TextPath) -> str:
    """Read text from a file (the path shows a file-picker widget)."""
    with open(text_file, "r") as f:
        return f.read()


# ----------------------------------------------------------------------------- case
@with_fiat_attributes(fiat_tags=["case"])
def str_lower(s: str = "") -> str:
    return s.lower()


@with_fiat_attributes(fiat_tags=["case"])
def str_upper(s: str = "") -> str:
    return s.upper()


@with_fiat_attributes(fiat_tags=["case"])
def capitalize(s: str = "") -> str:
    return s.capitalize()


@with_fiat_attributes(fiat_tags=["case"])
def title(s: str = "") -> str:
    return s.title()


# ----------------------------------------------------------------------------- clean
@with_fiat_attributes(fiat_tags=["clean"])
def remove_non_letters(s: str = "") -> str:
    """Replace every non-letter character with a space."""
    return "".join(c if c.isalpha() else " " for c in s)


@with_fiat_attributes(fiat_tags=["clean"])
def strip_whitespace(s: str = "") -> str:
    return s.strip()


@with_fiat_attributes(fiat_tags=["clean"])
def collapse_whitespace(s: str = "") -> str:
    """Collapse runs of whitespace into single spaces."""
    return " ".join(s.split())


# ----------------------------------------------------------------------------- transform
@with_fiat_attributes(fiat_tags=["transform"])
def replace_text(s: str = "", old: str = "", new: str = "") -> str:
    return s.replace(old, new)


@with_fiat_attributes(fiat_tags=["transform"])
def reverse_text(s: str = "") -> str:
    return s[::-1]


@with_fiat_attributes(times__range=(0, 20), fiat_tags=["transform"])
def repeat_text(s: str = "", times: int = 2) -> str:
    return s * times


# ----------------------------------------------------------------------------- split / join
@with_fiat_attributes(fiat_tags=["split"])
def split_words(s: str = "") -> List[str]:
    return s.split()


@with_fiat_attributes(fiat_tags=["split"])
def split_lines(s: str = "") -> List[str]:
    return s.splitlines()


@with_fiat_attributes(fiat_tags=["split"])
def join_words(words: List[str], separator: str = " ") -> str:
    return separator.join(words)


# ----------------------------------------------------------------------------- list operations
@with_fiat_attributes(fiat_tags=["list"])
def remove_empty_words(words: List[str]) -> List[str]:
    return [w for w in words if len(w) > 0]


@with_fiat_attributes(fiat_tags=["sort"])
def sort_words(words: List[str], reverse: bool = False) -> List[str]:
    return sorted(words, reverse=reverse)


@with_fiat_attributes(fiat_tags=["list"])
def unique_words(words: List[str]) -> List[str]:
    """Distinct words, keeping first-seen order."""
    seen: set[str] = set()
    r: List[str] = []
    for w in words:
        if w not in seen:
            seen.add(w)
            r.append(w)
    return r


@with_fiat_attributes(min_length__range=(1, 20), fiat_tags=["filter"])
def filter_out_short_words(words: List[str], min_length: int = 4) -> List[str]:
    return [w for w in words if len(w) >= min_length]


# ----------------------------------------------------------------------------- analyze (-> numbers; bridges into math)
@with_fiat_attributes(fiat_tags=["analyze"])
def char_count(s: str = "") -> int:
    return len(s)


@with_fiat_attributes(fiat_tags=["analyze"])
def word_count(s: str = "") -> int:
    return len(s.split())


@with_fiat_attributes(fiat_tags=["analyze"])
def count_words(words: List[str]) -> int:
    return len(words)
