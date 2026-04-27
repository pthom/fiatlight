from dataclasses import dataclass
from enum import Enum

from imgui_bundle import hello_imgui, imgui, imgui_ctx, imgui_md

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
    doc: str | None
    doc_is_markdown: bool


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


class FunctionPalette:
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
        gui = function_factory()
        name = gui.function_name
        doc = gui.get_function_doc()
        function_info = FunctionInfo(name, function_factory, tags, doc.user_doc, doc.is_user_doc_markdown)
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


class FunctionPaletteGui:
    palette: FunctionPalette
    on_add_function: Callable[[FunctionWithGui], None] | None = None

    _selected_tags: list[str]
    _search_text: str
    _match_mode: TagMatchMode

    def __init__(self) -> None:
        self.palette = FunctionPalette()
        self._selected_tags = []
        self._search_text = ""
        self._match_mode = TagMatchMode.AND

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def _search_terms(self) -> list[str]:
        import shlex

        try:
            tokens = shlex.split(self._search_text)
        except ValueError:
            tokens = self._search_text.split()
        return [t.lower() for t in tokens if t]

    def _filter_fn_infos(self) -> list[FunctionInfo]:
        """Apply tag filter and search-text filter, both under the current AND/OR mode."""
        infos = self.palette.get_function_factories(self._selected_tags, mode=self._match_mode)
        terms = self._search_terms()
        if not terms:
            return infos

        def haystack(fi: FunctionInfo) -> str:
            parts = [fi.name, *fi.tags]
            if fi.doc is not None:
                parts.append(fi.doc)
            return "\n".join(parts).lower()

        if self._match_mode is TagMatchMode.AND:
            return [fi for fi in infos if all(t in haystack(fi) for t in terms)]
        return [fi for fi in infos if any(t in haystack(fi) for t in terms)]

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def _gui_search_and_match_mode(self) -> None:
        imgui.set_next_item_width(hello_imgui.em_size(10))
        _, self._search_text = imgui.input_text("Search", self._search_text)

        imgui.same_line()
        imgui.text(" Match:")
        imgui.same_line()
        if imgui.radio_button("AND", self._match_mode is TagMatchMode.AND):
            self._match_mode = TagMatchMode.AND
        imgui.same_line()
        if imgui.radio_button("OR", self._match_mode is TagMatchMode.OR):
            self._match_mode = TagMatchMode.OR

    def _gui_tags(self) -> None:
        all_tags = self.palette.tags_set()
        if not all_tags:
            return
        style = imgui.get_style()
        checkbox_extra = imgui.get_frame_height() + style.item_inner_spacing.x
        col_width = max(imgui.calc_text_size(t).x for t in all_tags) + checkbox_extra + style.item_spacing.x
        avail = imgui.get_content_region_avail().x
        n_cols = max(1, int(avail // col_width))

        for i, tag in enumerate(all_tags):
            was_selected = tag in self._selected_tags
            _, is_selected = imgui.checkbox(tag, was_selected)
            if is_selected and not was_selected:
                self._selected_tags.append(tag)
            elif was_selected and not is_selected:
                self._selected_tags = [t for t in self._selected_tags if t != tag]

            col = i % n_cols
            if col + 1 < n_cols and i + 1 < len(all_tags):
                imgui.same_line(col_width * (col + 1))

    def _gui_function_row(self, fn_info: FunctionInfo) -> None:
        with imgui_ctx.push_obj_id(fn_info):
            with imgui_ctx.begin_horizontal("H"):
                with fontawesome_6_ctx():
                    imgui.text(fn_info.name)
                    if imgui.is_item_hovered():
                        if imgui.begin_item_tooltip():
                            imgui.dummy(hello_imgui.em_to_vec2(40, 0))
                            md_str = f"""
                            ## {fn_info.name}

                            Tags: {', '.join(fn_info.tags) if fn_info.tags else 'none'}

                            ---
                            """
                            imgui_md.render_unindented(md_str)

                            if fn_info.doc is not None:
                                if fn_info.doc_is_markdown:
                                    imgui_md.render_unindented(fn_info.doc)
                                else:
                                    imgui.text_wrapped(fn_info.doc)

                            imgui.end_tooltip()
                    imgui.spring()
                    if imgui.button(icons_fontawesome_6.ICON_FA_SQUARE_PLUS):
                        if self.on_add_function is not None:
                            new_fn = fn_info.function_factory()
                            self.on_add_function(new_fn)

    def _gui_functions(self) -> None:
        """Render functions grouped by their primary (first) tag."""
        infos = self._filter_fn_infos()

        # Preserve registration order for groups.
        groups: dict[str, list[FunctionInfo]] = {}
        for fi in infos:
            primary = fi.tags[0] if fi.tags else "other"
            groups.setdefault(primary, []).append(fi)

        flag_default_open = int(imgui.TreeNodeFlags_.default_open)
        for primary, group in groups.items():
            header = f"{primary} ({len(group)})"
            if imgui.collapsing_header(header, flag_default_open):
                for fi in group:
                    self._gui_function_row(fi)

    def gui(self) -> None:
        imgui.set_next_window_size(hello_imgui.em_to_vec2(25, -1.0), imgui.Cond_.appearing)
        with imgui_ctx.begin("Function palette"):
            with imgui_ctx.begin_vertical("V"):
                self._gui_search_and_match_mode()
                self._gui_tags()
                self._gui_functions()
