#! /usr/bin/env python

# Note: may study prompt_toolkit instead of fire

import fire  # type: ignore
from fiatlight.fiat_togui.to_gui import _GUI_FACTORIES


def types(query: str | None = None) -> None:
    """List registered types, with a possible query to filter them"""
    info = _GUI_FACTORIES.info_factories(query)
    print(info)


def gui_info(gui_typename: str) -> None:
    """Print the GUI info for a given type"""
    info = _GUI_FACTORIES.get_gui_info(gui_typename)
    print(info)


def main() -> None:
    fire.Fire(
        {
            "types": types,
            "gui_info": gui_info,
        }
    )


if __name__ == "__main__":
    main()
