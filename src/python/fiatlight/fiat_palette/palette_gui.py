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
    _gui_search_and_match_mode(filt, focus_search=focus_search)
    _gui_tags(palette, filt)

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
                    if imgui.selectable(fi.name, is_latched)[0]:
                        on_pick(fi)
                    if imgui.is_item_hovered():
                        filt.latched_fn = fi


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
