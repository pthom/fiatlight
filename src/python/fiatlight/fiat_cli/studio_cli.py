"""Shared launcher for the Fiatlight studio.

Single source of truth for the three studio entry points so they cannot drift:

- the `fiatlight_studio` console script (`[project.scripts]`),
- `python -m fiatlight` (see `fiatlight/__main__.py`),
- the `fiatlight studio` subcommand (see `fiat_cli/fiatlight_cli.py`).

`run_studio` does the launching; `main` adds an argparse front-end so
`fiatlight_studio -h` documents the `--min` / `--ai` options.
"""
from __future__ import annotations

import argparse


def run_studio(*, minimal: bool = False, ai: bool = False) -> None:
    """Open the Fiatlight studio with the chosen palette.

    minimal: fast, opencv-free palette (math + text).
    ai:      full palette plus the AI image-gen node.
    """
    import fiatlight as fl
    from fiatlight.fiat_kits.node_packs import minimal_nodes, node_pack

    if minimal:
        fl.run_graph_composer(minimal_nodes(), app_name="fiatlight studio (min)")
        return
    extra = node_pack("ai") if ai else None
    fl.studio(functions=extra)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fiatlight_studio",
        description="Launch the Fiatlight studio: an interactive node composer.",
        epilog=(
            "examples:\n"
            "  fiatlight_studio          full palette (image / math / text)\n"
            "  fiatlight_studio --min    fast, opencv-free palette (math + text)\n"
            "  fiatlight_studio --ai     full palette + the AI image-gen node\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--min",
        dest="minimal",
        action="store_true",
        help="fast, opencv-free palette (math + text)",
    )
    group.add_argument(
        "--ai",
        action="store_true",
        help="full palette + the AI image-gen node (needs a GPU/mps + a one-time model download)",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    run_studio(minimal=args.minimal, ai=args.ai)


if __name__ == "__main__":
    main()
