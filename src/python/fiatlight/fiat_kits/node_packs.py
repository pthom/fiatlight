"""Registry of built-in node packs, used by `fl.studio()`.

A node pack is a named provider returning a list of palette-ready functions.
Providers import their dependencies lazily and are guarded: a pack whose
optional dependency is missing is skipped with a warning rather than crashing
studio(). The image pack degrades gracefully — without opencv it still offers
the image I/O source nodes (which read/resize via Pillow).

The AI pack is intentionally NOT in the default set: importing it pulls in
torch (slow) and it is GPU/network-bound, so it stays opt-in until studio()
grows explicit pack selection.
"""
import importlib
import logging
from typing import Callable, List

from fiatlight.fiat_types import Function

NodeProvider = Callable[[], List[Function]]


def _import_provider(spec: str) -> NodeProvider:
    """A provider that imports `module:attr` (deferred to call time) and calls
    it. A missing optional dependency surfaces as ImportError from the import."""

    def provider() -> List[Function]:
        module_name, attr = spec.split(":")
        module = importlib.import_module(module_name)
        return list(getattr(module, attr)())

    return provider


def _image_provider() -> List[Function]:
    """The image pack. With opencv: the full cv2 node pack (which already
    includes the image I/O source nodes). Without opencv: just the I/O source
    nodes, which read/resize via Pillow — so you can still load + display images
    and feed them to your own numpy/PIL code."""
    try:
        from fiatlight.fiat_kits.fiat_image.cv2_nodes import cv2_nodes

        return cv2_nodes()
    except ImportError:
        from fiatlight.fiat_kits.fiat_image import image_from_file, image_from_file_resized
        from fiatlight.fiat_utils.fiat_attributes_decorator import add_fiat_attributes

        logging.warning("opencv not installed: offering image I/O nodes only (no cv2 processing nodes).")
        sources = [image_from_file_resized, image_from_file]
        for fn in sources:
            # cv2_nodes' kit-defaults loop normally categorizes these; do it here
            # since that loop did not run (its import needs cv2).
            add_fiat_attributes(fn, fiat_category="image")
        return sources


_PACKS: dict[str, NodeProvider] = {
    "image": _image_provider,
    "math": _import_provider("fiatlight.fiat_kits.fiat_math:math_nodes"),
    "text": _import_provider("fiatlight.fiat_kits.fiat_text:text_nodes"),
    "ai": _import_provider("fiatlight.fiat_kits.fiat_ai:ai_nodes"),
}

# Packs loaded by `fl.studio()` by default. The `ai` pack is excluded: it needs a
# GPU and a multi-GB model download, so it is opt-in (via `node_pack("ai")`).
_DEFAULT_PACK_NAMES = ["image", "math", "text"]


def _load(name: str, provider: NodeProvider) -> List[Function]:
    try:
        return provider()
    except ImportError as e:
        logging.warning(f"Node pack {name!r} skipped (missing dependency: {e}).")
        return []


def node_pack(name: str) -> List[Function]:
    """Load a single named pack: "image", "math", "text", or "ai". Returns []
    if the pack's optional dependency is missing. Use it to opt into packs that
    are not in the default `fl.studio()` palette, e.g. `node_pack("ai")`."""
    if name not in _PACKS:
        raise ValueError(f"Unknown node pack {name!r}. Known packs: {sorted(_PACKS)}.")
    return _load(name, _PACKS[name])


def default_nodes() -> List[Function]:
    """Every default built-in node pack whose dependencies are installed (image
    / math / text), concatenated in a stable order. This is the default palette
    of `fl.studio()`. Without opencv, the image pack degrades to its I/O source
    nodes."""
    nodes: List[Function] = []
    for name in _DEFAULT_PACK_NAMES:
        nodes.extend(_load(name, _PACKS[name]))
    return nodes


def minimal_nodes() -> List[Function]:
    """A lightweight subset (math + text only — no opencv import), for fast
    startup / IDE debugging of non-image features."""
    return _load("math", _PACKS["math"]) + _load("text", _PACKS["text"])
