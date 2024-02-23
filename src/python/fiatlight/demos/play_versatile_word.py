from typing import List, Tuple


poem = """
 If—
By Rudyard Kipling

If you can keep your head when all about you
    Are losing theirs and blaming it on you,
If you can trust yourself when all men doubt you,
    But make allowance for their doubting too;
If you can wait and not be tired by waiting,
    Or being lied about, don’t deal in lies,
Or being hated, don’t give way to hating,
    And yet don’t look too good, nor talk too wise:

If you can dream—and not make dreams your master;
    If you can think—and not make thoughts your aim;
If you can meet with Triumph and Disaster
    And treat those two impostors just the same;
If you can bear to hear the truth you’ve spoken
    Twisted by knaves to make a trap for fools,
Or watch the things you gave your life to, broken,
    And stoop and build ’em up with worn-out tools:

If you can make one heap of all your winnings
    And risk it on one turn of pitch-and-toss,
And lose, and start again at your beginnings
    And never breathe a word about your loss;
If you can force your heart and nerve and sinew
    To serve your turn long after they are gone,
And so hold on when there is nothing in you
    Except the Will which says to them: ‘Hold on!’

If you can talk with crowds and keep your virtue,
    Or walk with Kings—nor lose the common touch,
If neither foes nor loving friends can hurt you,
    If all men count with you, but none too much;
If you can fill the unforgiving minute
    With sixty seconds’ worth of distance run,
Yours is the Earth and everything that’s in it,
    And—which is more—you’ll be a Man, my son!
"""


WordWithCount = Tuple[str, int]


def str_lower(s: str) -> str:
    return s.lower()


def remove_non_letters(s: str) -> str:
    r = ""
    for c in s:
        if c.isalpha() or c == " ":
            r += c
        elif c.isspace():
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


def display_word_with_counts(words: List[WordWithCount]) -> str:
    strs = [w[0] + ": " + str(w[1]) for w in words]
    r = "\n".join(strs)
    return r


def main() -> None:
    # from fiatlight import data_presenters as dp
    #
    # functions = [
    #     dp.make_str_source(
    #         poem,
    #         dp.StrWithGuiParams(
    #             edit_type=dp.StrEditType.multiline,
    #             height_em=3,
    #         ),
    #     ),
    #     remove_non_letters,
    #     str_lower,
    #     split_words,
    #     remove_empty_words,
    #     sorted,
    #     run_length_encode,
    #     sort_word_with_counts,
    #     display_word_with_counts,
    # ]
    # fiatlight_run(FiatlightGuiParams(functions_graph=functions, app_title="play_versatile_word", initial_value=poem))

    def get_poem() -> str:
        return poem

    from fiatlight.functions_graph import FunctionsGraph
    from fiatlight.fiatlight_gui import fiatlight_run, FiatlightGuiParams

    fiatlight_run(
        FunctionsGraph.from_function_composition(
            [
                get_poem,
                # remove_non_letters,
                # str_lower,
                # split_words,
                # remove_empty_words,
                # sorted,
                # run_length_encode,
                # sort_word_with_counts,
                # display_word_with_counts,
            ]
        ),
        FiatlightGuiParams(
            app_title="play_versatile_word",
            window_size=(1600, 1000),
            show_image_inspector=True,
        ),
    )


if __name__ == "__main__":
    main()
