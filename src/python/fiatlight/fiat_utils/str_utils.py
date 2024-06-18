def text_wrap_preserve_eol(text: str, width: int = 60, replace_whitespace: bool = True) -> str:
    from textwrap import wrap

    original_lines = text.splitlines()
    final_lines = []

    for original_line in original_lines:
        if len(original_line) > width:
            final_lines += wrap(original_line, width=width, replace_whitespace=replace_whitespace)
        else:
            final_lines.append(original_line)

    r = "\n".join(final_lines)
    return r


def test_wrap_preserve_eol() -> None:
    text = """The maximum length of wrapped lines. As long as there are...
line2
line3
"""
    r = text_wrap_preserve_eol(text, width=30)
    assert (
        r
        == """The maximum length of wrapped
lines. As long as there are...
line2
line3"""
    )

    # Test 2, with replace_whitespace=False
    text = """The maximum length of wrapped lines. As long as there are...
    * line2
    * line3
"""
    r = text_wrap_preserve_eol(text, width=30, replace_whitespace=False)
    assert (
        r
        == """The maximum length of wrapped
lines. As long as there are...
    * line2
    * line3"""
    )


def memory_readable_str(nb_bytes: int) -> str:
    """Display the number of bytes in a human-readable format."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if nb_bytes < 1024.0:
            return f"{nb_bytes:.2f} {unit}"
        nb_bytes /= 1024.0
    return f"{nb_bytes:.2f} PB"
