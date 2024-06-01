#! /usr/bin/env python

# Note: may study prompt_toolkit instead of fire

import fire  # type: ignore
from fiatlight.fiat_togui.to_gui import _GUI_FACTORIES


def types(query: str | None = None) -> None:
    """List registered types, with a possible query to filter them. Add an optional query to filter the types."""
    info = _GUI_FACTORIES.info_factories(query)
    print(info)


def gui_info(gui_typename: str) -> None:
    """Print the GUI info for a given type. Add the GUI type name as an argument (if not provided, all Gui widgets names are printed)"""
    info = _GUI_FACTORIES.get_gui_info(gui_typename)
    print(info)


def run_gui_demo(gui_typename: str) -> None:
    """Tries to run a GUI demo for a given type. Add the GUI type name as an argument."""
    _GUI_FACTORIES.run_gui_demo(gui_typename)


def main() -> None:
    fire.Fire(
        {
            "types": types,
            "gui_info": gui_info,
            "gui_demo": run_gui_demo,
        }
    )


if __name__ == "__main__":
    main()
