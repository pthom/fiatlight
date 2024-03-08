from fiatlight.core import UnspecifiedValue, DataType, AnyDataGuiHandlers
from fiatlight.core.any_data_with_gui import AnyDataWithGui
from fiatlight.core.function_with_gui import FunctionWithGui, ParamKind, ParamWithGui, OutputWithGui
from fiatlight.core import standard_gui_handlers

import inspect
import logging
from typing import TypeAlias, Callable, Any, Dict


GuiHandlersFactory = Callable[[], AnyDataGuiHandlers[DataType]]


def any_typeclass_to_data_handlers(type_class_name: str) -> AnyDataGuiHandlers[Any]:
    if type_class_name.startswith("<class '") and type_class_name.endswith("'>"):
        type_class_name = type_class_name[8:-2]

    is_list = type_class_name.startswith("typing.List") or type_class_name.startswith("list")
    if is_list:
        list_type_str = type_class_name[type_class_name.index("[") + 1 : -1]
        item_handlers = any_typeclass_to_data_handlers(list_type_str)
        list_handlers = standard_gui_handlers.make_list_gui_handlers(item_handlers)
        return list_handlers
    else:
        if type_class_name in ALL_GUI_HANDLERS_FACTORIES:
            return ALL_GUI_HANDLERS_FACTORIES[type_class_name]()
        # if we reach this point, we have no GUI implementation for the type
        logging.warning(f"Type {type_class_name} not supported by any_typeclass_to_data_with_gui")
        return AnyDataGuiHandlers()


def any_value_to_data_with_gui(value: DataType) -> AnyDataWithGui[DataType]:
    type_class_name = str(type(value))
    handlers: AnyDataGuiHandlers[DataType] = any_typeclass_to_data_handlers(type_class_name)
    return AnyDataWithGui(value, handlers)


def any_param_to_param_with_gui(name: str, param: inspect.Parameter) -> ParamWithGui[Any]:
    annotation = param.annotation

    handlers: AnyDataGuiHandlers[Any]
    if annotation is None or annotation is inspect.Parameter.empty:
        handlers = AnyDataGuiHandlers[Any]()
    else:
        handlers = any_typeclass_to_data_handlers(str(annotation))

    data_with_gui = AnyDataWithGui(UnspecifiedValue, handlers)

    param_kind = ParamKind.PositionalOrKeyword
    if param.kind is inspect.Parameter.POSITIONAL_ONLY:
        param_kind = ParamKind.PositionalOnly
    elif param.kind is inspect.Parameter.KEYWORD_ONLY:
        param_kind = ParamKind.KeywordOnly

    default_value = param.default if param.default is not inspect.Parameter.empty else UnspecifiedValue
    return ParamWithGui(name, data_with_gui, param_kind, default_value)


def any_function_to_function_with_gui(f: Callable[..., Any]) -> FunctionWithGui:
    function_with_gui = FunctionWithGui()
    function_with_gui.name = f.__name__
    function_with_gui.f_impl = f

    try:
        sig = inspect.signature(f)
    except ValueError as e:
        raise ValueError(f"Function {f.__name__} has no type annotations") from e
    params = sig.parameters
    for name, param in params.items():
        function_with_gui.inputs_with_gui.append(any_param_to_param_with_gui(name, param))

    return_annotation = sig.return_annotation
    if return_annotation is inspect.Parameter.empty:
        handlers_none = AnyDataGuiHandlers[Any]()
        data_with_gui = AnyDataWithGui(UnspecifiedValue, handlers_none)
        function_with_gui.outputs_with_gui.append(OutputWithGui(data_with_gui))
    else:
        return_annotation_str = str(return_annotation)
        is_tuple = return_annotation_str.startswith("typing.Tuple") or return_annotation_str.startswith("tuple")
        if is_tuple:
            return_annotation_inner_str = return_annotation_str[return_annotation_str.index("[") + 1 : -1]
            tuple_type_annotation_strs = return_annotation_inner_str.split(", ")
            tuple_type_annotations = [eval(annotation_str) for annotation_str in tuple_type_annotation_strs]
            for i, annotation in enumerate(tuple_type_annotations):
                handlers: AnyDataGuiHandlers[Any] = any_typeclass_to_data_handlers(str(annotation))
                data_with_gui = AnyDataWithGui(UnspecifiedValue, handlers)
                function_with_gui.outputs_with_gui.append(OutputWithGui(data_with_gui))
        else:
            handlers = any_typeclass_to_data_handlers(str(sig.return_annotation))
            data_with_gui = AnyDataWithGui(UnspecifiedValue, handlers)
            function_with_gui.outputs_with_gui.append(OutputWithGui(data_with_gui))

    return function_with_gui


# ----------------------------------------------------------------------------------------------------------------------
#       all to gui
# ----------------------------------------------------------------------------------------------------------------------
Typename: TypeAlias = str

ALL_GUI_HANDLERS_FACTORIES: Dict[Typename, GuiHandlersFactory[Any]] = {
    "int": standard_gui_handlers.make_int_gui_handlers,
    "float": standard_gui_handlers.make_float_gui_handlers,
    "str": standard_gui_handlers.make_str_gui_handlers,
    "bool": standard_gui_handlers.make_bool_gui_handlers,
    # "List[str]": make_bool_gui_handlers,
    # "List[bool]": make_bool_gui_handlers,
}
