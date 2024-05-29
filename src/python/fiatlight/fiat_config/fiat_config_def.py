import logging
import os

from fiatlight.fiat_config.fiat_style_def import FiatStyle
from pydantic import BaseModel, Field
from typing import Any, Iterable


class FiatRunConfig(BaseModel):
    """Run configuration for fiatlight.
    This configuration is used to control the behavior of the fiatlight engine during execution.

    Note: if you place a file named ".fiat_run_config.json" in the current working directory,
    or in any of its parent directories, the configuration will be loaded from this file.

    Here is an example of a .fiat_run_config.json file:

        {
            "catch_function_exceptions": true,
            "disable_input_during_execution": false
            "disable_type_eval": false
        }

    Members:
        disable_type_eval: bool, default=False
            Important! As part of this advanced introspection, fiatlight
            may need to evaluate the types of the variables in the code

        catch_function_exceptions: bool, default=True
            If true, exceptions raised by FunctionWithGui nodes will be caught and shown in the function.
            You can disable this by setting this to False.

        disable_input_during_execution:
            If true, the input will be disabled during execution, especially the execution of async functions.
    """

    disable_type_eval: bool = False
    catch_function_exceptions: bool = True
    disable_input_during_execution: bool = False


class FiatConfig(BaseModel):
    style: FiatStyle = Field(default_factory=FiatStyle)
    run_config: FiatRunConfig = Field(default_factory=FiatRunConfig)

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        self.style = FiatStyle()


_FIAT_CONFIG = FiatConfig()


def get_fiat_config() -> FiatConfig:
    return _FIAT_CONFIG


def save_fiat_run_config(run_config: FiatRunConfig, filename: str) -> None:
    as_json_str = run_config.json()
    with open(filename, "w") as f:
        f.write(as_json_str)


def load_fiat_run_config(filename: str) -> FiatRunConfig:
    with open(filename) as f:
        content = f.read()
    run_config = FiatRunConfig.model_validate(content)
    return run_config


def _all_cwd_parents() -> Iterable[str]:
    """Yield all the parent directories of the current working directory.
    current working directory is yielded first, then its parent, and so on.
    """
    cwd = os.getcwd()
    while True:
        yield cwd
        new_cwd = os.path.dirname(cwd)
        if new_cwd == cwd:
            break
        cwd = new_cwd


def load_user_default_fiat_run_config() -> None:
    for dir in _all_cwd_parents():
        filename = f"{dir}/.fiat_run_config.json"
        if os.path.exists(filename):
            run_config = load_fiat_run_config(filename)
            _FIAT_CONFIG.run_config = run_config
            logging.warning(
                f"""
            Loaded user default fiat run config from {filename}:
            {run_config}
            """
            )
            return
