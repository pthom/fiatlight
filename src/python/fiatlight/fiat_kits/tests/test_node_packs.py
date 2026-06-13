"""The node-pack registry behind fl.studio()."""
import fiatlight as fl
from fiatlight.fiat_kits.node_packs import default_nodes
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
