import fiatlight
from fiatlight.fiat_togui import text_from_file
from fiatlight.fiat_togui.file_types_gui import TextToFileGui


def to_lower(text: str) -> str:
    return text.lower()


def main() -> None:
    fiatlight.fiat_run_composition([text_from_file, to_lower, TextToFileGui()])


if __name__ == "__main__":
    main()
