from IPython import display
from IPython.core.magic import register_line_magic


@register_line_magic  # type: ignore
def look_at_python_code(_magic_args: str) -> display.Code:
    """Display the Python code of a function or class in a notebook cell."""
    import inspect
    import fiatlight  # noqa

    obj = eval(_magic_args)
    r = display.Code(inspect.getsource(obj), language="python")  # type: ignore
    return r
