"""Registry of built-in node packs, used by `fl.studio()`.

A node pack is a named provider returning a list of palette-ready functions.
Packs are imported lazily and guarded: a pack whose optional dependency is
missing (e.g. opencv for the image pack) is skipped with a warning rather than
crashing studio().

The AI pack is intentionally NOT in the default set: importing it pulls in
torch (slow) and it is GPU/network-bound, so it should stay opt-in until
studio() grows explicit pack selection.
"""
import importlib
import logging
from typing import List

from fiatlight.fiat_types import Function

# Pack name -> "module:provider" (provider is a zero-arg callable returning a
# list of functions). Insertion order defines the palette order.
_DEFAULT_PACKS: dict[str, str] = {
    "image": "fiatlight.fiat_kits.fiat_image.cv2_nodes:cv2_nodes",
    "math": "fiatlight.fiat_kits.fiat_math:math_nodes",
    "text": "fiatlight.fiat_kits.fiat_text:text_nodes",
}


def _load_pack(spec: str) -> List[Function] | None:
    module_name, attr = spec.split(":")
    try:
        module = importlib.import_module(module_name)
    except ImportError as e:
        logging.warning(f"Node pack {spec!r} skipped (missing dependency: {e}).")
        return None
    provider = getattr(module, attr)
    return list(provider())


def _load_packs(specs: List[str]) -> List[Function]:
    nodes: List[Function] = []
    for spec in specs:
        pack = _load_pack(spec)
        if pack is not None:
            nodes.extend(pack)
    return nodes


def default_nodes() -> List[Function]:
    """Every built-in node pack whose dependencies are installed (image / math /
    text), concatenated in a stable order. This is the default palette of
    `fl.studio()`."""
    return _load_packs(list(_DEFAULT_PACKS.values()))


def minimal_nodes() -> List[Function]:
    """A lightweight subset (math + text only — no opencv import), for fast
    startup / IDE debugging of non-image features."""
    return _load_packs([_DEFAULT_PACKS["math"], _DEFAULT_PACKS["text"]])
