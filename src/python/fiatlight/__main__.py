"""`python -m fiatlight` — launch the Fiatlight studio (interactive node composer).

    python -m fiatlight          # full palette (image / math / text)
    python -m fiatlight --min    # fast, opencv-free palette (math + text)
    python -m fiatlight --ai     # full palette + the AI image-gen node
                                 # (needs a GPU/mps + a one-time model download)

Launch logic lives in `fiat_cli/studio_cli.py`, shared with the
`fiatlight_studio` console script and the `fiatlight studio` subcommand.
"""
from fiatlight.fiat_cli.studio_cli import main

if __name__ == "__main__":
    main()
