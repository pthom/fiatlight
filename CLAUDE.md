# CLAUDE.md — fiatlight

# Guidelines for AI-assisted coding

When helping users with coding tasks, please follow these guidelines to ensure high-quality, maintainable code.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.
- If a solution becomes complex (multiple cascading changes, need for workarounds), STOP and explain the difficulty. Present options rather than plowing ahead.

**If you encounter an API in the codebase which is awkward to use**
- Do not circumvent it with a hack. Instead, surface the issue and ask for clarification or improvement.
- The same goes for code smells or patterns that seem out of place. Don't just "make it work" - stop implementing,
  then communicate the underlying problem so it can be addressed properly in collaboration with the user.
- This is **important**: we follow a trajectory where the codebase needs to become better and better.
  So, when we encounter something that is awkward (a code, an architecture smell) and which makes our job difficult, it is a good time to surface it.
  Then discuss with the user on how it could be improved to make the task at hand better, as well as all future developments a maintenance.
  The user might discuss with you on how to improve the architecture (do provide some well thought advices), or he might decide to say that a workaround
  is the way to follow. But this needs to be discussed.


**Before implementing a solution, wait for the user to finish evaluating alternatives.**

**No whack-a-mole loops.** When hitting a second unexpected failure in a row on a hard problem (especially cross-platform builds, CI, toolchain issues): STOP fixing. Present the full picture of what's going wrong and why, and ask to examine the difficulties together before writing more code. Investigation time up front saves much more than it costs. Similarly, before bumping a dependency version, check changelogs/release notes for new features that could interact with existing build flags.


## 1b. Interaction Style

**Wait before acting.** Do NOT start implementing or proposing solutions before the user has finished evaluating alternatives or describing the problem. Wait for explicit go-ahead. When asked to analyze or review, produce analysis ONLY — not code changes.


## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 3b. C++/Python Porting

When porting between C++ and Python: use raw strings for multiline content, use Python naming conventions (snake_case). Verify API names exist before using them (check the `.pyi` stubs).

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## 5. Debug from data, not from theory

**A single well-placed log is worth ten speculative fixes.**

- Before changing code to fix a bug, observe the actual values at the suspected fault site. Don't assume what a function returns — log it.
- If your fix doesn't work on the first try, stop coding and add observation. A second failed attempt without new data means you don't yet understand the bug.
- Choose log sites that will distinguish between the leading hypotheses. If you have two competing theories, log the values that would differ between them.

## 5a. Stop after two

After **two failed attempts** to fix a bug, stop coding and write down — for the user, or for yourself — what you've tried, why each failed, and what data would distinguish the remaining hypotheses. Resist the third speculative patch. The third patch usually leaks into the fourth, and by then the original problem is buried under fix-of-fix code.


## 6. Comments document the code, not the journey

Code comments explain what a future reader needs to know to safely modify the code. They do **not** narrate development history.

- ✅ "Function X reroutes Y through a transform — value here is in canvas coords, not screen."
- ❌ "We had a bug where this returned the wrong value, then we tried Z, then we discovered…"

War stories belong in commit messages and PR descriptions; the code stays clean.


# Fiatlight-specific notes

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

**Never display bare (i.e outside of  node) GUI widgets while inside `ed.begin / ed.end`** (the
`imgui_node_editor` canvas). The canvas's zoom transform is incompatible
with ImGui windows / child windows / popups. Two correct paths:

1. **`fiat_widgets.fiat_osd`** — preferred for tooltips/popups originating
   from inside nodes. Queue with `set_tooltip(str)` / `set_tooltip_gui(fn)`
   / `set_popup_gui(fn)`; rendered later via `render_all_osd()`. The
   `set_tooltip_str` helper is canvas-aware (defers when inside the editor).
2. **Render after `ed.end()`** — explicit, used by `FunctionsGraphGui`
   for the palette popup. `imgui.open_popup` / `begin_popup` calls live
   *outside* the `ed.begin/end` pair, so no `suspend()` / `resume()` needed.

When you are inside ed.begin() / ed.end(), the canvas hacks all the coordinates (widgets windows, including the mouse coordinates),
so that they are in canvas coordinates. It is possible suspend/resume that with the suspend()/resume() functions.
Suspend and resume are not 100% safe based on Pascal's experiments, so we may also avoid the problem by using the fiat_osd when possible
(i.e. deferred gui lambdas that will run after ed.end()).



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
