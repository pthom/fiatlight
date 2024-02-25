from fiatlight.any_data_with_gui import AnyDataWithGui, DataType
from fiatlight.function_with_gui import FunctionWithGui, NamedDataWithGui
import inspect

from dataclasses import dataclass
from typing import TypeAlias, Callable, Type, Any


GuiEditParams: TypeAlias = Any
StandardType: TypeAlias = Any


@dataclass
class TypeToGuiInfo:
    standard_type_class: Type[Any]
    gui_type_factory: Callable[[StandardType | None, GuiEditParams | None], AnyDataWithGui[Any]]
    default_edit_params: GuiEditParams

    def is_type(self, typeclass: Type[Any] | str) -> bool:
        # in some circumstances, typeclass is a string...
        # I don't know why, must be a limitation of the type system
        if isinstance(typeclass, str):
            typeclass = eval(typeclass)
        return typeclass is self.standard_type_class


def any_typeclass_to_data_with_gui(
    typeclass: Type[DataType], default_value: DataType | None = None
) -> AnyDataWithGui[DataType]:
    from fiatlight.all_to_gui import all_type_to_gui_info

    for type_to_gui_info in all_type_to_gui_info():
        if type_to_gui_info.is_type(typeclass):
            return type_to_gui_info.gui_type_factory(default_value, type_to_gui_info.default_edit_params)
    raise ValueError(f"Type {typeclass} not supported by any_typeclass_to_data_with_gui")


def any_value_to_data_with_gui(value: DataType) -> AnyDataWithGui[DataType]:
    return any_typeclass_to_data_with_gui(type(value), value)


def any_param_to_param_with_gui(name: str, param: inspect.Parameter) -> NamedDataWithGui[Any]:
    default_value = param.default if param.default is not inspect.Parameter.empty else None
    annotation = param.annotation if param.annotation is not inspect.Parameter.empty else None

    if annotation is None:
        raise ValueError(f"Parameter {name} has no type annotation")

    as_any_data_with_gui = any_typeclass_to_data_with_gui(annotation, default_value)
    return NamedDataWithGui(name, as_any_data_with_gui)


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
        raise ValueError(f"Function {f.__name__} has no return type annotation")

    return_annotation_str = str(return_annotation)
    is_tuple = return_annotation_str.startswith("typing.Tuple") or return_annotation_str.startswith("tuple")
    if is_tuple:
        return_annotation_inner_str = return_annotation_str[return_annotation_str.index("[") + 1 : -1]
        tuple_type_annotation_strs = return_annotation_inner_str.split(", ")
        tuple_type_annotations = [eval(annotation_str) for annotation_str in tuple_type_annotation_strs]
        for i, annotation in enumerate(tuple_type_annotations):
            function_with_gui.outputs_with_gui.append(
                NamedDataWithGui(f"output_{i}", any_typeclass_to_data_with_gui(annotation))
            )
    else:
        function_with_gui.outputs_with_gui.append(
            NamedDataWithGui("output", any_typeclass_to_data_with_gui(sig.return_annotation))
        )

    return function_with_gui
