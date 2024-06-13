import copy

from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui
from fiatlight.fiat_togui.to_gui import fully_qualified_typename_or_str
from typing import Any


def make_gui_demo_code(gui_instance: AnyDataWithGui[Any]) -> str:
    """Returns a piece of code to test the GUI type."""
    from fiatlight.fiat_doc import code_utils

    datatype = gui_instance._type
    datatype_str = fully_qualified_typename_or_str(datatype)
    datatype_basename = datatype.__name__

    param_name = datatype_basename.lower() + "_param"

    def compute_fiat_attrs_code() -> str:
        possible_fiat_attrs, generic_fiat_attributes = gui_instance.possible_fiat_attributes_with_generic()
        if possible_fiat_attrs is None:
            possible_plus_generic = generic_fiat_attributes
        else:
            possible_plus_generic = copy.deepcopy(possible_fiat_attrs)
            possible_plus_generic.merge_attributes(generic_fiat_attributes)

        example_usage = possible_plus_generic.example_usage(param_name)
        example_usage = code_utils.indent_code(example_usage, indent_size=4)
        r = "@fiatlight.with_fiat_attributes(\n"
        r += example_usage
        r += ")"
        return r

    fiat_attrs_code = compute_fiat_attrs_code()

    code = f"""
    import typing
    import fiatlight

    {fiat_attrs_code}
    def f({param_name}: {datatype_str}) -> {datatype_str}:
        return {param_name}

    fiatlight.run(f)
    """[1:]
    code = code_utils.unindent_code(code)
    return code
