"""Function palette popup body. Render only — caller owns begin/end of the
host imgui window or popup, plus the lifetime of the `PaletteFilter`."""

from imgui_bundle import hello_imgui, imgui, imgui_ctx, imgui_md, ImVec2

from fiatlight.fiat_palette.palette import FunctionInfo, FunctionPalette, PaletteFilter, TagMatchMode

from typing import Callable


def palette_gui_body(
    palette: FunctionPalette,
    filt: PaletteFilter,
    on_pick: Callable[[FunctionInfo], None],
    *,
    focus_search: bool = False,
) -> None:
    """Render search bar + tag chips + grouped function list + side doc panel.

    `on_pick(fi)` is called when the user clicks a row.
    `focus_search=True` (set on the first frame the popup opens) sends
    keyboard focus to the search input so the user can start typing.
    """
    _gui_filter_header(palette, filt, focus_search=focus_search)

    # Side-by-side: function list on the left, doc panel on the right.
    # The side layout (rather than below the list) lets the user move the
    # mouse rightward into the doc panel without crossing other rows
    # (which would otherwise switch the latched function).
    avail = imgui.get_content_region_avail()
    list_w = max(hello_imgui.em_size(15), avail.x * 0.4)
    if imgui.begin_child("##palette_fn_list", ImVec2(list_w, avail.y)):
        _gui_functions(palette, filt, on_pick)
    imgui.end_child()
    imgui.same_line()
    _gui_doc_panel(filt.latched_fn, ImVec2(0, avail.y))


def _cell_label(text: str) -> None:
    """Left-column label, vertically centered against the controls in the next
    column."""
    imgui.align_text_to_frame_padding()
    imgui.text(text)


def _check_item_width(label: str) -> float:
    """Approximate width of a checkbox / radio button with `label`."""
    style = imgui.get_style()
    return imgui.get_frame_height() + style.item_inner_spacing.x + imgui.calc_text_size(label).x


def _row_right_edge() -> float:
    """Absolute x of the content region's right edge. Capture once at the start
    of a flowing row (it stays constant while items are added)."""
    return imgui.get_cursor_screen_pos().x + imgui.get_content_region_avail().x


def _flow_to_next(next_label: str, right_edge: float) -> None:
    """Call between flowing-row items: stay on the same line if the next
    checkbox / radio (`next_label`) still fits before `right_edge`, otherwise let
    it wrap to a new line. Avoids the horizontal overflow a bare `same_line()`
    would cause when there are many tags / categories."""
    style = imgui.get_style()
    next_x2 = imgui.get_item_rect_max().x + style.item_spacing.x + _check_item_width(next_label)
    if next_x2 < right_edge:
        imgui.same_line()


def _gui_filter_header(palette: FunctionPalette, filt: PaletteFilter, *, focus_search: bool) -> None:
    """Search + match mode + category + tag filters, grouped inside a discreet
    panel. A 2-column table aligns the row labels (left) against their controls
    (right)."""
    child_flags = imgui.ChildFlags_.auto_resize_y.value | imgui.ChildFlags_.always_use_window_padding.value
    if imgui.begin_child("##palette_filters", ImVec2(0, 0), child_flags=child_flags):
        if imgui.begin_table("##filters", 2):
            imgui.table_setup_column("##label", imgui.TableColumnFlags_.width_fixed.value)
            imgui.table_setup_column("##controls", imgui.TableColumnFlags_.width_stretch.value)

            _table_row("Search", lambda: _search_and_match_controls(filt, focus_search=focus_search))

            categories = palette.categories_set()
            if len(categories) > 1:
                _table_row("Category:", lambda: _category_controls(palette, filt, categories))

            if palette.tags_set(filt.selected_category):
                _table_row("Tags:", lambda: _tag_controls(palette, filt))

            imgui.end_table()
    imgui.end_child()


def _table_row(label: str, controls: Callable[[], None]) -> None:
    imgui.table_next_row()
    imgui.table_next_column()
    _cell_label(label)
    imgui.table_next_column()
    controls()


