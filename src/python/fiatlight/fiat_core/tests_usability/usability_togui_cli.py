from fiatlight.fiat_togui.to_gui import _GUI_FACTORIES


def show_types(query: str | None = None) -> None:
    info = _GUI_FACTORIES.info_factories(query)
    print(info)


def main() -> None:
    # show_types("Plot")
    show_types(None)


if __name__ == "__main__":
    main()
