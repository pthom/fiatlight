from typing import List, Tuple
from fiatlight import FunctionsGraph, fiat_run, to_function_with_gui
from fiatlight.fiat_types import TextPath


WordWithCount = Tuple[str, int]


def get_text(text_file: TextPath) -> str:
    """This is our source of text."""
    with open(text_file, "r") as f:
        r = f.read()
    return r


def str_lower(s: str) -> str:
    return s.lower()


def remove_non_letters(s: str) -> str:
    r = ""
    for c in s:
        if c.isalpha():
            r += c
        else:
            r += " "
    return r


def split_words(s: str) -> List[str]:
    r = s.split(" ")
    return r


def remove_empty_words(words: List[str]) -> List[str]:
    r = [word for word in words if len(word) > 0]
    return r


def run_length_encode(input_list: List[str]) -> List[WordWithCount]:
    r: List[WordWithCount] = []

    for i in range(len(input_list)):
        current = input_list[i]
        previous = input_list[i - 1] if i > 0 else None
        if current == previous:
            previous_count = r[-1][1]
            r[-1] = (current, previous_count + 1)
        else:
            r.append((current, 1))
    return r


def sort_word_with_counts(words: List[WordWithCount]) -> List[WordWithCount]:
    r = sorted(words, key=lambda w: w[1], reverse=True)
    return r


def main() -> None:
    sorted_gui = to_function_with_gui(
        sorted, signature_string="(words: List[str], /, reverse: bool = False) -> List[str]"
    )

    fiat_run(
        FunctionsGraph.from_function_composition(
            [
                get_text,
                str_lower,
                remove_non_letters,
                split_words,
                remove_empty_words,
                sorted_gui,
                run_length_encode,
                sort_word_with_counts,
            ]
        )
    )


if __name__ == "__main__":
    main()
