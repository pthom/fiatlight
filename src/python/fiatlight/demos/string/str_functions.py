from typing import List
from fiatlight.fiat_types import TextPath


def text_from_file(text_file: TextPath) -> str:
    """This is our source of text.
    Since text_file is a TextPath (a type alias for str), it will be displayed
    as a widget in the UI, allowing the user to select a text file.
    """
    with open(text_file, "r") as f:
        r = f.read()
    return r


def str_lower(s: str) -> str:
    """Convert a string to lowercase."""
    return s.lower()


def remove_non_letters(s: str) -> str:
    """Remove all non-letter characters from a string."""
    r = ""
    for c in s:
        if c.isalpha():
            r += c
        else:
            r += " "
    return r


def split_words(s: str) -> List[str]:
    """Split a string into a list of words."""
    r = s.split(" ")
    return r


def remove_empty_words(words: List[str]) -> List[str]:
    """Remove empty words from a list of words."""
    r = [word for word in words if len(word) > 0]
    return r


def sort_words(words: List[str], reverse: bool = False) -> List[str]:
    """Sort a list of words alphabetically (or reverse alphabetically)."""
    r = sorted(words, reverse=reverse)
    return r


all_functions = [text_from_file, str_lower, remove_non_letters, split_words, remove_empty_words, sort_words]
