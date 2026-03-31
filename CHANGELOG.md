# Changelog

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
