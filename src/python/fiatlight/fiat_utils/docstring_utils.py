def docstring_first_line(o: object) -> str | None:
    """Return the first line of the docstring, if available"""
    if not hasattr(o, "__doc__"):
        return None
    if o.__doc__ is None:
        return None
    first_line = o.__doc__.split("\n")[0]
    first_line = first_line.strip()
    if len(first_line) == 0:
        return None
    return first_line


def unindent_docstring(docstring: str) -> str:
    if len(docstring) <= 1:
        return docstring

    # if the docstring has more than one line
    # the first line is the title, it is not indented,
    # but the rest of the lines are indented
    lines = docstring.splitlines()
    first_line = lines[0]
    rest_lines = "\n".join(lines[1:])

    from fiatlight.fiat_doc import code_utils

    rest_lines = code_utils.unindent_code(rest_lines, flag_strip_empty_lines=False)

    r = first_line + "\n" + rest_lines
    return r


def test_unindent_docstring() -> None:
    def f() -> None:
        """This is a docstring
        that is indented
        """
        pass

    docstring = f.__doc__
    if docstring is None:
        return None
    r = unindent_docstring(docstring)
    assert r == "This is a docstring\nthat is indented\n"
