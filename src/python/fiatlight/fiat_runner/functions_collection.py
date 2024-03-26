from dataclasses import dataclass

from imgui_bundle import hello_imgui, imgui, imgui_ctx

from fiatlight.fiat_core import FunctionWithGui

from typing import List, Callable


@dataclass
class FunctionInfo:
    tags: List[str]
    function: FunctionWithGui


class FunctionsCollection:
    _functions: List[FunctionInfo]

    def __init__(self) -> None:
        self._functions = []

    def add_function(self, function: FunctionWithGui, tags: List[str] | None) -> None:
        self._functions.append(FunctionInfo(tags or [], function))

    def tags_set(self) -> List[str]:
        tags = set()
        for function_info in self._functions:
            tags.update(function_info.tags)

        tags_sorted = list(sorted(tags))
        return tags_sorted

    def get_functions(self, tags: List[str] | None) -> List[FunctionWithGui]:
        if tags is None:
            return [function_info.function for function_info in self._functions]

        functions = []
        for function_info in self._functions:
            if all(tag in function_info.tags for tag in tags):
                functions.append(function_info.function)

        return functions


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
        functions = self.functions_collection.get_functions(self._selected_tags)
        for function in functions:
            with imgui_ctx.push_obj_id(function):
                imgui.text(function.name)
                imgui.same_line()
                if imgui.button("Add"):
                    if self.on_add_function is not None:
                        self.on_add_function(function)

    def gui(self) -> None:
        imgui.begin("Functions collection")
        self._gui_tags()
        self._gui_functions()
        imgui.end()
