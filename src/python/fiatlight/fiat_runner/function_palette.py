from dataclasses import dataclass, field
from enum import Enum

from imgui_bundle import hello_imgui, imgui, imgui_ctx, imgui_md, ImVec2

from fiatlight.fiat_core import FunctionWithGui
from fiatlight.fiat_widgets import fontawesome_6_ctx, icons_fontawesome_6
from fiatlight.fiat_types import Function
from fiatlight.fiat_types.type_compat import is_link_compatible
from fiatlight.fiat_types.typename_utils import TypeLike

from typing import Any, Callable, Literal

FunctionWithGuiFactory = Callable[[], FunctionWithGui]
PinKind = Literal["input", "output"]


class TagMatchMode(Enum):
    """How the function palette combines a list of selected tags.

    AND: a function matches only if it carries every selected tag.
    OR:  a function matches if it carries any of the selected tags.
    """

    AND = "AND"
    OR = "OR"


@dataclass
class PaletteFilter:
    """Owned by the caller, mutated by the palette widgets each frame.

    Three filters are composed (AND/OR depending on `match_mode`):
    - `selected_tags`: which tag chips are checked.
    - `search_text`: substring tokens matched against name / tags / doc.
    - `compatibility`: when set, restrict to functions that have at least one
      pin compatible with this dragged pin (set by the drag-from-pin popup).

    `latched_fn` is the row whose docs the side panel currently shows.
    Updated each frame a row is hovered; persists across frames so the user
    can move the mouse into the doc panel and read/scroll without losing
    the active function.
    """

    selected_tags: list[str] = field(default_factory=list)
    search_text: str = ""
    match_mode: TagMatchMode = TagMatchMode.AND
    compatibility: tuple[TypeLike, PinKind] | None = None
    latched_fn: "FunctionInfo | None" = None


@dataclass
class FunctionInfo:
    name: str
    function_factory: FunctionWithGuiFactory
    tags: list[str]
    doc: str | None
    doc_is_markdown: bool
    # Cached pin types so the compatibility filter does not have to re-factor
    # every function on every popup frame. Each entry is the parameter / output
    # name and its Python type (which may be None for unannotated outputs).
    input_types: list[tuple[str, Any]] = field(default_factory=list)
    output_types: list[Any] = field(default_factory=list)

    def first_compatible_input(self, dragged_output_type: TypeLike) -> str | None:
        """Return the name of the first input whose type accepts `dragged_output_type`."""
        for name, t in self.input_types:
            if t is not None and is_link_compatible(dragged_output_type, t):
                return name
        return None

    def first_compatible_output(self, dragged_input_type: TypeLike) -> int | None:
        """Return the index of the first output whose type fits into `dragged_input_type`."""
        for idx, t in enumerate(self.output_types):
            if t is not None and is_link_compatible(t, dragged_input_type):
                return idx
        return None


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
        input_types = [
            (gui.input_of_idx(i).name, gui.input_of_idx(i).data_with_gui._type) for i in range(gui.nb_inputs())
        ]
        output_types = [gui.output(i)._type for i in range(gui.nb_outputs())]
        function_info = FunctionInfo(
            name,
            function_factory,
            tags,
            doc.user_doc,
            doc.is_user_doc_markdown,
            input_types=input_types,
            output_types=output_types,
        )
        self._functions.append(function_info)

    def get_compatible_function_infos(self, pin_type: TypeLike, pin_kind: PinKind) -> list[FunctionInfo]:
        """Return functions that have at least one pin compatible with the dragged pin.

        If the user dragged an *output* pin, we look for functions with at least one
        input that accepts `pin_type`. Symmetrically for inputs.
        """
        result: list[FunctionInfo] = []
        for fi in self._functions:
            if pin_kind == "output":
                if fi.first_compatible_input(pin_type) is not None:
                    result.append(fi)
            else:
                if fi.first_compatible_output(pin_type) is not None:
                    result.append(fi)
        return result

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
        # Saved graphs may carry duplicate-disambiguation suffixes like
        # `foo_2` when the same function appears twice. The palette only
        # knows the base name; strip a trailing `_<digits>` and retry. The
        # graph's own dedup logic will re-apply the suffix on insertion.
        import re

        base = re.sub(r"(_\d+)+$", "", name)
        if base != name:
            for function_info in self._functions:
                if function_info.name == base:
                    return function_info.function_factory()
        raise ValueError(f"Function with name {name} not found in collection")


def _search_terms(search_text: str) -> list[str]:
    import shlex

    try:
        tokens = shlex.split(search_text)
    except ValueError:
        tokens = search_text.split()
    return [t.lower() for t in tokens if t]


