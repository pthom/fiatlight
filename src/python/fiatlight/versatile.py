# from typing import Any, Optional, Sequence
# from imgui_bundle import imgui
# from fiatlight.any_data_with_gui import AnyDataWithGui
# from fiatlight.function_with_gui import FunctionWithGui
# from fiatlight.functions_graph import FunctionsGraph
# from fiatlight.fiatlight_types import PureFunction
# from fiatlight.data_presenters import versatile_gui_data
#
#
# class VersatileDataWithGui(AnyDataWithGui):
#     def __init__(self) -> None:
#         super().__init__()
#         self.gui_present_impl = lambda: self._gui_present_impl()
#
#     def _gui_present_impl(self) -> None:
#         imgui.push_id(str(id(self)))
#         versatile_gui_data(self.value)
#         imgui.pop_id()
#
#
# class VersatileFunctionWithGui(FunctionWithGui):
#     inner_function: PureFunction
#     inner_function_name: str
#
#     def __init__(self, function: PureFunction, function_name: Optional[str] = None):
#         self.inner_function = function
#         if function_name is not None:
#             self.inner_function_name = function_name
#         else:
#             self.inner_function_name = function.__name__
#         self.input_gui = VersatileDataWithGui()
#         self.output_gui = VersatileDataWithGui()
#         self.name = self.inner_function_name
#
#         def f(x: Any) -> Any:
#             return self.inner_function(x)
#
#         self.f_impl = f
#
#     def old_gui_params(self) -> bool:
#         return False
#
#
# def to_function_with_gui(f: Any) -> FunctionWithGui:
#     if isinstance(f, FunctionWithGui):
#         return f
#     else:
#         return VersatileFunctionWithGui(f)
#
#
# class VersatileFunctionsGraph(FunctionsGraph):
#     def __init__(self, functions: Sequence[PureFunction]) -> None:
#         functions_with_gui = [to_function_with_gui(f) for f in functions]
#         FunctionsGraph.__init__(self, functions_with_gui)
#         # super.__init__(self, functions_with_gui)
