# from fiatlight.any_data_with_gui import AnyDataWithGui
# from fiatlight.data_presenters import (
#     make_int_with_gui, make_str_with_gui, make_bool_with_gui, make_float_with_gui,
#     IntEditParams, StrEditParams, BoolEditParams, FloatEditParams
# )
# from typing import Any, Dict, Type, Generic, TypeVar, Callable, Optional, TypeAlias
# from dataclasses import dataclass


########################################################################################################################
#                               Any dispatcher
########################################################################################################################
# def make_any_with_gui(initial_value: Any, label: str = "##any") -> AnyDataWithGui:
#     if isinstance(initial_value, int):
#         return make_int_with_gui(initial_value, IntEditParams(label=label))
#     elif isinstance(initial_value, float):
#         return make_float_with_gui(initial_value, FloatEditParams(label=label))
#     elif isinstance(initial_value, str):
#         return make_str_with_gui(initial_value, StrEditParams(label=label))
#     elif isinstance(initial_value, bool):
#         return make_bool_with_gui(initial_value, BoolEditParams(label=label))
#     else:
#         raise ValueError(f"Unsupported type: {type(initial_value)}")


# A dict from any type to its equivalent AnyDataWithGui

# StandardType = TypeVar("StandardType")
# GuiType = TypeVar("GuiType", bound=AnyDataWithGui)
# GuiTypeFactoryParams = TypeVar("GuiTypeFactoryParams", bound=AnyDataWithGui)
#
#
# GuiTypeFactory: TypeAlias = Callable[[StandardType, GuiTypeFactoryParams], AnyDataWithGui]
#
#
# @dataclass
# class TypeToGuiInfo(Generic[StandardType, GuiType]):
#     standard_type: StandardType
#     gui_type_factory: GuiTypeFactory
#     gui_type_factory_params: GuiTypeFactoryParams
#
#
# ALL_TYPE_TO_GUI_PAIRS = [
#     TypeToGuiInfo(int, make_int_with_gui, IntEditParams()),
#
# ]
#
#
# def all_data_with_gui_factories() -> Dict[Type, GuiTypeFactory[Any, Any]]:
#     return {
#         int : make_int_with_gui,
#         float: make_float_with_gui,
#         str: make_str_with_gui,
#         bool: make_bool_with_gui
#     }
#
#
# a = all_data_with_gui_factories()
# print(a)
