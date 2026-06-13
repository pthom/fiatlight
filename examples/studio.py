"""Launch the Fiatlight studio — run/debug this directly from your IDE.

Right-click -> Run/Debug for the full palette (image / math / text). For fast
iteration without the opencv import, add `--min` to the run configuration's
parameters (math + text only).

Delegates to `python -m fiatlight` so the launch logic lives in one place.
"""
from fiatlight.__main__ import main

if __name__ == "__main__":
    main()
