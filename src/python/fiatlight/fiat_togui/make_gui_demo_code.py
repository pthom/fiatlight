from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui
from fiatlight.fiat_togui.to_gui import fully_qualified_typename_or_str
from typing import Any


def make_gui_demo_code(gui_instance: AnyDataWithGui[Any]) -> str:
    """Returns a piece of code to test the GUI type."""
    from fiatlight.fiat_doc import code_utils

    datatype = gui_instance._type
    datatype_str = fully_qualified_typename_or_str(datatype)
    datatype_basename = datatype.__name__

    def compute_custom_attrs_code() -> str:
        possible_custom_attrs = gui_instance.possible_custom_attributes()
        if possible_custom_attrs is None:
            return ""

        example_usage = possible_custom_attrs.example_usage()
        example_usage = code_utils.indent_code(example_usage, indent_size=4)
        r = "@fiatlight.with_custom_attrs(\n"
        r += example_usage
        r += ")"
        return r

    custom_attrs_code = compute_custom_attrs_code()

    param_name = datatype_basename.lower() + "_param"

    code = f"""
    import typing
    import fiatlight

    {custom_attrs_code}
    def f({param_name}: {datatype_str}) -> {datatype_str}:
        return {param_name}

    fiatlight.fiat_run(f)
    """[1:]
    code = code_utils.unindent_code(code)
    return code
