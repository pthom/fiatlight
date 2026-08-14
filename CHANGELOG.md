# Changelog

## v0.8.0 (2026-08-14)

A major release centered on the interactive graph composer ("studio"): build image-processing
and data pipelines by wiring nodes on a canvas, with type-checked links, a searchable function
palette, groups, auto-layout, undo/redo and workspace persistence.

### Fiatlight Studio (interactive node composer)

- New entry points: `fl.studio()`, `fl.run_graph_composer(functions=[...])`,
  `fiatlight_studio` console script and `python -m fiatlight`
- Function palette (`fiat_palette`): searchable, with categories and optional tags;
  dockable on the left, or as a popup on right-click; filter persists across sessions
- Drag a wire from a pin onto empty canvas to pick a compatible node (palette filtered
  by link compatibility); double-click empty canvas opens the palette (ComfyUI-style)
- Link-time type checking: incompatible links are rejected at graph-edit time
  (`fiat_types.type_compat`, NewType supertype walking, Union rules)
- Opt-in node packs: `node_pack("ai")` / `--ai` for the AI pack

### Graph editing

- Undo/redo for the function graph (snapshot-based)
- Copy / paste / duplicate nodes and groups (pasted nodes recompute their outputs)
- Groups: tinted rectangles behind nodes, with a categorized context menu
  (Reorganize, collapse all / expand all)
- Auto-layout: layered (Sugiyama-style) algorithm with crossing minimization,
  group-aware; "Reorganize" via menu or Ctrl+L; can also lay out only the selected nodes
- Reroute (relay) passthrough nodes with compact custom rendering
- Editable markdown / post-it Note node, with resize grip and inline popup editor
- Unified, categorized graph actions menu shared by the canvas right-click and the Graph menu
- Canvas navigation help surfaced in the Help menu and on right-click

### Workspace persistence

- Workspace + session JSON file format, based on stable node identities
- File menu rewrite: New / Open / Save / Save As + "Open Recent" workspace list
- Status-bar workspace name with unsaved marker; Ctrl+S to save;
  workspaces auto-save on exit
- Canvas auto-refits after loading a workspace (zoom out only, never in)

### fiat_image: OpenCV kit expansion

- Many new cv2 wrappers, keeping the original cv2 names: contours, histograms,
  HoughLinesP / HoughCircles, feature detectors, warps, pyrDown / pyrUp, inRange,
  distanceTransform, template matching, floodFill, grabCut / watershed,
  connected components, sparse optical flow, pencilSketch, ...
- New geometry types with GUIs: `Points2D`, `Lines2D`, `Circles2D`, `Rect2D`,
  `Matrix2x3`, `Matrix3x3`
- Interactive ROI picker node (`image_roi`)
- Works without OpenCV: image loading / resizing falls back to Pillow,
  image I/O nodes stay available in the palette

### New kits

- `fiat_math` (float and int math nodes) and `fiat_text` node packs

### Core improvements

- Functions can return `NamedTuple`s: each field becomes a separate labeled output;
  outputs can be labeled via fiat attributes (`return__label`, `return_1__label`, ...)
- NewType auto-dispatch: GUIs are found by walking the NewType supertype chain
- New helpers: `make_simple_gui`, `register_callbacks`
- Node rendering polish: one-line value preview in collapsed nodes, width-based text
  truncation, values aligned to the widest label, nodes shrink cleanly
- Exceptions are displayed wrapped inside the node
- Errors raise a notification instead of auto-opening the Log window
- Rewritten any-range float slider

### Runner & tooling

- `capture_graph`: screenshot capture (node-cropped or full window) + exit-after-frames,
  for automated visual validation
- pyright configuration added alongside strict mypy (0 errors)

### Maintenance

- `fiat_matplotlib`: close previous figure to avoid a pyplot leak
- Removed `documented_newtype`, `roi_picker`, `graph.function_with_gui_of_name`
- Detached popup windows no longer save settings (fixes a crash at exit)

## v0.7.2 (2026-04-02)
- Fix dataframe registration

## v0.7.1 (2026-03-31)

- Logo loading no longer requires OpenCV — uses `hello_imgui.im_texture_id_from_asset` (stb_image) instead

## v0.7.0 (2026-03-31)

### New features
- Async runner support: `fiatlight.nb.start()` / `fiatlight.nb.stop()` for running fiatlight apps from notebooks
- `top_most` parameter for runners (keep window on top)
- LUT: implement `_draw_line` for LUT curve visualization

### Improvements
- OpenCV is now optional: `fiat_image` gracefully degrades when OpenCV is not installed
- `pydantic` added as a core dependency (was previously implicit)
- Mypy clean: all type warnings resolved (0 errors across 324 source files)
- New motto: "Turn Python functions into interactive apps in one line"

### Maintenance
- Doc submodule moved to repository root
- Removed empty `devel_doc` directory
- `uv.lock` added to `.gitignore`

## v0.6.0

- Depends on imgui-bundle 1.92.6
- Internal release (not published to PyPI)

## v0.5.0

- Initial public release on PyPI
