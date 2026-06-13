"""The node-pack registry behind fl.studio()."""
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
    # math and text have no heavy dependency, so they are always present;
    # image is present only when opencv is installed.
    assert {"math", "text"}.issubset(cats)


def test_studio_is_exported() -> None:
    assert callable(fl.studio)


def test_node_pack_by_name() -> None:
    assert len(node_pack("text")) > 0
    assert len(node_pack("ai")) == 1  # invoke_sdxl_turbo (imports lazily, no GPU needed to list it)
    with pytest.raises(ValueError):
        node_pack("does_not_exist")
