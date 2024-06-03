import fiatlight


def str_stats(s: str) -> tuple[int, int, int]:
    """Return simple statistics about the string: number of characters, lines, and words"""
    n_chars = len(s)
    n_lines = s.count("\n") + 1
    n_words = len(s.split())
    return n_chars, n_lines, n_words


def prompt_stats(s: str) -> tuple[int, int, int]:
    """Return simple statistics about the prompt: number of characters, lines, and words"""
    n_chars = len(s)
    n_lines = s.count("\n") + 1
    n_words = len(s.split())
    return n_chars, n_lines, n_words


def main() -> None:
    from fiatlight import FunctionsGraph

    graph = FunctionsGraph()
    graph.add_function(str_stats)
    graph.add_function(prompt_stats)
    fiatlight.run(graph)


if __name__ == "__main__":
    main()
