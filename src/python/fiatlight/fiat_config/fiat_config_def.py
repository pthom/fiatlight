from fiatlight.fiat_config.fiat_style_def import FiatStyle, AnyGuiWithDataSettings
from pydantic import BaseModel, Field
from typing import Any


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


class FiatConfig(BaseModel):
    style: FiatStyle = Field(default_factory=FiatStyle)
    run_config: FiatRunConfig = Field(default_factory=FiatRunConfig)

    def any_gui_with_data_settings(self) -> AnyGuiWithDataSettings:
        return self.style.any_gui_with_data_settings

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self.style = FiatStyle()

    def _heartbeat(self) -> None:
        self.style._heartbeat()
