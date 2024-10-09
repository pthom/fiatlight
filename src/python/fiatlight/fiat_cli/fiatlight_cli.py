#! /usr/bin/env python

# Note: may study prompt_toolkit instead of fire

# if fire not installed, inform user to install it
try:
    import fire  # type: ignore
except ImportError:
    raise ModuleNotFoundError(
        """
    The 'fire' module is required for fiatlight command line interface.
    Please install it with:

        pip install fire

    """
    )
from fiatlight.fiat_togui.gui_registry import _GUI_FACTORIES


def types(query: str | None = None) -> None:
    """List registered types, with a possible query to filter them. Add an optional query to filter the types."""
    info = _GUI_FACTORIES.info_factories(query)
    print(info)


def gui_info(gui_or_data_typename: str) -> None:
    """Print the info and fiat attributes available for a given type. Add the datatype or Gui type name as an argument (if not provided, all Gui widgets names are printed)"""
    info = _GUI_FACTORIES.get_gui_info(gui_or_data_typename)
    print(info)


def fn_attrs() -> None:
    """Display the available fiat attributes for a function"""
    from fiatlight.fiat_core.function_with_gui import _FUNCTION_POSSIBLE_FIAT_ATTRIBUTES

    print(_FUNCTION_POSSIBLE_FIAT_ATTRIBUTES.documentation())


# def run_gui_demo(gui_or_data_typename: str) -> None:
#     """Tries to run a GUI demo for a given type. Add the GUI type name as an argument."""
#     _GUI_FACTORIES.run_gui_demo(gui_or_data_typename)


def main() -> None:
    fire.Fire(
        {
            "types": types,
            "gui": gui_info,
            "fn_attrs": fn_attrs,
        }
    )


if __name__ == "__main__":
    main()
