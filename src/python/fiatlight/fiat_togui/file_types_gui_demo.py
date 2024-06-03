"""Demonstrates how to use image_from_file and ImageToFileGui functions in a pipeline.
"""
import fiatlight
from fiatlight.fiat_togui import text_from_file
from fiatlight.fiat_togui.file_types_gui import TextToFileGui


def to_lower(text: str) -> str:
    return text.lower()


def main() -> None:
    fiatlight.run([text_from_file, to_lower, TextToFileGui()])


if __name__ == "__main__":
    main()