def _search_and_match_controls(filt: PaletteFilter, *, focus_search: bool) -> None:
    imgui.set_next_item_width(hello_imgui.em_size(10))
    if focus_search:
        imgui.set_keyboard_focus_here()
    _, filt.search_text = imgui.input_text("##search", filt.search_text)

    imgui.same_line()
    _cell_label("Match:")
    imgui.same_line()
    if imgui.radio_button("AND", filt.match_mode is TagMatchMode.AND):
        filt.match_mode = TagMatchMode.AND
    imgui.same_line()
    if imgui.radio_button("OR", filt.match_mode is TagMatchMode.OR):
        filt.match_mode = TagMatchMode.OR


def _category_controls(palette: FunctionPalette, filt: PaletteFilter, categories: list[str]) -> None:
    """Coarse domain selector (image / text / math / ...). Selecting a category
    scopes the tag chips below to that domain."""

    def select(cat: str | None) -> None:
        if filt.selected_category == cat:
            return
        filt.selected_category = cat
        # Drop selected tags that don't exist in the new category's scope,
        # otherwise the tag filter would silently empty the list.
        scoped = set(palette.tags_set(cat))
        filt.selected_tags[:] = [t for t in filt.selected_tags if t in scoped]

    right_edge = _row_right_edge()
    options: list[tuple[str, str | None]] = [("All", None)]
    for c in categories:
        options.append((c, c))
    for i, (label, cat) in enumerate(options):
        if i > 0:
            _flow_to_next(label, right_edge)
        if imgui.radio_button(label, filt.selected_category == cat):
            select(cat)


def _tag_controls(palette: FunctionPalette, filt: PaletteFilter) -> None:
    all_tags = palette.tags_set(filt.selected_category)
    right_edge = _row_right_edge()
    for i, tag in enumerate(all_tags):
        if i > 0:
            _flow_to_next(tag, right_edge)
        was_selected = tag in filt.selected_tags
        _, is_selected = imgui.checkbox(tag, was_selected)
        if is_selected and not was_selected:
            filt.selected_tags.append(tag)
        elif was_selected and not is_selected:
            filt.selected_tags[:] = [t for t in filt.selected_tags if t != tag]


def _gui_functions(
    palette: FunctionPalette,
    filt: PaletteFilter,
    on_pick: Callable[[FunctionInfo], None],
) -> None:
    """Render functions grouped by their primary (first) tag.

    Updates `filt.latched_fn` to the row currently being hovered. The latch
    persists across frames — when the user moves the mouse into the side
    doc panel, the previously-hovered function's docs stay visible and the
    row stays highlighted.
    """
    infos = palette.filter(filt)
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
                with imgui_ctx.push_obj_id(fi):
                    is_latched = filt.latched_fn is fi
                    display_label = fi.label.split("##")[0]
                    if imgui.selectable(display_label, is_latched)[0]:
                        on_pick(fi)
                    if imgui.is_item_hovered():
                        filt.latched_fn = fi
                        if fi.label != fi.name:
                            imgui.set_tooltip(f"id: {fi.name}")


def _gui_doc_panel(fn_info: FunctionInfo | None, size: ImVec2) -> None:
    """Side documentation panel. Visually distinct from the function list
    (title strip + tinted background) so the user reads it as a separate
    section."""
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


def _render_function_doc_markdown(fn_info: FunctionInfo) -> None:
    title = fn_info.label.split("##")[0]
    tags_str = ", ".join(fn_info.tags) if fn_info.tags else "none"
    lines = [f"## {title}"]
    if fn_info.label != fn_info.name:
        lines.append(f"*id: {fn_info.name}*")
    lines.append(f"Category: {fn_info.category}")
    lines.append(f"Tags: {tags_str}")
    lines.append("---")
    md_str = "\n\n".join(lines)
    imgui_md.render_unindented(md_str)
    if fn_info.doc is not None:
        if fn_info.doc_is_markdown:
            imgui_md.render_unindented(fn_info.doc)
        else:
            imgui.text_wrapped(fn_info.doc)
