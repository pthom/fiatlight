"""Function palette — pure model + filtering. No imgui import here.

Kept GUI-free so the palette can power non-popup surfaces too (a registry
browser, a CLI list, headless tests). The matching popup widget lives in
`fiat_palette.palette_gui`.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from fiatlight.fiat_core import FunctionWithGui
from fiatlight.fiat_types import Function
from fiatlight.fiat_types.type_compat import is_link_compatible
from fiatlight.fiat_types.typename_utils import TypeLike

from typing import Any, Callable


FunctionWithGuiFactory = Callable[[], FunctionWithGui]


class PinKind(Enum):
    """Which side of a function a pin sits on."""

    INPUT = "input"
    OUTPUT = "output"


class TagMatchMode(Enum):
    """How the function palette combines a list of selected tags.

    AND: a function matches only if it carries every selected tag.
    OR:  a function matches if it carries any of the selected tags.
    """

    AND = "AND"
    OR = "OR"


class PaletteFilter(BaseModel):
    """Mutated by the GUI each frame; lifetime owned by the popup host.

    Persisted across sessions (search text, selected tags, match mode are
    user UI state worth remembering)
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    selected_tags: list[str] = Field(default_factory=list)
    search_text: str = ""
    match_mode: TagMatchMode = TagMatchMode.AND
    # Coarse domain filter (image / text / math / ...). None = all categories.
    # Tag chips are scoped to the selected category.
    selected_category: str | None = None

    # Type filters: when drag-from-pin opens the popup, the graph sets the
    # appropriate slot to restrict the candidate list. Both sides may be
    # set; the result is the AND of both constraints. Excluded from persistence.
    input_type_filter: TypeLike | None = Field(default=None, exclude=True)
    output_type_filter: TypeLike | None = Field(default=None, exclude=True)

    # Hover latch for the side doc panel — transient UI state.
    latched_fn: "FunctionInfo | None" = Field(default=None, exclude=True)

    # Whether the full tag grid is expanded. Transient presentation state
    # (collapsed by default); not a filter, so it is excluded from persistence
    # and ignored by is_user_default().
    show_all_tags: bool = Field(default=False, exclude=True)

    def reset(self) -> None:
        """Reset the user-facing filters to their defaults. Leaves the per-open
        type filters (input/output_type_filter) and the doc-panel latch alone."""
        self.search_text = ""
        self.selected_tags = []
        self.match_mode = TagMatchMode.AND
        self.selected_category = None
        self.show_all_tags = False

    def is_user_default(self) -> bool:
        """True when no user filter is active (so the Clear button can hide)."""
        return (
            not self.search_text
            and not self.selected_tags
            and self.match_mode is TagMatchMode.AND
            and self.selected_category is None
        )


@dataclass
class FunctionInfo:
    name: str
    # Display name (from the `label` fiat attribute). Falls back to `name`.
    # `name` stays the Python id used as the registry/identity key everywhere;
    # `label` is presentation-only.
    label: str
    function_factory: FunctionWithGuiFactory
    tags: list[str]
    # Coarse domain (from the `fiat_category` attribute). "other" when unset.
    category: str
    doc: str | None
    doc_is_markdown: bool
    # Stable cross-run identity (`module.qualname`) used as the registry key
    # in saved workspaces. Empty when the wrapped factory builds a
    # FunctionWithGui without a Python-defined function (e.g. some MarkdownNode
    # constructions).
    function_ref: str = ""
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


# Fallback tag / category for functions that declare neither. They still work
# in the palette (grouped under "other"); curated packs set their own.
_UNCATEGORIZED = "other"


def _read_fiat_tags(fn: Function) -> list[str]:
    """Read `fn.fiat_tags`, defaulting to `["other"]` when unset.

    Tags are the single source of truth — they live on the function so the same
    wrapper carries the same intent everywhere it is registered. Set them via
    `@fl.with_fiat_attributes(fiat_tags=[...])` at definition, or
    `fl.add_fiat_attributes(fn, fiat_tags=[...])` for imported / shimmed
    functions. Untagged functions are not rejected (that would make a quick
    `run_graph_composer([my_fn])` crash); they land in the "other" group, with a
    warning so the omission is still surfaced.
    """
    tags = getattr(fn, "fiat_tags", None)
    if not tags:
        name = getattr(fn, "__name__", repr(fn))
        logging.warning(
            f"Function {name!r} has no `fiat_tags`; placing it in the {_UNCATEGORIZED!r} group. "
            f"Set them via `@fl.with_fiat_attributes(fiat_tags=[...])` or `fl.add_fiat_attributes(...)`."
        )
        return [_UNCATEGORIZED]
    return list(tags)


