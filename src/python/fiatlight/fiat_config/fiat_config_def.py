from fiatlight.fiat_config.fiat_style_def import FiatStyle
from pydantic import BaseModel, Field
from typing import Any


class AnyGuiWithDataSettings(BaseModel):
    # show_collapse_button:
    # If true, display a button that enables the user to collapse a widget
    show_collapse_button: bool = True

    # show_popup_button:
    # If true, display a button that enables the user to open a popup
    # for presentation or edition of a collapsible widgets
    show_popup_button: bool = True

    # show_clipboard_button:
    # If true, display a button that enables the user to copy the content of a widget to the clipboard
    show_clipboard_button: bool = True

    @staticmethod
    def default_in_function_graph() -> "AnyGuiWithDataSettings":
        return AnyGuiWithDataSettings(
            show_collapse_button=True,
            show_popup_button=True,
            show_clipboard_button=True,
        )

    @staticmethod
    def default_in_standalone_app() -> "AnyGuiWithDataSettings":
        return AnyGuiWithDataSettings(
            show_collapse_button=True,
            show_popup_button=False,
            show_clipboard_button=False,
        )


class FiatRunConfig(BaseModel):
    """Run configuration for fiatlight.
    This configuration is used to control the behavior of the fiatlight engine during execution.

    Note: if you place a file named ".fiat_run_config.json" in the current working directory,
    or in any of its parent directories, the configuration will be loaded from this file.

    Here is an example of a .fiat_run_config.json file:

        {
            "catch_function_exceptions": true,
            "disable_input_during_execution": false
        }
    """

    # catch_function_exceptions: bool, default=True
    # If true, exceptions raised by FunctionWithGui nodes will be caught and shown in the function.
    # You can disable this by setting this to False.
    catch_function_exceptions: bool = True

    # disable_input_during_execution: bool, default=False
    # If true, the input will be disabled during execution, especially the execution of async functions.
    disable_input_during_execution: bool = False

    any_gui_with_data_settings_function_graph: AnyGuiWithDataSettings = (
        AnyGuiWithDataSettings.default_in_function_graph()
    )
    any_gui_with_data_settings_standalone_app: AnyGuiWithDataSettings = (
        AnyGuiWithDataSettings.default_in_standalone_app()
    )


class FiatConfig(BaseModel):
    style: FiatStyle = Field(default_factory=FiatStyle)
    run_config: FiatRunConfig = Field(default_factory=FiatRunConfig)

    def any_gui_with_data_settings(self) -> AnyGuiWithDataSettings:
        from fiatlight.fiat_runner.fiat_gui import is_running_in_function_graph

        if is_running_in_function_graph():
            return self.run_config.any_gui_with_data_settings_function_graph
        else:
            return self.run_config.any_gui_with_data_settings_standalone_app

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self.style = FiatStyle()
