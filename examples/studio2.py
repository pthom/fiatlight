"""Launch the Fiatlight studio — run/debug this directly from your IDE.

Right-click -> Run/Debug for the full palette (image / math / text). Add a flag
to the run configuration's parameters:
  --min   fast, opencv-free palette (math + text only)
  --ai    full palette + the AI image-gen node (needs a GPU/mps + model download)

Delegates to `python -m fiatlight` so the launch logic lives in one place.
"""
import fiatlight as fl
# from fiatlight.__main__ import main


@fl.with_fiat_attributes(fiat_tags=["math"])
def make_int() -> int:
    return 21


@fl.with_fiat_attributes(fiat_tags=["math"])
def double(x: int) -> int:
    return x * 2


@fl.with_fiat_attributes(fiat_tags=["math"])
def add_ten(x: int) -> int:
    return x + 10


@fl.with_fiat_attributes(fiat_tags=["text"])
def make_str() -> str:
    return "hello"


if __name__ == "__main__":
    fl.studio(
        functions=[make_int, double, add_ten, make_str],
        app_name="fiatlight studio (from examples/studio.py)",
    )
