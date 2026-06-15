---
name: screenshot-fiatlight
description: Capture a PNG of a fiatlight node graph for visual self-validation. Use after changing anything that affects node rendering (a node's GUI, pins, the reroute node, image/dataframe widgets, the Sugiyama auto-layout, themes), or to reproduce a GUI issue the user reported, so you can look at the result yourself before asking the user to smoke-test.
---

# Screenshot a fiatlight graph for visual validation

When you change node-rendering code, don't run `python -m fiatlight` and ask the
user to paste a screenshot. Capture a PNG yourself and `Read` it. Two mechanisms,
pick by intent:

- **Reproduce the user's EXACT scenario** (their bug report, their layout) → run
  *their unmodified script* with capture env vars. Faithful: their saved workspace /
  node positions, no relayout, full-window PNG. See next section.
- **Validate a rendering change on a graph you build** → `capture_graph`. Builds a
  fresh graph, auto-lays-it-out (Sugiyama), node-cropped PNG. See "capture_graph".

## Reproduce the user's exact scenario (preferred when reproducing their report)

Run their script verbatim — no edits — with two env vars:

```bash
FIATLIGHT_EXIT_AFTER_FRAMES=40 FIATLIGHT_SCREENSHOT_PATH=/tmp/shot.png \
  VIRTUAL_ENV=.venv python <their_script.py>
```

**Run it from the script's own directory** (`cd` there first): `fiat_settings/` — the saved
workspace / node layout — is resolved relative to the **cwd**, not the script path. Running from
the repo root loads a fresh/empty workspace (so the layout won't match the user's) and scatters a
stray `fiat_settings/` at the root. Use an absolute `FIATLIGHT_SCREENSHOT_PATH` (e.g. `/tmp/...`).

then `Read /tmp/shot.png`. The run loads their real workspace / saved node positions
(no clean slate, no auto-relayout), renders N frames, writes a **full-window** PNG
(menus, tabs, status bar, the graph where they left it), and exits. The env vars are
the fallback for `FiatRunParams.exit_after_frames` / `screenshot_path` (so no code
change is needed); set those fields directly if capturing from your own run call.
Backed by `fiat_runner/fiat_gui.py` (`_resolve_capture_params`, `_before_exit`).

## capture_graph (build a graph, validate its rendering)

`fiatlight.fiat_runner.capture.capture_graph` builds the graph in a real window,
lays the nodes out (Sugiyama), lets it settle, auto-exits after N frames, and
writes the **node-cropped** framebuffer to a PNG. It reuses the app's own
exit-screenshot path (`hello_imgui.final_app_window_screenshot` cropped to node
bounds, via `get_last_screenshot`); the only added wiring is "exit after N frames".

## Workflow

Write a tiny temp script in `/tmp/` (keep the repo clean), build the graph you
want to validate, capture, then Read the PNG.

```python
# /tmp/shoot_xxx.py
from fiatlight.fiat_core.functions_graph import FunctionsGraph
from fiatlight.fiat_runner.capture import capture_graph

def make_str() -> str: return "hello"
def need_str(s: str) -> str: return s

# Build whatever wiring you want to see (links are part of what you validate).
g = FunctionsGraph.create_empty()
g.add_function(make_str)
g.add_function(need_str)
src, dst = g.functions_nodes
g._add_link_from_function_nodes(src, dst, dst_input_name="s", src_output_idx=0)

capture_graph(g, "/tmp/shot.png", frames=30)
```

Run it (it opens a real window for ~1 s) and read the PNG:

```bash
python /tmp/shoot_xxx.py     # the project venv python, with imgui_bundle installed
```

```
Read /tmp/shot.png
```

The PNG appears as `<output_image>` in the tool result.

## API

`capture_graph(graph_or_functions, output_path, *, frames=25, window_size=(1000,700), invoke=True) -> str`

- `graph_or_functions` — a ready-built `FunctionsGraph` (build the exact wiring you
  want to validate), or a flat list of functions (added unlinked).
- `frames` — how many frames to render before grabbing. Bump to 40-60 if a wide
  graph needs more time for layout + camera-fit to settle.
- `window_size` — logical pixels; the PNG is `size * dpi_scale` (2× on retina).
- `invoke=True` — run the functions once so output values (e.g. images) are present.

## Validating specific things

- **A node's rendering** (reroute pins/colors/rotation, image widget, dataclass
  form, float slider): build a 1-3 node graph that exercises it and capture.
- **Reroute display options**: set them before capturing —
  `reroute.function_with_gui.show_type = True`, `.rotate(1)`.
- **Auto-layout**: capture a wider graph; the nodes are laid out automatically a
  few frames in (once their sizes are known), so the shot shows the real layout.

## Caveats

- **Real GL context required** — opens a real window for ~1 s (it flashes). Not
  headless without Xvfb. Fine on a desktop. Run it outside the sandbox. If it errors
  with "could not use non existent monitor #0", the display went unavailable
  (lock/sleep) — retry after a moment.
- **Canvas gestures are not scriptable.** The ImGui Test Engine can't drive
  `imgui_node_editor` (node drag, pin-to-pin wiring, right-click-on-link). To
  validate a wired result, build the end-state graph in code (`add_function` +
  `_add_link_from_function_nodes`) and screenshot that — it validates the
  *rendering*, not the gesture. Standard imgui (menus, dialogs, the palette popup)
  could be driven via `immapp.testing.run`, but that's not wrapped here yet.
- **Crop differs by mechanism.** `capture_graph` is node-cropped (tight + readable);
  the env-var path is full-window (menus / tabs / status bar included). Use the env-var
  path when the surrounding UI matters or to match what the user sees.
- **Throwaway settings** land under `fiat_settings/` (git-ignored) — never commit them.
  `capture_graph` starts from a clean window layout (`ini_clear_previous_settings`) so
  stale debug windows can't leak in; the env-var path keeps the user's real settings.
- **Clean up** the `/tmp/shoot_*.py` after validating.

## Reference

- Reconstruct-a-graph: `fiatlight/fiat_runner/capture.py` (`capture_graph`).
- Capture-the-running-app: `fiatlight/fiat_runner/fiat_gui.py`
  (`FiatRunParams.exit_after_frames` / `screenshot_path`, `_resolve_capture_params`,
  `_save_full_window_screenshot`, env vars `FIATLIGHT_EXIT_AFTER_FRAMES` /
  `FIATLIGHT_SCREENSHOT_PATH`).
- Underlying: `get_last_screenshot` + `hello_imgui.final_app_window_screenshot`.
- Inspiration: imgui_bundle's `screenshot-imgui-bundle` / `interact-and-screenshot`
  skills (`immapp.testing.capture_final_frame` / `.run`).
```
