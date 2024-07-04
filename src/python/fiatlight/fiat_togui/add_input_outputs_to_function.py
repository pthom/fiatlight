from fiatlight.fiat_types.base_types import FiatAttributes, JsonDict
from fiatlight.fiat_types.error_types import UnspecifiedValue
from fiatlight.fiat_core.any_data_with_gui import AnyDataWithGui, AnyDataWithGui_UnregisteredType
from fiatlight.fiat_core.param_with_gui import ParamWithGui, ParamKind
from fiatlight.fiat_core.function_with_gui import FunctionWithGui
from fiatlight.fiat_core.output_with_gui import OutputWithGui
from fiatlight.fiat_types import typename_utils
from .to_gui import _any_type_to_gui_impl
from .to_gui_context import TO_GUI_CONTEXT
from .function_signature import get_function_signature
import inspect
from typing import Any, Type, List


def _fn_outputs_with_gui(
    output_type: Type[Any], fn_fiat_attributes: FiatAttributes, split_if_tuple: bool
) -> List[AnyDataWithGui[Any]]:
    """Convert the return type of a function to a (list of) GUI representation."""
    from fiatlight.fiat_togui.tuple_with_gui import TupleWithGui

    output_gui = _any_type_to_gui_impl(output_type, fn_fiat_attributes)

    if not split_if_tuple or not isinstance(output_gui, TupleWithGui):
        output_fiat_attrs = get_output_fiat_attributes(fn_fiat_attributes)
        output_gui.merge_fiat_attributes(output_fiat_attrs)
        output_gui.label = "Output"
        return [output_gui]
    else:
        r = []
        for idx_output, output_gui in enumerate(output_gui._inner_guis):
            output_fiat_attrs = get_output_fiat_attributes(fn_fiat_attributes, idx_output)
            output_gui.merge_fiat_attributes(output_fiat_attrs)
            output_gui.label = f"Output {idx_output + 1}"
            r.append(output_gui)

    return r


def _to_param_with_gui(name: str, param: inspect.Parameter, fiat_attributes: FiatAttributes) -> ParamWithGui[Any]:
    """Convert a function parameter to a GUI representation."""
    type_annotation = param.annotation

    data_with_gui: AnyDataWithGui[Any]
    if type_annotation is None or type_annotation is inspect.Parameter.empty:
        data_with_gui = AnyDataWithGui_UnregisteredType[Any](
            typename_utils.fully_qualified_typename(type_annotation), None
        )
    else:
        data_with_gui = _any_type_to_gui_impl(type_annotation, fiat_attributes)

    if data_with_gui.label is None:
        data_with_gui.label = name

    param_kind = ParamKind.PositionalOrKeyword
    if param.kind is inspect.Parameter.POSITIONAL_ONLY:
        param_kind = ParamKind.PositionalOnly
    elif param.kind is inspect.Parameter.KEYWORD_ONLY:
        param_kind = ParamKind.KeywordOnly

    default_value = param.default if param.default is not inspect.Parameter.empty else UnspecifiedValue
    r = ParamWithGui(name, data_with_gui, param_kind, default_value)

    return r


def _get_input_param_fiat_attributes(fn_attributes: JsonDict, param_name: str) -> FiatAttributes:
    """Get the optional fiat attributes for the parameter.
    Those parameters are defined in the function attributes, and may be passed:

    * either by manually adding attributes some time after the function definition:
        def f(x: float):
            return x

       f.x__range = (0, 1)
       f.x__type = "slider"

    * or by using the with_fiat_attributes decorator:
       @fl.with_fiat_attributes(x__range=(0, 1), x__type="slider")
       def f(x: float):
           return x
    """
    r = FiatAttributes({})
    for k, v in fn_attributes.items():
        if k.startswith(param_name + "__"):
            r[k[len(param_name) + 2 :]] = v
    return r


def get_output_fiat_attributes(fn_attributes: JsonDict, idx_output: int = 0) -> FiatAttributes:
    """Get the optional fiat attributes for the return value.
    For example:
        @with_fiat_attributes(return__range=(0, 1))
        def f() -> float:
            return 1.0
    """
    r = FiatAttributes({})

    if idx_output == 0:
        prefix = "return__"
    else:
        prefix = f"return_{idx_output}__"
    prefix_len = len(prefix)

    for k, v in fn_attributes.items():
        if k.startswith(prefix):
            r[k[prefix_len:]] = v
    return r


def add_input_outputs_to_function(
    function_with_gui: FunctionWithGui,
    signature_string: str | None,
    fiat_attributes: FiatAttributes,
) -> None:
    """Central function that is called by FunctionWithGui.__init__ to add the inputs and outputs to the function.

    It analyzes the signature of the function, and adds the inputs and outputs to the function_with_gui.
    """

    TO_GUI_CONTEXT.enqueue_function(function_with_gui.function_name)
    f = function_with_gui._f_impl  # noqa
    assert f is not None
    try:
        signature = get_function_signature(f, signature_string=signature_string)
    except ValueError as e:
        raise ValueError(f"Failed to get the signature of the function {f.__name__}") from e

    params_signatures = signature.parameters
    for param_name, param_signature in params_signatures.items():
        param_fiat_attrs = _get_input_param_fiat_attributes(fiat_attributes, param_name)
        function_with_gui._inputs_with_gui.append(_to_param_with_gui(param_name, param_signature, param_fiat_attrs))

    return_annotation = signature.return_annotation
    if return_annotation is inspect.Parameter.empty:
        output_with_gui = AnyDataWithGui_UnregisteredType[Any]("inspect.Parameter.empty", None)
        output_with_gui.label = "Output"
        output_with_gui.merge_fiat_attributes(get_output_fiat_attributes(fiat_attributes))
        function_with_gui._outputs_with_gui.append(OutputWithGui(output_with_gui))
    else:
        if return_annotation is not None:
            outputs_guis = _fn_outputs_with_gui(return_annotation, fiat_attributes, split_if_tuple=True)
            outputs_with_gui = [OutputWithGui(outputs_gui) for outputs_gui in outputs_guis]
            function_with_gui._outputs_with_gui = outputs_with_gui
