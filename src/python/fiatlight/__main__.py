"""`python -m fiatlight` — launch the Fiatlight studio (interactive node composer).

    python -m fiatlight          # full palette (image / math / text)
    python -m fiatlight --min    # fast, opencv-free palette (math + text)
    python -m fiatlight --ai     # full palette + the AI image-gen node
                                 # (needs a GPU/mps + a one-time model download)

This is also the single source of truth for the `examples/studio.py` launcher.
"""
import sys

import fiatlight as fl


def main() -> None:
    from fiatlight.fiat_kits.node_packs import minimal_nodes, node_pack

    if "--min" in sys.argv:
        fl.run_graph_composer(minimal_nodes(), app_name="fiatlight studio (min)")
        return
    extra = node_pack("ai") if "--ai" in sys.argv else None
    fl.studio(functions=extra)


if __name__ == "__main__":
    main()
