from .fiat_config_def import FiatRunConfig, FiatConfig
from typing import Iterable
import os
import logging


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


def load_user_default_fiat_run_config() -> FiatRunConfig | None:
    for dir in _all_cwd_parents():
        filename = f"{dir}/.fiat_run_config.json"
        if os.path.exists(filename):
            run_config = load_fiat_run_config(filename)
            logging.warning(
                f"""
            Loaded user default fiat run config from {filename}:
            {run_config}
            """
            )
            return run_config
    return None


_FIAT_CONFIG = FiatConfig()
_FIAT_CONFIG_LAST_FRAME_IDX = 0


def get_fiat_config() -> FiatConfig:
    static = get_fiat_config
    if not hasattr(static, "WAS_LOAD_USER_DEFAULT_FIAT_RUN_CONFIG_CALLED"):
        static.WAS_LOAD_USER_DEFAULT_FIAT_RUN_CONFIG_CALLED = False  # type: ignore

    # This will load the user default settings for the fiat run config
    # from a file named .fiat_run_config.json in the current directory or one of its parents.
    if not static.WAS_LOAD_USER_DEFAULT_FIAT_RUN_CONFIG_CALLED:  # type: ignore
        run_config = load_user_default_fiat_run_config()
        if run_config is not None:
            _FIAT_CONFIG.run_config = run_config
        static.WAS_LOAD_USER_DEFAULT_FIAT_RUN_CONFIG_CALLED = True  # type: ignore

    # Heartbeat per frame (update style / dark or light, etc)
    global _FIAT_CONFIG_LAST_FRAME_IDX
    from imgui_bundle import imgui

    from imgui_bundle import hello_imgui

    if hello_imgui.is_using_hello_imgui():
        current_frame_idx = imgui.get_frame_count()
        if current_frame_idx != _FIAT_CONFIG_LAST_FRAME_IDX:
            _FIAT_CONFIG._heartbeat()

    return _FIAT_CONFIG
