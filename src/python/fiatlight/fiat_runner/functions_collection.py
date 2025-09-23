from dataclasses import dataclass

from imgui_bundle import hello_imgui, imgui, imgui_ctx

from fiatlight.fiat_core import FunctionWithGui
from fiatlight.fiat_widgets import fontawesome_6_ctx, icons_fontawesome_6
from fiatlight.fiat_types import Function

from typing import List, Callable, Any

FunctionWithGuiFactory = Callable[[], FunctionWithGui]


@dataclass
class FunctionInfo:
    name: str
    function_factory: FunctionWithGuiFactory
    tags: List[str]


class FunctionsCollection:
    _functions: List[FunctionInfo]

    def __init__(self) -> None:
        self._functions = []

    def add_function_list(self, fn_list: List[Any], tags: List[str]) -> None:
        import copy

        for f in fn_list:
            f_copy = copy.copy(f)
            self.add_function(f_copy, tags)

    def add_function(self, fn: Function, tags: List[str]) -> None:
        def factory() -> FunctionWithGui:
            return FunctionWithGui(fn)

        self._add_function_factory(factory, tags)

    def _add_function_factory(self, function_factory: FunctionWithGuiFactory, tags: List[str] | None) -> None:
        if tags is None:
            tags = []

        name = function_factory().function_name

        function_info = FunctionInfo(name, function_factory, tags)
        self._functions.append(function_info)

    def tags_set(self) -> List[str]:
        tags = set()
        for function_info in self._functions:
            tags.update(function_info.tags)

        tags_sorted = list(sorted(tags))
        return tags_sorted

    def get_function_factories(self, tags: List[str] | None) -> List[FunctionInfo]:
        if tags is None:
            return self._functions

        fn_factories = []
        for function_info in self._functions:
            if all(tag in function_info.tags for tag in tags):
                fn_factories.append(function_info)

        return fn_factories

    def factor_function_from_name(self, name: str) -> FunctionWithGui:
        for function_info in self._functions:
            if function_info.name == name:
                return function_info.function_factory()
        raise ValueError(f"Function with name {name} not found in collection")


class FunctionCollectionGui:
    functions_collection: FunctionsCollection
    on_add_function: Callable[[FunctionWithGui], None] | None = None

    _selected_tags: List[str]

    def __init__(self) -> None:
        self.functions_collection = FunctionsCollection()
        self._selected_tags = []

    def _gui_tags(self) -> None:
        all_tags = self.functions_collection.tags_set()
        for tag in all_tags:
            is_selected = tag in self._selected_tags
            _, is_selected = imgui.checkbox(tag, is_selected)
            if is_selected:
                self._selected_tags.append(tag)
            else:
                self._selected_tags = [t for t in self._selected_tags if t != tag]

            cursor_pos = imgui.get_cursor_pos()
            window_width = imgui.get_window_width()
            if cursor_pos.x + hello_imgui.em_size(5) < window_width:
                imgui.same_line()
        imgui.new_line()

    def _gui_functions(self) -> None:
        fn_infos = self.functions_collection.get_function_factories(self._selected_tags)
        for fn_info in fn_infos:
            with imgui_ctx.push_obj_id(fn_info):
                with imgui_ctx.begin_horizontal("H"):
                    with fontawesome_6_ctx():
                        imgui.text(fn_info.name)
                        # if imgui.is_item_hovered():  fn_info.function_factory().get_function_doc()
                        imgui.spring()
                        if imgui.button(icons_fontawesome_6.ICON_FA_SQUARE_PLUS):
                            if self.on_add_function is not None:
                                new_fn = fn_info.function_factory()
                                self.on_add_function(new_fn)

    def gui(self) -> None:
        imgui.set_next_window_size(hello_imgui.em_to_vec2(20, -1.0), imgui.Cond_.appearing)
        with imgui_ctx.begin("Functions collection"):
            with imgui_ctx.begin_vertical("V"):
                self._gui_tags()
                self._gui_functions()