def _filter_fn_infos(palette: FunctionPalette, filt: PaletteFilter) -> list[FunctionInfo]:
    """Apply tag, compatibility, and search-text filters."""
    infos = palette.get_function_factories(filt.selected_tags, mode=filt.match_mode)

    if filt.compatibility is not None:
        pin_type, pin_kind = filt.compatibility
        if pin_kind == "output":
            infos = [fi for fi in infos if fi.first_compatible_input(pin_type) is not None]
        else:
            infos = [fi for fi in infos if fi.first_compatible_output(pin_type) is not None]

    terms = _search_terms(filt.search_text)
    if not terms:
        return infos

    def haystack(fi: FunctionInfo) -> str:
        parts = [fi.name, *fi.tags]
        if fi.doc is not None:
            parts.append(fi.doc)
        return "\n".join(parts).lower()

    if filt.match_mode is TagMatchMode.AND:
        return [fi for fi in infos if all(t in haystack(fi) for t in terms)]
    return [fi for fi in infos if any(t in haystack(fi) for t in terms)]


def _gui_search_and_match_mode(filt: PaletteFilter, *, focus_search: bool) -> None:
    imgui.set_next_item_width(hello_imgui.em_size(10))
    if focus_search:
        imgui.set_keyboard_focus_here()
    _, filt.search_text = imgui.input_text("Search", filt.search_text)

    imgui.text(" Match:")
    imgui.same_line()
    if imgui.radio_button("AND", filt.match_mode is TagMatchMode.AND):
        filt.match_mode = TagMatchMode.AND
    imgui.same_line()
    if imgui.radio_button("OR", filt.match_mode is TagMatchMode.OR):
        filt.match_mode = TagMatchMode.OR


