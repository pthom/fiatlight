from IPython import display
from IPython.core.magic import register_line_magic


@register_line_magic  # type: ignore
def run_bash_command(_magic_args: str) -> display.Code:
    """Run a bash command and display the output in a notebook cell."""
    import subprocess

    result = subprocess.run(_magic_args, shell=True, capture_output=True)
    r = display.Code(result.stdout.decode(), language="bash")  # type: ignore
    return r


@register_line_magic  # type: ignore
def look_at_python_file(_magic_args: str) -> display.Code:
    """Display the Python code of a file in a notebook cell."""
    import fiatlight

    full_path = fiatlight.fiatlight_dir() + "/" + _magic_args
    with open(full_path) as f:
        code = f.read()
    r = display.Code(code, language="python")  # type: ignore
    return r


@register_line_magic  # type: ignore
def look_at_python_code(_magic_args: str) -> display.Code:
    """Display the Python code of a function or class in a notebook cell."""
    import inspect
    import fiatlight  # noqa

    obj = eval(_magic_args)
    r = display.Code(inspect.getsource(obj), language="python")  # type: ignore
    return r


@register_line_magic  # type: ignore
def look_at_class_header(_magic_args: str) -> display.Code:
    """Display the header of a class in a notebook cell, i.e. the class definition without method bodies."""
    from fiatlight.fiat_doc.make_class_header import make_class_header
    import fiatlight  # noqa

    args = _magic_args.split()
    class_name = args[0]
    class_ = eval(class_name)

    header = make_class_header(class_)
    r = display.Code(header, language="python")  # type: ignore
    return r
