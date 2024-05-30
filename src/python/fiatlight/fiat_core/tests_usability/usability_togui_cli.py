from fiatlight.fiat_togui.to_gui import _GUI_FACTORIES


def show_types(query: str | None = None) -> None:
    info = _GUI_FACTORIES.info_factories(query)
    print(info)


if __name__ == "__main__":
    show_types()