def _gui_tags(palette: FunctionPalette, filt: PaletteFilter) -> None:
    all_tags = palette.tags_set()
    if not all_tags:
        return
    style = imgui.get_style()
    checkbox_extra = imgui.get_frame_height() + style.item_inner_spacing.x
    col_width = max(imgui.calc_text_size(t).x for t in all_tags) + checkbox_extra + style.item_spacing.x
    avail = imgui.get_content_region_avail().x
    n_cols = max(1, int(avail // col_width))

    for i, tag in enumerate(all_tags):
        was_selected = tag in filt.selected_tags
        _, is_selected = imgui.checkbox(tag, was_selected)
        if is_selected and not was_selected:
            filt.selected_tags.append(tag)
        elif was_selected and not is_selected:
            filt.selected_tags[:] = [t for t in filt.selected_tags if t != tag]

        col = i % n_cols
        if col + 1 < n_cols and i + 1 < len(all_tags):
            imgui.same_line(col_width * (col + 1))


def _gui_function_row(
    fn_info: FunctionInfo,
    on_pick: Callable[[FunctionInfo], None],
    *,
    row_click_picks: bool,
    is_latched: bool = False,
) -> bool:
    """Render one row.

    Returns True iff the row is hovered this frame — used by the popup body
    to drive the doc panel. (In dock mode hover state is unused; the inline
    tooltip below provides on-demand docs.)

    `is_latched` (popup mode only): render the row as `selected` so the user
    can see which row's docs are showing in the side panel.
    """
    hovered = False
    with imgui_ctx.push_obj_id(fn_info):
        if row_click_picks:
            # Whole-row clickable (popup mode); doc panel renders the doc.
            if imgui.selectable(fn_info.name, is_latched)[0]:
                on_pick(fn_info)
            hovered = imgui.is_item_hovered()
        else:
            # Name + spring + "+" button (dock mode); inline tooltip on hover.
            with imgui_ctx.begin_horizontal("H"):
                with fontawesome_6_ctx():
                    imgui.text(fn_info.name)
                    _draw_function_row_tooltip(fn_info)
                    imgui.spring()
                    if imgui.button(icons_fontawesome_6.ICON_FA_SQUARE_PLUS):
                        on_pick(fn_info)
    return hovered


def _draw_function_row_tooltip(fn_info: FunctionInfo) -> None:
    """Inline imgui-managed tooltip used by the dock-side palette."""
    if not imgui.begin_item_tooltip():
        return
    imgui.dummy(hello_imgui.em_to_vec2(40, 0))
    _render_function_doc_markdown(fn_info)
    imgui.end_tooltip()


def _render_function_doc_markdown(fn_info: FunctionInfo) -> None:
    """Render the function's documentation block (header + body) as markdown.

    Shared between the dock-side hover tooltip and the popup doc panel.
    """
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


def _gui_functions(
    palette: FunctionPalette,
    filt: PaletteFilter,
    on_pick: Callable[[FunctionInfo], None],
    *,
    row_click_picks: bool,
) -> None:
    """Render functions grouped by their primary (first) tag.

    In popup mode (`row_click_picks=True`), updates `filt.latched_fn` to
    the row currently being hovered. The latch persists across frames —
    when the user moves the mouse into the side doc panel, the previously-
    hovered function's docs stay visible, and the row stays highlighted.
    """
    infos = _filter_fn_infos(palette, filt)
    if not infos:
        imgui.text_disabled("No matching functions")
        return

    groups: dict[str, list[FunctionInfo]] = {}
    for fi in infos:
        primary = fi.tags[0] if fi.tags else "other"
        groups.setdefault(primary, []).append(fi)

    flag_default_open = int(imgui.TreeNodeFlags_.default_open)
    for primary, group in groups.items():
        header = f"{primary} ({len(group)})"
        if imgui.collapsing_header(header, flag_default_open):
            for fi in group:
                hovered = _gui_function_row(
                    fi, on_pick, row_click_picks=row_click_picks, is_latched=(filt.latched_fn is fi)
                )
                if hovered:
                    filt.latched_fn = fi


def palette_gui_body(
    palette: FunctionPalette,
    filt: PaletteFilter,
    on_pick: Callable[[FunctionInfo], None],
    *,
    row_click_picks: bool = False,
    focus_search: bool = False,
    show_doc_panel: bool = False,
    list_width_ratio: float = 0.4,
) -> None:
    """Render the full palette body (search bar, tag chips, function list)
    into the current imgui window or popup. The caller owns `filt` so its
    state persists across frames; `on_pick` receives the picked FunctionInfo.

    `row_click_picks=True` makes the whole row clickable (good for popups);
    `False` shows the "+" button next to each name (dock layout).

    `focus_search=True` (set on the first frame a popup opens) sends keyboard
    focus to the search input so the user can start typing immediately.

    `show_doc_panel=True` lays out a documentation panel to the right of
    the function list, showing the docs of the latched (last-hovered) row.
    The side layout — rather than below the list — means the user can move
    the mouse rightward into the doc panel without crossing other rows
    (which would otherwise switch the latch). Same pattern as Dear ImGui
    Explorer (code on the right, list on the left).

    `list_width_ratio` is the fraction of the popup's content width given
    to the function list; the doc panel takes the rest.
    """
    _gui_search_and_match_mode(filt, focus_search=focus_search)
    _gui_tags(palette, filt)

    if not show_doc_panel:
        _gui_functions(palette, filt, on_pick, row_click_picks=row_click_picks)
        return

    # Side-by-side: function list on the left, doc panel on the right.
    avail = imgui.get_content_region_avail()
    list_w = max(hello_imgui.em_size(15), avail.x * list_width_ratio)
    if imgui.begin_child("##palette_fn_list", ImVec2(list_w, avail.y)):
        _gui_functions(palette, filt, on_pick, row_click_picks=row_click_picks)
    imgui.end_child()
    imgui.same_line()
    _gui_doc_panel(filt.latched_fn, ImVec2(0, avail.y))


def _gui_doc_panel(fn_info: FunctionInfo | None, size: ImVec2) -> None:
    """Side documentation panel. Visually distinct from the function list
    (title strip + tinted background) so the user reads it as a separate
    section."""
    # Slightly darker bg so the panel reads as "another surface".
    style = imgui.get_style()
    base = style.color_(imgui.Col_.child_bg.value)
    tinted = (base.x * 0.6, base.y * 0.6, base.z * 0.6, max(base.w, 0.6))
    imgui.push_style_color(imgui.Col_.child_bg.value, tinted)
    flags = imgui.ChildFlags_.borders.value
    if imgui.begin_child("##palette_doc", size, child_flags=flags):
        imgui.text_disabled("Documentation")
        imgui.separator()
        if fn_info is not None:
            _render_function_doc_markdown(fn_info)
        else:
            imgui.text_disabled("Hover a function to see its documentation")
    imgui.end_child()
    imgui.pop_style_color()


class FunctionPaletteGui:
    """Persistent dock-side palette. Owns its own filter state so search/tag
    selections are remembered across frames."""

    palette: FunctionPalette
    on_add_function: Callable[[FunctionWithGui], None] | None = None
    _filter: PaletteFilter

    def __init__(self) -> None:
        self.palette = FunctionPalette()
        self._filter = PaletteFilter()

    def gui(self) -> None:
        """Render palette contents into the surrounding window. The caller
        owns the `imgui.begin/end` (typical when docked via HelloImGui)."""

        def on_pick(fi: FunctionInfo) -> None:
            if self.on_add_function is not None:
                self.on_add_function(fi.function_factory())

        palette_gui_body(self.palette, self._filter, on_pick)
