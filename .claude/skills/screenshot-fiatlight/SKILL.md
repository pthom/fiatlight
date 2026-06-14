---
name: screenshot-fiatlight
description: Capture a PNG of a fiatlight node graph for visual self-validation. Use after changing anything that affects node rendering (a node's GUI, pins, the reroute node, image/dataframe widgets, the Sugiyama auto-layout, themes) so you can look at the result yourself before asking the user to smoke-test.
---

# Screenshot a fiatlight graph for visual validation

When you change node-rendering code, don't run `python -m fiatlight` and ask the
user to paste a screenshot. Build the graph in code, capture a PNG with
`capture_graph`, and `Read` it yourself first.

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
  headless without Xvfb. Fine on a desktop.
- **Canvas gestures are not scriptable.** The ImGui Test Engine can't drive
  `imgui_node_editor` (node drag, pin-to-pin wiring, right-click-on-link). To
  validate a wired result, build the end-state graph in code (`add_function` +
  `_add_link_from_function_nodes`) and screenshot that — it validates the
  *rendering*, not the gesture. Standard imgui (menus, dialogs, the palette popup)
  could be driven via `immapp.testing.run`, but that's not wrapped here yet.
- **Node-cropped only.** The PNG is cropped to the node bounds (tight + readable);
  there's no full-canvas option in v1.
- **Throwaway settings** land under `fiat_settings/` (git-ignored); `capture_graph`
  starts from a clean window layout (`ini_clear_previous_settings`) so stale debug
  windows can't leak into the shot.
- **Clean up** the `/tmp/shoot_*.py` after validating.

## Reference

- Helper: `fiatlight/fiat_runner/capture.py` (`capture_graph`).
- Underlying: `FiatGui._setup_runner` + `get_last_screenshot` +
  `hello_imgui.final_app_window_screenshot`.
- Inspiration: imgui_bundle's `screenshot-imgui-bundle` / `interact-and-screenshot`
  skills (`immapp.testing.capture_final_frame` / `.run`).
```