def _read_fiat_category(fn: Function) -> str:
    """Read `fn.fiat_category` (coarse domain: image / text / math / ...).

    Optional: defaults to "other" when unset. Set via
    `@fl.with_fiat_attributes(fiat_category="image")` or by a kit applying it to
    its whole pack.
    """
    category = getattr(fn, "fiat_category", None)
    return category if category else _UNCATEGORIZED


def _search_terms(search_text: str) -> list[str]:
    import shlex

    try:
        tokens = shlex.split(search_text)
    except ValueError:
        tokens = search_text.split()
    return [t.lower() for t in tokens if t]


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
        category = _read_fiat_category(fn)

        def factory() -> FunctionWithGui:
            return FunctionWithGui(fn)

        self._add_function_factory(factory, tags, category)

    def add_reroute_node(self) -> None:
        """Register the built-in Reroute (relay) node: a polymorphic passthrough for
        tidying crossing wires. It needs the factory path (not `add_function`) since
        it builds a FunctionWithGui subclass; registering it also lets saved
        workspaces resolve its `function_ref` on load."""
        from fiatlight.fiat_core.reroute_function import RerouteFunctionWithGui

        self._add_function_factory(lambda: RerouteFunctionWithGui(), tags=["reroute"], category="utilities")

    def _add_function_factory(
        self, function_factory: FunctionWithGuiFactory, tags: list[str], category: str = _UNCATEGORIZED
    ) -> None:
        gui = function_factory()
        name = gui.function_name
        label = gui.label
        function_ref = gui.function_ref
        doc = gui.get_function_doc()
        input_types = [
            (gui.input_of_idx(i).name, gui.input_of_idx(i).data_with_gui._type) for i in range(gui.nb_inputs())
        ]
        output_types = [gui.output(i)._type for i in range(gui.nb_outputs())]
        function_info = FunctionInfo(
            name,
            label,
            function_factory,
            tags,
            category,
            doc.user_doc,
            doc.is_user_doc_markdown,
            function_ref=function_ref,
            input_types=input_types,
            output_types=output_types,
        )
        self._functions.append(function_info)

    def tags_set(self, category: str | None = None) -> list[str]:
        """Distinct tags, optionally restricted to functions in `category`."""
        tags: set[str] = set()
        for function_info in self._functions:
            if category is not None and function_info.category != category:
                continue
            tags.update(function_info.tags)
        return sorted(tags)

    def categories_set(self) -> list[str]:
        """Distinct categories across all functions (sorted)."""
        return sorted({fi.category for fi in self._functions})

    def filter(self, filt: PaletteFilter) -> list[FunctionInfo]:
        """Apply category / tag / type / search-text filters in one pass."""
        # 0. Category filter (coarse domain).
        if filt.selected_category is not None:
            infos = [fi for fi in self._functions if fi.category == filt.selected_category]
        else:
            infos = list(self._functions)

        # 1. Tag filter (within the category-filtered set).
        if filt.selected_tags:
            if filt.match_mode is TagMatchMode.AND:
                infos = [fi for fi in infos if all(t in fi.tags for t in filt.selected_tags)]
            elif filt.match_mode is TagMatchMode.OR:
                infos = [fi for fi in infos if any(t in fi.tags for t in filt.selected_tags)]
            else:
                raise ValueError(f"Unknown TagMatchMode: {filt.match_mode!r}")

        # 2. Type filters: AND-combined.
        if filt.input_type_filter is not None:
            tl = filt.input_type_filter
            infos = [fi for fi in infos if fi.first_compatible_input(tl) is not None]
        if filt.output_type_filter is not None:
            tl = filt.output_type_filter
            infos = [fi for fi in infos if fi.first_compatible_output(tl) is not None]

        # 3. Search text.
        terms = _search_terms(filt.search_text)
        if not terms:
            return infos

        def haystack(fi: FunctionInfo) -> str:
            parts = [fi.name, fi.label, *fi.tags]
            if fi.doc is not None:
                parts.append(fi.doc)
            return "\n".join(parts).lower()

        if filt.match_mode is TagMatchMode.AND:
            return [fi for fi in infos if all(t in haystack(fi) for t in terms)]
        return [fi for fi in infos if any(t in haystack(fi) for t in terms)]

    def factor_function_from_ref(self, function_ref: str) -> FunctionWithGui:
        """Look up a `function_ref` (the `module.qualname` string carried in
        saved workspaces) and call the registered factory to produce a fresh
        FunctionWithGui. Raises ValueError if no registered function has
        that ref; the workspace loader catches this to drop orphaned nodes
        gracefully."""
        for function_info in self._functions:
            if function_info.function_ref and function_info.function_ref == function_ref:
                return function_info.function_factory()
        raise ValueError(f"Function with ref {function_ref!r} not found in palette")

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
