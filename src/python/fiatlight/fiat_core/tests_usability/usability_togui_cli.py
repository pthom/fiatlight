from fiatlight.fiat_togui.gui_registry import _GUI_FACTORIES


def show_types(query: str | None = None) -> None:
    """Manual usability test: can we list registered types?"""
    info = _GUI_FACTORIES.info_factories(query)
    print(info)


if __name__ == "__main__":
    show_types()
