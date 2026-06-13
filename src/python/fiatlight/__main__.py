"""`python -m fiatlight` — launch the Fiatlight studio (interactive node composer).

    python -m fiatlight          # full palette (image / math / text)
    python -m fiatlight --min    # fast, opencv-free palette (math + text)

This is also the single source of truth for the `examples/studio.py` launcher.
"""
import sys

import fiatlight as fl


def main() -> None:
    if "--min" in sys.argv:
        from fiatlight.fiat_kits.node_packs import minimal_nodes

        fl.run_graph_composer(minimal_nodes(), app_name="Fiatlight Studio (min)")
    else:
        fl.studio()


if __name__ == "__main__":
    main()
