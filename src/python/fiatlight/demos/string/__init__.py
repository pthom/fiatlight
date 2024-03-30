from fiatlight.demos.string.str_functions import (
    str_lower,
    text_from_file,
    sort_words,
    split_words,
    remove_empty_words,
    remove_non_letters,
)
from fiatlight.fiat_types import FunctionList


def all_functions() -> FunctionList:
    from fiatlight.demos.string.str_functions import all_functions as all_str_functions

    return all_str_functions  # type: ignore


__all__ = [
    "all_functions",
    "str_lower",
    "text_from_file",
    "sort_words",
    "split_words",
    "remove_empty_words",
    "remove_non_letters",
]
