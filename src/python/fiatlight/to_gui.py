from fiatlight.fiatlight_types import UnspecifiedValue
from fiatlight.any_data_with_gui import (
    AnyDataGuiHandlers,
    AnyDataWithGui,
    DataType,
    OutputWithGui,
    ParamKind,
    ParamWithGui,
)
from fiatlight.function_with_gui import FunctionWithGui
from fiatlight.standard_gui_handlers import make_list_gui_handlers
import inspect

from dataclasses import dataclass
from typing import TypeAlias, Callable, Type, Any


GuiEditParams: TypeAlias = Any
StandardType: TypeAlias = Any


@dataclass
class TypeToGuiHandlers:
    standard_type_class: Type[Any]
    gui_type_factory: Callable[[GuiEditParams | None], AnyDataGuiHandlers[Any]]
    default_edit_params: GuiEditParams


def any_typeclass_to_data_handlers(typeclass_or_str: Type[DataType] | str) -> AnyDataGuiHandlers[DataType]:
    from fiatlight.all_to_gui import all_type_to_gui_info

    # in some circumstances, typeclass is a string...I don't know why, must be a limitation of the type system
    typeclass: Type[DataType]
    typeclass = eval(typeclass_or_str) if isinstance(typeclass_or_str, str) else typeclass_or_str

    typeclass_str = str(typeclass)
    is_list = typeclass_str.startswith("typing.List") or typeclass_str.startswith("list")
    if is_list:
        list_type_str = typeclass_str[typeclass_str.index("[") + 1 : -1]
        list_type = eval(list_type_str)
        item_handlers = any_typeclass_to_data_handlers(list_type)  # type: ignore
        list_handlers = make_list_gui_handlers(item_handlers)
        return list_handlers  # type: ignore
    else:
        for type_to_gui_info in all_type_to_gui_info():
            if typeclass is type_to_gui_info.standard_type_class:
                return type_to_gui_info.gui_type_factory(type_to_gui_info.default_edit_params)
        raise ValueError(f"Type {typeclass} not supported by any_typeclass_to_data_with_gui")


def any_value_to_data_with_gui(value: DataType) -> AnyDataWithGui[DataType]:
    handlers = any_typeclass_to_data_handlers(type(value))
    return AnyDataWithGui(value, handlers)


def any_param_to_param_with_gui(name: str, param: inspect.Parameter) -> ParamWithGui[Any]:
    default_value = param.default if param.default is not inspect.Parameter.empty else UnspecifiedValue
    annotation = param.annotation

    handlers: AnyDataGuiHandlers[Any]
    if annotation is None or annotation is inspect.Parameter.empty:
        handlers = AnyDataGuiHandlers[Any]()
    else:
        handlers = any_typeclass_to_data_handlers(annotation)

    data_with_gui = AnyDataWithGui(default_value, handlers)

    param_kind = ParamKind.PositionalOrKeyword
    if param.kind is inspect.Parameter.POSITIONAL_ONLY:
        param_kind = ParamKind.PositionalOnly
    elif param.kind is inspect.Parameter.KEYWORD_ONLY:
        param_kind = ParamKind.KeywordOnly
    return ParamWithGui(name, data_with_gui, param_kind)


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
                handlers: AnyDataGuiHandlers[Any] = any_typeclass_to_data_handlers(annotation)
                data_with_gui = AnyDataWithGui(UnspecifiedValue, handlers)
                function_with_gui.outputs_with_gui.append(OutputWithGui(data_with_gui))
        else:
            handlers = any_typeclass_to_data_handlers(sig.return_annotation)
            data_with_gui = AnyDataWithGui(UnspecifiedValue, handlers)
            function_with_gui.outputs_with_gui.append(OutputWithGui(data_with_gui))

    return function_with_gui
