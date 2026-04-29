# CLAUDE.md — fiatlight

Project-level guidance for AI coding sessions. Read this before making
non-trivial changes; it captures the *why* and the gotchas, not the
things you can read off the code in five minutes.

## What this is

A Python library that turns annotated functions into a live, type-checked
visual node graph rendered with Dear ImGui (via imgui_bundle). Users wire
functions together on a canvas; types are checked at link-creation time;
each output auto-renders with a type-aware preview (numpy images,
dataframes, plots, primitives, dataclasses, pydantic models, ...).

Entry point: `fl.run_graph_composer(functions=[...])`.
Read `examples/img_proc_playground/main.py` first for a representative use.

## Repo layout

Source: `src/python/fiatlight/`. Layered, depending downward:

- `fiat_types/` — pure type metadata: NewTypes, `typename_utils` (string
  identities for types), `type_compat` (link-time compatibility).
- `fiat_togui/` — type → GUI factory dispatch, the `gui_factories()` registry.
- `fiat_core/` — `AnyDataWithGui`, `FunctionWithGui`, `FunctionsGraph`
  (headless graph data + execution).
- `fiat_widgets/` — reusable imgui widgets, OSD primitives (see canvas rule).
- `fiat_kits/` — domain bundles (`fiat_image`, `fiat_dataframe`, ...).
- `fiat_nodes/` — `FunctionsGraphGui`, `FunctionNodeGui`, the
  `imgui_node_editor` canvas wiring.
- `fiat_runner/` — `FiatGui` (top-level app), `FunctionPalette` (left dock
  + popup palette), `run_graph_composer`.

Tests live next to code at `<package>/tests/test_*.py`.
Examples / demos / sandbox / `tests_usability` are interactive.

`examples/*/fiat_settings/*.json` are **runtime state** (saved graph,
window positions). Never include them in feature commits.

## Type identity is string-based

`fiat_types.typename_utils.fully_qualified_typename(t)` returns a string
(`"fiatlight.fiat_kits.fiat_image.image_types.ImageRgb"`). The whole GUI
registry / factory dispatch / matching layer is keyed on those strings —
not on Python `issubclass`. NewType chains expose `.__supertype__`,
which `type_compat` walks one-directionally (output → input).

The image type hierarchy in `fiat_kits/fiat_image/image_types.py` is
non-obvious:

- `ImageRgb.__supertype__ is ImageU8_3` (a NewType), **not** `np.ndarray`.
- `Image = Union[ImageU8, ImageFloat]` where each side is itself a Union
  of role-typed and channel-count-typed NewTypes.
- Walking the supertype chain reaches `np.ndarray` eventually.

Link-time compatibility lives in `fiat_types.type_compat.is_link_compatible`.
Rule order is documented in its module docstring; the short version:
`Any → typename eq → output Union all-match → input Union any-match →
NewType supertype walk on output side → bare-ndarray escape hatch → reject`.
Wired into `FunctionsGraph._can_add_link` (graph data) and into the
palette popup via `FunctionInfo.first_compatible_input/output` (UX filter).

## The canvas rule

**Never display GUI widgets while inside `ed.begin / ed.end`** (the
`imgui_node_editor` canvas). The canvas's zoom transform is incompatible
with ImGui windows / child windows / popups. Two correct paths:

1. **`fiat_widgets.fiat_osd`** — preferred for tooltips/popups originating
   from inside nodes. Queue with `set_tooltip(str)` / `set_tooltip_gui(fn)`
   / `set_popup_gui(fn)`; rendered later via `render_all_osd()`. The
   `set_tooltip_str` helper is canvas-aware (defers when inside the editor).
2. **Render after `ed.end()`** — explicit, used by `FunctionsGraphGui`
   for the palette popup. `imgui.open_popup` / `begin_popup` calls live
   *outside* the `ed.begin/end` pair, so no `suspend()` / `resume()` needed.

When in doubt, don't reimplement what imgui does (tooltip positioning,
auto-resize, viewport clip). If a lever you need isn't exposed, that's
usually imgui telling you the seam is wrong.

## Cross-package patterns

- `fiat_nodes` does not import from `fiat_runner`. Cross-package features
  (right-click palette popup, drag-from-pin) are wired via **callbacks**
  set on `FunctionsGraphGui` by `FiatGui`. See
  `on_open_palette_popup` / `on_render_palette_popup_body`.
- Pin types live on `AnyDataWithGui._type` (leading underscore — pre-
  existing pattern, widespread). Several call sites read it directly.
  A public `data_type` property would be cleaner; separate refactor.
- Several `FunctionsGraph` operations are nominally "private"
  (`_can_add_link`, `_add_link_from_function_nodes`, `_remove_link`)
  but are part of the GUI's working API. Don't tighten access.

## Tooling

```bash
python -m mypy                            # strict, mypy.ini at repo root
python -m pytest src/python/fiatlight/ \
    --ignore=src/python/fiatlight/tests_usability
```

mypy is `strict=True` and is expected to be **0 errors**.
Pre-commit hooks run ruff / ruff-format / utf-8-bom / no-tabs.
Treat them as authoritative — don't bypass with `--no-verify`.

## How to extend types (TL;DR)

1. Define a `NewType` (with a `__doc__`) or a regular class.
2. Register a GUI:
   - `fl.register_type(MyType, MyTypeWithGui)` for plain types,
   - `fl.register_typing_new_type(...)` for NewTypes,
   - `fl.register_dataclass(...)` / `register_base_model(...)` for
     dataclasses / pydantic models (autogenerated form GUI),
   - `gui_factories().register_bound_float(...)` for refined numeric
     types like `Float_0_1`.
3. `type_compat` picks up NewType supertype walking automatically — no
   per-type rules needed for ordinary subtypes.

## How to add a graph-editor feature

Pattern: `FunctionsGraphGui` exposes optional callbacks; `FiatGui` wires
them. Keep the data flow one-directional (callback in, callback out) so
`fiat_nodes` stays a leaf. See the palette popup wiring as a worked example.

## Workflow notes

- For non-trivial features (multi-file, new modules, new public API,
  cross-cutting GUI changes): finish + tests + senior-review pass, then
  **show the diff and wait for approval before committing**. Auto-mode
  does not override this.
- For symbol-level rename / remove, prefer LSP `findReferences` over
  grep — strings inside docstrings or matcher predicates can hide
  actual usage.
- Commit messages: short lowercase declarative subject (`area: do X`),
  paragraph or bullet body explaining *why* and pointing at the related
  code paths. Don't restate the diff.
- Don't reach for hooks / `--no-verify` / amend on hook failure. Fix the
  reported issue and create a new commit.

## Things that are NOT in scope here

- Caching of node outputs / parallel execution / progress bars — known
  gaps vs. ComfyUI; don't add ad-hoc.
- Reroute / subgraph / pin nodes — planned, not yet implemented.
- Replacing `_type` accesses with a public property — broad refactor,
  not part of any current feature.
