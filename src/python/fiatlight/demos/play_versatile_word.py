from typing import List, Tuple
from fiatlight import AnyDataWithGui, FunctionsGraph, fiat_run, any_function_to_function_with_gui


poem = """
                 If

By Rudyard Kipling
_______________________________________________________

If you can keep your head when all about you
    Are losing theirs and blaming it on you,
If you can trust yourself when all men doubt you,
    But make allowance for their doubting too;
If you can wait and not be tired by waiting,
    Or being lied about, don't deal in lies,
Or being hated, don't give way to hating,
    And yet don't look too good, nor talk too wise:

If you can dream and not make dreams your master;
    If you can think and not make thoughts your aim;
If you can meet with Triumph and Disaster
    And treat those two impostors just the same;
If you can bear to hear the truth you've spoken
    Twisted by knaves to make a trap for fools,
Or watch the things you gave your life to, broken,
    And stoop and build 'em up with worn-out tools:

If you can make one heap of all your winnings
    And risk it on one turn of pitch-and-toss,
And lose, and start again at your beginnings
    And never breathe a word about your loss;
If you can force your heart and nerve and sinew
    To serve your turn long after they are gone,
And so hold on when there is nothing in you
    Except the Will which says to them: "Hold on!"

If you can talk with crowds and keep your virtue,
    Or walk with Kings nor lose the common touch,
If neither foes nor loving friends can hurt you,
    If all men count with you, but none too much;
If you can fill the unforgiving minute
    With sixty seconds' worth of distance run,
Yours is the Earth and everything that's in it,
    And - which is more - you'll be a Man, my son!
"""


WordWithCount = Tuple[str, int]


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


class TextFileWithGui(AnyDataWithGui[str]):
    """An example of a custom GUI for a string.
    It allows the user to select a text file and use its content."""

    from imgui_bundle import portable_file_dialogs as pfd

    open_file_dialog: pfd.open_file | None = None

    def __init__(self) -> None:
        super().__init__()
        self.callbacks.edit = self.edit
        self.callbacks.present_str = self.present_str
        self.callbacks.default_value_provider = lambda: poem

    def edit(self) -> bool:
        changed = False
        from imgui_bundle import imgui

        if imgui.button("Get from file"):
            self.open_file_dialog = self.pfd.open_file("Select text file")
        if self.open_file_dialog is not None and not self.open_file_dialog.ready():
            if len(self.open_file_dialog.result()) > 0:
                filename = self.open_file_dialog.result()[0]
                with open(filename, "r") as f:
                    self.value = f.read()
                changed = True
            self.open_file_dialog = None
        return changed

    def present_str(self, value: str) -> str:
        return value


def main() -> None:
    def get_text(text: str = poem) -> str:
        """This is our source of text.
        By default, it uses the poem variable defined above.
        It will be associated with a GUI that allows the user to select a text file
        (see the TextFileWithGui class above).
        """
        return text

    get_text_gui = any_function_to_function_with_gui(get_text)
    get_text_gui.set_input_gui("text", TextFileWithGui())

    # In this example, we will use the standard `sorted` function,
    # but we create a FunctionWithGui around it, by adding a signature_string,
    # so that the `reverse` parameter can be displayed as a checkbox in the GUI.
    # Notes:
    # - in Python, the sorted signature is untyped (and reverse is also untyped):
    #      def sorted(iterable, /, *, key=None, reverse=False)
    # - the "/" in the signature means that the parameters before it are positional-only
    #  (by default, fiatlight will try to specify all parameters using keywords, hence the need to specify this)
    # - we could also use the following more generic signature_string:
    #      "(iterable: Iterable[T], /, *, key: Optional[Callable[[T], Any]] = None, reverse: bool = False) -> List[T]"
    sorted_gui = any_function_to_function_with_gui(
        sorted, signature_string="(words: List[str], /, reverse: bool = False) -> List[str]"
    )

    fiat_run(
        FunctionsGraph.from_function_composition(
            [
                get_text_gui,
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
