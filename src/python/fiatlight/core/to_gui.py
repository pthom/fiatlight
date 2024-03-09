from fiatlight.core import UnspecifiedValue, DataType, AnyDataGuiCallbacks
from fiatlight.core.any_data_with_gui import AnyDataWithGui
from fiatlight.core.function_with_gui import FunctionWithGui, ParamKind, ParamWithGui, OutputWithGui
from fiatlight.core import primitives_gui
from fiatlight.core.optional_gui import OptionalWithGui
from fiatlight.core.function_signature import get_function_signature

import inspect
import logging
from typing import TypeAlias, Callable, Any, Dict, Tuple


GuiFactory = Callable[[], AnyDataWithGui[DataType]]


_COMPLAINTS_MISSING_GUI_FACTORY = []


def extract_optional_typeclass(type_class_name: str) -> Tuple[bool, str]:
    if type_class_name.startswith("typing.Optional[") and type_class_name.endswith("]"):
        return True, type_class_name[16:-1]
    if type_class_name.endswith(" | None"):
        return True, type_class_name[:-7]
    return False, type_class_name


def any_typeclass_to_gui(type_class_name: str) -> AnyDataWithGui[Any]:
    if type_class_name.startswith("<class '") and type_class_name.endswith("'>"):
        type_class_name = type_class_name[8:-2]

    is_optional, type_class_name = extract_optional_typeclass(type_class_name)

    if type_class_name in ALL_GUI_FACTORIES:
        if not is_optional:
            return ALL_GUI_FACTORIES[type_class_name]()
        else:
            inner_gui = ALL_GUI_FACTORIES[type_class_name]()
            return OptionalWithGui(inner_gui)

    # if we reach this point, we have no GUI implementation for the type
    if type_class_name not in _COMPLAINTS_MISSING_GUI_FACTORY:
        logging.warning(f"Type {type_class_name} not present in ALL_GUI_FACTORIES")
        _COMPLAINTS_MISSING_GUI_FACTORY.append(type_class_name)
    return AnyDataWithGui.make_default()


def any_value_to_data_with_gui(value: DataType) -> AnyDataWithGui[DataType]:
    type_class_name = str(type(value))
    r = any_typeclass_to_gui(type_class_name)
    r.value = value
    return r


def any_param_to_param_with_gui(name: str, param: inspect.Parameter) -> ParamWithGui[Any]:
    annotation = param.annotation

    data_with_gui: AnyDataWithGui[Any]
    if annotation is None or annotation is inspect.Parameter.empty:
        data_with_gui = AnyDataWithGui.make_default()
    else:
        data_with_gui = any_typeclass_to_gui(str(annotation))

    param_kind = ParamKind.PositionalOrKeyword
    if param.kind is inspect.Parameter.POSITIONAL_ONLY:
        param_kind = ParamKind.PositionalOnly
    elif param.kind is inspect.Parameter.KEYWORD_ONLY:
        param_kind = ParamKind.KeywordOnly

    default_value = param.default if param.default is not inspect.Parameter.empty else UnspecifiedValue
    return ParamWithGui(name, data_with_gui, param_kind, default_value)


def any_function_to_function_with_gui(
    f: Callable[..., Any],
    *,
    signature_string: str | None = None,
    signatures_import_code: str | None = None,
) -> FunctionWithGui:
    """Create a FunctionWithGui from a function.

    :param f: the function for which we want to create a FunctionWithGui
    :param signature_string: a string representing the signature of the function
    :param signatures_import_code: a string representing the code to import the types used in the signature_string
    :return: a FunctionWithGui instance that wraps the function.
    """
    function_with_gui = FunctionWithGui()
    function_with_gui.name = f.__name__
    function_with_gui.f_impl = f

    try:
        sig = get_function_signature(
            f, signature_string=signature_string, signatures_import_code=signatures_import_code
        )
    except ValueError as e:
        raise ValueError(f"Failed to get the signature of the function {f.__name__}") from e

    params = sig.parameters
    for name, param in params.items():
        function_with_gui.inputs_with_gui.append(any_param_to_param_with_gui(name, param))

    return_annotation = sig.return_annotation
    if return_annotation is inspect.Parameter.empty:
        handlers_none = AnyDataGuiCallbacks[Any]()
        data_with_gui = AnyDataWithGui.from_handlers(handlers_none)
        function_with_gui.outputs_with_gui.append(OutputWithGui(data_with_gui))
    else:
        return_annotation_str = str(return_annotation)
        is_tuple = return_annotation_str.startswith("typing.Tuple") or return_annotation_str.startswith("tuple")
        if is_tuple:
            return_annotation_inner_str = return_annotation_str[return_annotation_str.index("[") + 1 : -1]
            tuple_type_annotation_strs = return_annotation_inner_str.split(", ")
            tuple_type_annotations = [eval(annotation_str) for annotation_str in tuple_type_annotation_strs]
            for i, annotation in enumerate(tuple_type_annotations):
                data_with_gui = any_typeclass_to_gui(str(annotation))
                function_with_gui.outputs_with_gui.append(OutputWithGui(data_with_gui))
        else:
            data_with_gui = any_typeclass_to_gui(str(sig.return_annotation))
            function_with_gui.outputs_with_gui.append(OutputWithGui(data_with_gui))

    return function_with_gui


# ----------------------------------------------------------------------------------------------------------------------
#       all to gui
# ----------------------------------------------------------------------------------------------------------------------
Typename: TypeAlias = str

ALL_GUI_FACTORIES: Dict[Typename, GuiFactory[Any]] = {
    "int": primitives_gui.IntWithGui,
    "float": primitives_gui.FloatWithGui,
    "str": primitives_gui.StrWithGui,
    "bool": primitives_gui.BoolWithGui,
}
