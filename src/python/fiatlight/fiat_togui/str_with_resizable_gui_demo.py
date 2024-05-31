import fiatlight
from fiatlight.fiat_togui.str_with_resizable_gui import StrWithGui  # noqa


def main() -> None:
    def f(s: str) -> str:
        return s

    f_gui = fiatlight.FunctionWithGui(f)
    f_gui.set_input_gui("s", StrWithGui())

    fiatlight.fiat_run(f_gui)


if __name__ == "__main__":
    main()
