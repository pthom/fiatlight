"""The node-pack registry behind fl.studio()."""
import sys

import pytest

import fiatlight as fl
from fiatlight.fiat_kits.node_packs import default_nodes, node_pack
from fiatlight.fiat_palette import FunctionPalette


def test_default_nodes_span_categories() -> None:
    nodes = default_nodes()
    assert len(nodes) > 0
    p = FunctionPalette()
    for f in nodes:
        p.add_function(f)
    cats = set(p.categories_set())
    # math/text always present; image is always present too (the I/O source
    # nodes degrade to a Pillow fallback when opencv is absent).
    assert {"image", "math", "text"}.issubset(cats)


def test_studio_is_exported() -> None:
    assert callable(fl.studio)


def test_node_pack_by_name() -> None:
    assert len(node_pack("text")) > 0
    assert len(node_pack("ai")) == 1  # invoke_sdxl_turbo (imports lazily, no GPU needed to list it)
    with pytest.raises(ValueError):
        node_pack("does_not_exist")


def test_image_pack_falls_back_to_io_nodes_without_cv2(monkeypatch: pytest.MonkeyPatch) -> None:
    # Force `import cv2` to fail, and drop the cached cv2_nodes package so the
    # provider re-imports it and hits the ImportError fallback branch.
    monkeypatch.setitem(sys.modules, "cv2", None)
    for mod in list(sys.modules):
        if mod.startswith("fiatlight.fiat_kits.fiat_image.cv2_nodes"):
            monkeypatch.delitem(sys.modules, mod, raising=False)

    names = [f.__name__ for f in node_pack("image")]
    assert names == ["image_from_file_resized", "image_from_file"]
    # categorized as image even though the cv2_nodes kit loop did not run
    p = FunctionPalette()
    for f in node_pack("image"):
        p.add_function(f)
    assert p.categories_set() == ["image"]
