"""Launch the Fiatlight studio — run/debug this directly from your IDE.

Right-click -> Run/Debug for the full palette (image / math / text). Add a flag
to the run configuration's parameters:
  --min   fast, opencv-free palette (math + text only)
  --ai    full palette + the AI image-gen node (needs a GPU/mps + model download)

Delegates to `python -m fiatlight` so the launch logic lives in one place.
"""
from fiatlight.__main__ import main

if __name__ == "__main__":
    main()
