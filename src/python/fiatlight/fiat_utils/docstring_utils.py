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
