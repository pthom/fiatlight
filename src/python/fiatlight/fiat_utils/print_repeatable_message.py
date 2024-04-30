"""Prints a message on the standard output.
If repeated, re-print on the same line, with a count indication.

Note: This implementation is simple and not foolproof.
"""

from threading import Lock

# Static attributes
_last_message = ""
_count = 0
_lock = Lock()


def _do_print(msg: str, count: int) -> None:
    global _last_message
    if _count > 1:
        print(f"\r({count}) {msg}", end="")
    else:
        print(f"\r{msg}", end="")
    _last_message = msg


def _do_new_line() -> None:
    print("")


def print_repeatable_message(msg: str) -> None:
    global _last_message, _count

    with _lock:
        if msg == _last_message:
            _count += 1
            _do_print(msg, _count)
        else:
            if len(_last_message) > 0:
                _do_print(_last_message, _count)
                _do_new_line()
            _count = 1
            _do_print(msg, _count)


def sandbox() -> None:
    """Example usage of the print_repeatable_message function."""
    import time

    print_repeatable_message("Starting the sandbox...")
    for i in range(2):
        print_repeatable_message("Message")
        time.sleep(0.1)
    print_repeatable_message("\nEnd of the sandbox.")


if __name__ == "__main__":
    sandbox()
