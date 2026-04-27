from dataclasses import dataclass
from enum import Enum

from imgui_bundle import hello_imgui, imgui, imgui_ctx

from fiatlight.fiat_core import FunctionWithGui
from fiatlight.fiat_widgets import fontawesome_6_ctx, icons_fontawesome_6
from fiatlight.fiat_types import Function

from typing import Callable

FunctionWithGuiFactory = Callable[[], FunctionWithGui]


class TagMatchMode(Enum):
    """How the function palette combines a list of selected tags.

    AND: a function matches only if it carries every selected tag.
    OR:  a function matches if it carries any of the selected tags.
    """

    AND = "AND"
    OR = "OR"


@dataclass
class FunctionInfo:
    name: str
    function_factory: FunctionWithGuiFactory
    tags: list[str]


def _read_fiat_tags(fn: Function) -> list[str]:
    """Read `fn.fiat_tags`. Raise if missing or empty.

    Tags are the single source of truth — they must live on the function so
    that the same wrapper carries the same intent everywhere it is registered.
    Set them via `@fl.with_fiat_attributes(fiat_tags=[...])` at definition
    time, or via `fl.add_fiat_attributes(fn, fiat_tags=[...])` for shimmed
    or imported functions.
    """
    tags = getattr(fn, "fiat_tags", None)
    if not tags:
        name = getattr(fn, "__name__", repr(fn))
        raise ValueError(
            f"Function {name!r} has no `fiat_tags`. "
            "Set them via `@fl.with_fiat_attributes(fiat_tags=[...])` at "
            f"the function definition, or `fl.add_fiat_attributes({name}, "
            "fiat_tags=[...])` for imported / shimmed functions."
        )
    return list(tags)


class FunctionsCollection:
    _functions: list[FunctionInfo]

    def __init__(self) -> None:
        self._functions = []

    def add_function_list(self, fn_list: list[Function]) -> None:
        import copy

        for f in fn_list:
            f_copy = copy.copy(f)
            self.add_function(f_copy)

    def add_function(self, fn: Function) -> None:
        tags = _read_fiat_tags(fn)

        def factory() -> FunctionWithGui:
            return FunctionWithGui(fn)

        self._add_function_factory(factory, tags)

    def _add_function_factory(self, function_factory: FunctionWithGuiFactory, tags: list[str]) -> None:
        name = function_factory().function_name
        function_info = FunctionInfo(name, function_factory, tags)
        self._functions.append(function_info)

    def tags_set(self) -> list[str]:
        tags: set[str] = set()
        for function_info in self._functions:
            tags.update(function_info.tags)
        return sorted(tags)

    def get_function_factories(
        self,
        tags: list[str] | None,
        mode: TagMatchMode = TagMatchMode.AND,
    ) -> list[FunctionInfo]:
        """Return functions whose tags match `tags` under the given match mode.

        With `TagMatchMode.AND` (default), a function is included only if it
        carries every selected tag. With `TagMatchMode.OR`, a function is
        included if it carries any of the selected tags.
        """
        if not tags:
            return list(self._functions)

        if mode is TagMatchMode.AND:
            return [fi for fi in self._functions if all(tag in fi.tags for tag in tags)]
        if mode is TagMatchMode.OR:
            return [fi for fi in self._functions if any(tag in fi.tags for tag in tags)]
        raise ValueError(f"Unknown TagMatchMode: {mode!r}")

    def factor_function_from_name(self, name: str) -> FunctionWithGui:
        for function_info in self._functions:
            if function_info.name == name:
                return function_info.function_factory()
        raise ValueError(f"Function with name {name} not found in collection")


class FunctionCollectionGui:
    functions_collection: FunctionsCollection
    on_add_function: Callable[[FunctionWithGui], None] | None = None

    _selected_tags: list[str]

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
