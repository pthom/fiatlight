import fiatlight
from fiatlight.fiat_togui.str_with_resizable_gui import StrWithResizableGui  # noqa


def main() -> None:
    def f(s: str) -> None:
        pass

    f_gui = fiatlight.FunctionWithGui(f)
    f_gui.set_input_gui("s", StrWithResizableGui())

    fiatlight.fiat_run(f_gui)


if __name__ == "__main__":
    main()
