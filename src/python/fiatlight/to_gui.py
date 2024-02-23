from fiatlight.any_data_with_gui import AnyDataWithGui
from fiatlight.function_with_gui import FunctionWithGui, FunctionParameterWithGui
from fiatlight.data_presenters import (
    make_int_with_gui,
    make_str_with_gui,
    make_bool_with_gui,
    make_float_with_gui,
    IntEditParams,
    StrEditParams,
    BoolEditParams,
    FloatEditParams,
    NoDataPresentParams,
)
import inspect

from dataclasses import dataclass
from typing import TypeAlias, Callable, List, Type, Any


GuiEditParams: TypeAlias = Any
GuiPresentParams: TypeAlias = Any
StandardType: TypeAlias = Any


@dataclass
class TypeToGuiInfo:
    standard_type_class: Type[Any]
    standard_type_name: str
    gui_type_factory: Callable[[StandardType | None, GuiEditParams | None, GuiPresentParams | None], AnyDataWithGui]
    default_edit_params: GuiEditParams
    default_present_params: GuiEditParams

    def is_type(self, typeclass: Type[Any] | str) -> bool:
        # in some circumstances, typeclass is a string... I don't know why, must be a limitation of the type system
        if isinstance(typeclass, str):
            return typeclass == self.standard_type_name
        return typeclass is self.standard_type_class


ALL_TYPE_TO_GUI_INFO: List[TypeToGuiInfo] = [
    TypeToGuiInfo(int, "int", make_int_with_gui, IntEditParams(), NoDataPresentParams()),
    TypeToGuiInfo(float, "float", make_float_with_gui, FloatEditParams(), NoDataPresentParams()),
    TypeToGuiInfo(str, "str", make_str_with_gui, StrEditParams(), NoDataPresentParams()),
    TypeToGuiInfo(bool, "bool", make_bool_with_gui, BoolEditParams(), NoDataPresentParams()),
]


def any_typeclass_to_data_with_gui(typeclass: Type[Any], default_value: Any | None = None) -> AnyDataWithGui:
    for type_to_gui_info in ALL_TYPE_TO_GUI_INFO:
        if type_to_gui_info.is_type(typeclass):
            return type_to_gui_info.gui_type_factory(
                default_value, type_to_gui_info.default_edit_params, type_to_gui_info.default_present_params
            )
    raise ValueError(f"Type {typeclass} not supported by any_typeclass_to_data_with_gui")


def any_value_to_data_with_gui(value: Any) -> AnyDataWithGui:
    return any_typeclass_to_data_with_gui(type(value), value)


def any_param_to_param_with_gui(name: str, param: inspect.Parameter) -> FunctionParameterWithGui:
    default_value = param.default if param.default is not inspect.Parameter.empty else None
    annotation = param.annotation if param.annotation is not inspect.Parameter.empty else None

    if annotation is None:
        raise ValueError(f"Parameter {name} has no type annotation")

    as_any_data_with_gui = any_typeclass_to_data_with_gui(annotation, default_value)
    return FunctionParameterWithGui(name, as_any_data_with_gui)


def any_function_to_function_with_gui(f: Callable[..., Any]) -> FunctionWithGui:
    function_with_gui = FunctionWithGui()
    function_with_gui.name = f.__name__
    function_with_gui.f_impl = f

    sig = inspect.signature(f)
    params = sig.parameters
    for name, param in params.items():
        print(f"Name: {name}")
        print(f"Default: {param.default}")
        print(f"Annotation: {param.annotation}")
        print("-----")

        function_with_gui.inputs_with_gui.append(any_param_to_param_with_gui(name, param))

    return_annotation = sig.return_annotation
    if return_annotation is inspect.Parameter.empty:
        raise ValueError(f"Function {f.__name__} has no return type annotation")

    if isinstance(return_annotation, tuple):
        for i, item_annotation in enumerate(return_annotation):
            if item_annotation is inspect.Parameter.empty:
                raise ValueError(f"Function {f.__name__} has no return type annotation for item {i}")
            function_with_gui.outputs_with_gui.append(
                FunctionParameterWithGui(f"output_{i}", any_typeclass_to_data_with_gui(item_annotation))
            )
    else:
        function_with_gui.outputs_with_gui.append(
            FunctionParameterWithGui("output", any_typeclass_to_data_with_gui(sig.return_annotation))
        )

    return function_with_gui


def add(x: int, y: int = 2) -> (int, int):
    return x + y, x * y
